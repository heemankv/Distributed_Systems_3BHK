import grpc
import kmeans_pb2
import kmeans_pb2_grpc
from concurrent import futures
from random import sample
import  os
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import time

#  TODO: We need to reset latest mappers to original mappers after a successful iteration -> done by @heemankv

class Master:
    def __init__(self, n_mappers, n_reducers, data_file, k, max_iters):
        self.n_mappers = n_mappers
        self.n_reducers = n_reducers        
        self.mapper_ids = [i+1 for i in range(n_mappers)]
        self.latest_mapper_ids = [i+1 for i in range(n_mappers)]
        self.reducer_ids = [i+1 for i in range(n_reducers)]

        self.data_file = data_file
        self.k = k
        self.max_iters = max_iters
        self.centroids = self.initialize_centroids()
        self.mapper_stubs = self.create_mapper_stubs()
        self.reducer_stubs = self.create_reducer_stubs() 
        self.remap_mappers_request = {}  
        self.prev_dist = None     
    
    def initialize_centroids(self):        
        centroids = []
        for i in range(self.k):
            centroids.append(self.get_random_data_point())            
        return centroids

    def get_random_data_point(self): 
        #TODO: centroids should not be same
        return (sample(range(10), 1)[0], sample(range(10), 1)[0])

    def read_data_points(self):
        with open(self.data_file, 'r') as f:
            return [tuple(map(float, line.strip().split(','))) for line in f]
    
    def create_mapper_stubs(self):
        mapper_stubs = {}
        

        for id in self.latest_mapper_ids:
            channel = grpc.insecure_channel(mapper_id_to_address[id])
            stub = kmeans_pb2_grpc.MapperServiceStub(channel)
            mapper_stubs[id] = stub
        return mapper_stubs

    def split_data_for_mappers(self):
        # TODO: Could be randomized, let's see
        data_points = self.read_data_points()
        split_size = len(data_points) // len(self.latest_mapper_ids)        
        split_indices = {mapper_id :  (i * split_size, (i + 1) * split_size) for i, mapper_id in enumerate(self.latest_mapper_ids)}
        return split_indices


    
    # Retry decorator function
    def retry(func):
        def wrapper(*args, **kwargs):
            max_retries = 1
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Error: {e}")
                    retries += 1
                    if retries < max_retries:
                        print("Retrying...")
                        time.sleep(1)  # Wait for 1 second before retrying
                    else:
                        print("Max retries reached. Giving up on this Mapper, going to other.")
                        # assign the task to another mapper
                        return kmeans_pb2.MapResponse(success=False, message=str(e))
                        # raise  # Re-raise the exception if max retries reached
        return wrapper

    # Modified call_rpc function with retry decorator
    @retry 
    def call_rpc(self, id, centroids_flat, split, mapper_stubs):
        future = mapper_stubs[id].RunMap.future(
            kmeans_pb2.MapRequest(
                mapper_id=id,
                centroids=centroids_flat,
                index_start=split[0],
                index_end=split[1]
            )
        )
        response = future.result()
        if response.success:
            print(f"Received SUCCESS from Mapper: {id}")
            return response
        else:
            self.remap_mappers_request[id] = True
            raise Exception("RPC call failed")

    def call_rpc_wrapper(self,args):
        id, centroids_flat, split, mapper_stubs = args
        print(f"Sending RPC to Mapper: {id}, Centroids: {centroids_flat}, Split: {split}, Mapper Stubs: {mapper_stubs}")
        return self.call_rpc(id, centroids_flat, split, mapper_stubs)
    
    def run_map_phase(self, data_splits):
        map_responses = []

        with ThreadPoolExecutor() as executor:
            map_responses = list(executor.map(
                self.call_rpc_wrapper,
                [(id, [c for centroid in self.centroids for c in centroid], data_splits[id], self.mapper_stubs)
                for id in self.mapper_stubs]
            ))

        return map_responses

    def create_reducer_stubs(self):
        reducer_stubs = {}
        for id in self.reducer_ids:
            channel = grpc.insecure_channel(reducer_id_to_address[id])
            stub = kmeans_pb2_grpc.ReducerServiceStub(channel)
            reducer_stubs[id] = stub
        return reducer_stubs

    def run_reduce_phase(self): 
        reduce_responses = []
        for id, stub in self.reducer_stubs.items():
            print(f"Sending RPC to Reducer: {id}")
            reduce_request = kmeans_pb2.ReducerRequest(
                reducer_id=id,
                mapper_addresses=[mapper_id_to_address[mapper_id] for mapper_id in self.latest_mapper_ids]
            )
            response = stub.RunReducer(reduce_request)
            status = "SUCCESS" if response.success else "FAILURE"
            print(f"Received {status} from Reducer: {id}")
            reduce_responses.append(response)
        return reduce_responses
    
    def remap_mappers(self):
        new_mapper_ids = []
        # deepcopy the mapper ids
        for mapper_id in self.mapper_ids:
            new_mapper_ids.append(mapper_id)
        
        # remove the mapper ids from the new_mapper_ids list if they are in the remap_mappers_request
        for mapper_id in self.remap_mappers_request.keys():
            new_mapper_ids.remove(mapper_id)

        print(f"Old mappers: {self.mapper_ids}")
        print(f"Remapped mappers: {new_mapper_ids}")
        self.latest_mapper_ids = new_mapper_ids
        self.mapper_stubs = self.create_mapper_stubs()


    def execute(self):       
        # TODO: Stop when the centroids converge 
        for iter in range(self.max_iters):
            with open('Data/centroids.txt', 'w') as f:
                f.write(str(self.centroids))
            print(f'Iteration {iter + 1}, Centroids: {self.centroids}')
            data_splits = self.split_data_for_mappers()  
            print(f"Data splits: {data_splits}")          
            map_responses = self.run_map_phase(data_splits)
                        
            remapping_flag = False
            for response in map_responses: 
                if not response.success:
                    remapping_flag = True
                    print(f'Error: {response.message} in Map phase')

            if(remapping_flag):
                print("Remapping mappers")
                # decrease the iteration count, as to not count this iteration
                iter -= 1
                # remap the mappers
                self.remap_mappers()
                if len(self.latest_mapper_ids) == 0:
                    print("All mappers failed. Exiting.")
                    return
                # continue to next iteration
                continue
        
            print('Map phase completed successfully')
            time.sleep(1)

            reduce_responses = self.run_reduce_phase()
            for response in reduce_responses:
                if not response.success:
                    print(f'Error: {response.message} in Reduce Phase')
                    return

            print('Reduce phase complete successfully')
            new_centroids = {}
            for response in reduce_responses:
                new_centroids[response.reducer_id] = response.new_centroids
            
            self.parse_new_centroids(new_centroids)    

            # assign the deepcopy of original mappers to latest mappers
            mapper_ids = []
            for mapper_id in self.mapper_ids:
                mapper_ids.append(mapper_id)
            self.latest_mapper_ids = mapper_ids

            print(f"Reassigning mappers: {self.latest_mapper_ids}")        

    def calculate_distance_from_centroids(self):
        dist = 0
        data_points = self.read_data_points()
        for data_point in data_points:
            min_dist = float('inf')
            for centroid in self.centroids:
                d = self.calculate_euclidean_distance(data_point, centroid)
                min_dist = min(min_dist, d)
            dist += min_dist
        return dist

    def calculate_euclidean_distance(self, p1, p2):
        return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5                                
    
    def parse_new_centroids(self, new_centroids):        
        for centroid in new_centroids.values():
            for key, value in centroid.items():
                print(f"Centroid {key}: {value}")
                self.centroids[key] = value.values                                        


if __name__ == '__main__':
    mapper_id_to_address = {1: 'localhost:50051', 2: 'localhost:50052', 3: 'localhost:50053'}
    reducer_id_to_address = {1: 'localhost:50061', 2: 'localhost:50062', 3: 'localhost:50063'}

    load_dotenv()
    n_mappers = int(os.getenv("n_mappers"))
    n_reducers = int(os.getenv("n_reducers"))

    # master = Master(mapper_ids=[1,2], reducer_ids = [1,2], data_file='Data/Input/points.txt', k=3, max_iters=1)
    master = Master(n_mappers = n_mappers, n_reducers = n_reducers, data_file='Data/Input/points.txt', k=5, max_iters=10)

    master.execute()
            
