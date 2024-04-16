import grpc
import kmeans_pb2
import kmeans_pb2_grpc
from concurrent import futures
from random import sample
import  time, os
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

# TODO: We need to reset latest mappers to original mappers after a successful iteration -> done by @heemankv
# TODO: remap_mappers_request always remains filled, might need to reset it after remapping
# TODO: Add dump statements for fault tolerance

# Dump File Code:
'''
Print/Display the following data while executing the master program for each iteration:

    Iteration number
    Execution of gRPC calls to Mappers or Reducers
    gRPC responses for each Mapper and Reducer function (SUCCESS/FAILURE)
    Centroids generated after each iteration (including the randomly initialized centroids)
'''

class Master:
    def __init__(self, n_mappers, n_reducers, data_file, k, max_iters):
        self.n_mappers = n_mappers
        self.n_reducers = n_reducers        
        self.mapper_ids = [i+1 for i in range(n_mappers)]
        self.reducer_ids = [i+1 for i in range(n_reducers)]

        self.data_file = data_file
        self.k = k
        self.max_iters = max_iters
        self.centroids = self.initialize_centroids()

        self.dump(f"Centroids added to Disk: {self.centroids}")
        with open('Data/centroids.txt', 'w') as f:
                f.write(str(self.centroids))  
         
        # Fault Tolerance
        self.latest_mapper_ids = [i+1 for i in range(n_mappers)]
        self.remap_mappers_request = {}  
        self.permanent_remap_mappers_request = {}
        self.latest_reducer_ids = [i+1 for i in range(n_reducers)]
        self.remap_reducers_request = {}
        self.permanent_remap_reducers_request = {}

        self.mapper_stubs = self.create_mapper_stubs()
        self.reducer_stubs = self.create_reducer_stubs()

        file_path = 'master_dump.txt'
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                pass

        self.dump("Master is started")  

    def dump(self,entry):
        file_path = 'master_dump.txt'
        with open(file_path, 'a') as f:
            f.write(f"{entry}\n")
    
    # def initialize_centroids(self):        
    #     centroids = []
    #     count=0
    #     # TODO: Test in actual code, working in rough.py
    #     while(count!=self.k):
    #         points=self.get_random_data_point()
    #         if(points not in centroids):
    #             centroids.append(self.get_random_data_point())     
    #             count+=1  
    #     return centroids
    def initialize_centroids(self):   
        data_points = self.read_data_points()        
        random_indices = sample(range(len(data_points)), self.k)
        centroids = []
        for i in random_indices:
            centroids.append(data_points[i])                    
        return centroids

    def get_random_data_point(self): 
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
        print(f"DATA POINTS: {data_points}")
        split_size = len(data_points) // len(self.latest_mapper_ids)        
        split_indices = {mapper_id :  (i * split_size, (i + 1) * split_size) for i, mapper_id in enumerate(self.latest_mapper_ids)}
        return split_indices

    
    # Retry decorator function
    def retryMappers(func):
        def wrapper(*args, **kwargs):
            max_retries = 1
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
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
    
    # Retry decorator function
    def retryReducers(func):
        def wrapper(*args, **kwargs):
            max_retries = 1
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries < max_retries:
                        print("Retrying...")
                        time.sleep(1)  # Wait for 1 second before retrying
                    else:
                        print("Max retries reached. Giving up on this Reducer, going to other.")
                        # assign the task to another mapper
                        return kmeans_pb2.ReducerResponse(success=False, message=str(e))
                        # raise  # Re-raise the exception if max retries reached
        return wrapper

    # Modified call_rpc function with retry decorator
    @retryMappers
    def call_mappers_rpc(self, id, centroids_flat, split, mapper_stubs):
        future = mapper_stubs[id].RunMap.future(
            kmeans_pb2.MapRequest(
                mapper_id=id,
                centroids=centroids_flat,
                index_start=split[0],
                index_end=split[1]
            )
        )
        #  we need to create a timeout for the RPC call
        #  if the rpc call doesn't return in 5 seconds, we will raise Exception("RPC call failed")
        #  and assign the task to another mapper
        # response = future.result()
        
        # TODO: so when this guy crashed, it raised the error directly 
        # but did not raise the remapping flag hence it was included in the next iteration and again failed
        # so we need a callback fucntion to execute when the future is done
        # if the future is done and the response is not successful, then we raise the remapping flag
        # code below

        try:
            response = future.result(timeout=timeout_error_seconds)
        except Exception as e:
            print(f"Error: {e} and Code :{str(e.code())}")
            if str(e.code()) == 'StatusCode.UNAVAILABLE':
                # process unavailable status
                print(" I am hereeeeee")
                self.permanent_remap_mappers_request[id] = True
                raise Exception("RPC call failed")
            
        if response.success:
            print(f"Received SUCCESS from Mapper: {id}")
            return response
        else:
            self.remap_mappers_request[id] = True
            raise Exception("RPC call failed")
    
    @retryReducers
    def call_reducers_rpc(self, id, reducer_stubs):
        future = reducer_stubs[id].RunReducer.future(
            kmeans_pb2.ReducerRequest(
                reducer_id=id,
                mapper_addresses=[mapper_id_to_address[mapper_id] for mapper_id in self.latest_mapper_ids]
            )
        )
        #  we need to create a timeout for the RPC call
        #  if the rpc call doesn't return in 5 seconds, we will raise Exception("RPC call failed")
        #  and assign the task to another mapper
        # response = future.result()
        
        # TODO: so when this guy crashed, it raised the error directly 
        # but did not raise the remapping flag hence it was included in the next iteration and again failed
        # so we need a callback fucntion to execute when the future is done
        # if the future is done and the response is not successful, then we raise the remapping flag
        # code below

        try:
            response = future.result(timeout=timeout_error_seconds)
        except Exception as e:
            print(f"Error: {e} and Code :{str(e.code())}")
            if str(e.code()) == 'StatusCode.UNAVAILABLE':
                # process unavailable status
                print(" I am hereeeeee")
                self.permanent_remap_reducers_request[id] = True
                raise Exception("RPC call failed")
            
        if response.success:
            print(f"Received SUCCESS from Reducer: {id}")
            return response
        else:
            self.remap_reducers_request[id] = True
            raise Exception("RPC call failed")

    def call_mapper_rpc_wrapper(self,args):
        id, centroids_flat, split, mapper_stubs = args

        self.dump(f"Sending RPC to Mapper: {id}, Centroids: {centroids_flat}, Split: {split}")
        print(f"Sending RPC to Mapper: {id}, Centroids: {centroids_flat}, Split: {split}")
        
        response = self.call_mappers_rpc(id, centroids_flat, split, mapper_stubs)
        
        status = "SUCCESS" if response.success else "FAILURE"

        self.dump(f"Received {status} from Mapper: {id}")

        if(response.success==False):
           errorMessage = response.message if isinstance(response.message, str) else response.details
           self.dump(f'Error: {errorMessage} in Map Phase with Mapper: {id}')            

        return response
    
    def call_reducer_rpc_wrapper(self,args):
        id, reducer_stubs = args

        self.dump(f"Sending RPC to Reducer: {id}")
        print(f"Sending RPC to Reducer: {id}")
        
        response = self.call_reducers_rpc(id, reducer_stubs)
        
        status = "SUCCESS" if response.success else "FAILURE"

        self.dump(f"Received {status} from Reducer: {id}")

        if(response.success==False):
           errorMessage = response.message if isinstance(response.message, str) else response.details
           self.dump(f'Error: {errorMessage} in Reduce Phase with Reducer: {id}')            

        return response
    
    def run_map_phase(self, data_splits):
        map_responses = []

        with ThreadPoolExecutor() as executor:
            map_responses = list(executor.map(
                self.call_mapper_rpc_wrapper,
                [(id, [c for centroid in self.centroids for c in centroid], data_splits[id], self.mapper_stubs)
                for id in self.mapper_stubs]
            ))

        return map_responses

    def run_reduce_phase(self): 
        reduce_responses = []

        with ThreadPoolExecutor() as executor:
            reduce_responses = list(executor.map(
                self.call_reducer_rpc_wrapper,
                [(id, self.reducer_stubs)
                for id in self.reducer_stubs]
            ))

        return reduce_responses
        # self.dump(f"Sending RPC to Reducer: {id}")
        # print(f"Sending RPC to Reducer: {id}")

        # self.dump(f"Received {status} from Reducer: {id}")
        # print(f"Received {status} from Reducer: {id}")

    def create_reducer_stubs(self):
        reducer_stubs = {}
        for id in self.latest_reducer_ids:
            channel = grpc.insecure_channel(reducer_id_to_address[id])
            stub = kmeans_pb2_grpc.ReducerServiceStub(channel)
            reducer_stubs[id] = stub
        return reducer_stubs

    def remap_mappers(self):
        new_mapper_ids = []
        # deepcopy the mapper ids
        for mapper_id in self.mapper_ids:
            new_mapper_ids.append(mapper_id)
        
        # remove the mapper ids from the new_mapper_ids list if they are in the remap_mappers_request
        for mapper_id in self.remap_mappers_request.keys():
            new_mapper_ids.remove(mapper_id)
        
        for mapper_id in self.permanent_remap_mappers_request.keys():
            new_mapper_ids.remove(mapper_id)
        

        print(f"Old mappers: {self.mapper_ids}")
        print(f"Remapped mappers: {new_mapper_ids}")
        self.latest_mapper_ids = new_mapper_ids
        self.mapper_stubs = self.create_mapper_stubs()

    
    def remap_reducers(self):
        new_reducer_ids = []
        # deepcopy the reducer ids
        for reducer_id in self.reducer_ids:
            new_reducer_ids.append(reducer_id)

        # remove the reducer ids from the new_reducer_ids list if they are in the remap_reducers_request
        for reducer_id in self.remap_reducers_request.keys():
            new_reducer_ids.remove(reducer_id)
        
        for reducer_id in self.permanent_remap_reducers_request.keys():
            new_reducer_ids.remove(reducer_id)

        print(f"Old reducers: {self.reducer_ids}")
        print(f"Remapped reducers: {new_reducer_ids}")
        self.latest_reducer_ids = new_reducer_ids
        self.reducer_stubs = self.create_reducer_stubs()


    def execute(self):       
        # TODO: Stop when the centroids converge 
        prev_centroids=None
        iter = 0
        while iter < self.max_iters:
        # for iter in range(self.max_iters):
            if(prev_centroids==None):
                pass
            else:
                print(f"Prev Centroids: {prev_centroids}")
                print(f"Current Centroids: {self.centroids}")
                if(prev_centroids==self.centroids):
                    self.dump('Centroids have converged, stopping the iterations')
                    print(f'Centroids have converged, stopping the iterations')
                    break
            
            self.dump(f'Iteration {iter + 1}, Centroids: {self.centroids}')
            print(f'Iteration {iter + 1}, Centroids: {self.centroids}')

            data_splits = self.split_data_for_mappers() 

            self.dump(f'Splitting Data into Mapper Tasks Data splits: {data_splits}')
            print(f"Data splits: {data_splits}")     

            map_responses = self.run_map_phase(data_splits)
                        
            remapping_flag = False
            for response in map_responses: 
                if not response.success:
                    remapping_flag = True
                    # if response.message is a string then print it, if it is an object then print its response.message.details
                    errorMessage = response.message if isinstance(response.message, str) else response.details
                    print(f'Error: {errorMessage} in Map Phase')

            if(remapping_flag):
                print("Remapping mappers")
                # decrease the iteration count, as to not count this iteration
                
                # remap the mappers
                self.remap_mappers()
                
                if len(self.latest_mapper_ids) == 0:
                    print("All mappers failed. Exiting.")
                    return
                # continue to next iteration
                continue
            
            self.dump('Map phase completed successfully')
            print('Map phase completed successfully')

            time.sleep(1)

            reduce_responses = self.run_reduce_phase()


            # for response in reduce_responses:
            #     if not response.success:
            #         print(f'Error: {response.message} in Reduce Phase')
            #         return

            remapping_flag = False
            for response in reduce_responses:
                if not response.success:
                    remapping_flag = True
                    # if response.message is a string then print it, if it is an object then print its response.message.details
                    errorMessage = response.message if isinstance(response.message, str) else response.details
                    print(f'Error: {errorMessage} in Reduce Phase')

            if(remapping_flag):
                print("Remapping reducers")
                # decrease the iteration count, as to not count this iteration                
                
                # remap the mappers
                self.remap_reducers()
                
                if len(self.latest_reducer_ids) == 0:
                    print("All reducers failed. Exiting.")
                    return
                # continue to next iteration
                continue
            

            self.dump('Reduce phase complete successfully')
            print('Reduce phase complete successfully')

            prev_centroids = []
            for item in self.centroids:
                prev_centroids.append(item)

            new_centroids = {}
            for response in reduce_responses:
                new_centroids[response.reducer_id] = response.new_centroids
            
            self.parse_new_centroids(new_centroids)    

            # assign the deepcopy of original mappers to latest mappers
            mapper_ids = []
            for mapper_id in self.mapper_ids:
                mapper_ids.append(mapper_id)

            for mapper_id in self.permanent_remap_mappers_request.keys():
                mapper_ids.remove(mapper_id)
        
            self.latest_mapper_ids = mapper_ids
            self.mapper_stubs = self.create_mapper_stubs()

            print(f"Reassigning mappers: {self.latest_mapper_ids}") 

            # assign the deepcopy of original reducers to latest reducers
            reducer_ids = []
            for reducer_id in self.reducer_ids:
                reducer_ids.append(reducer_id)

            for reducer_id in self.permanent_remap_reducers_request.keys():
                reducer_ids.remove(reducer_id)

            self.latest_reducer_ids = reducer_ids
            self.reducer_stubs = self.create_reducer_stubs()

            print(f"Reassigning reducers: {self.latest_reducer_ids}")
            iter+=1


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
                
                self.dump(f"Centroid {key}: {value}")
                print(f"Centroid {key}: {value}")

                self.centroids[key] = value.values 
        
        self.dump(f"New Centroids added to Disk: {self.centroids}")
        with open('Data/centroids.txt', 'w') as f:
                f.write(str(self.centroids))                                       


if __name__ == '__main__':
    mapper_id_to_address = {1: 'localhost:50051', 2: 'localhost:50052', 3: 'localhost:50053'}
    reducer_id_to_address = {1: 'localhost:50061', 2: 'localhost:50062', 3: 'localhost:50063'}

    load_dotenv()
    n_mappers = int(os.getenv("n_mappers"))
    n_reducers = int(os.getenv("n_reducers"))
    k_clusters = int(os.getenv("k_clusters"))
    max_iters = int(os.getenv("max_iters"))
    timeout_error_seconds = int(os.getenv("timeout_error_seconds"))

    # master = Master(mapper_ids=[1,2], reducer_ids = [1,2], data_file='Data/Input/points.txt', k=3, max_iters=1)
    master = Master(n_mappers = n_mappers, n_reducers = n_reducers, data_file='Data/Input/points.txt', k=k_clusters, max_iters=max_iters)

    master.execute()
            
