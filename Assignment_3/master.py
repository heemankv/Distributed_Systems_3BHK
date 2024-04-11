import grpc
import kmeans_pb2
import kmeans_pb2_grpc
from concurrent import futures
from random import sample

class Master:
    def __init__(self, mapper_ids, data_file, k, max_iters):
        self.mapper_ids = mapper_ids
        self.data_file = data_file
        self.k = k
        self.max_iters = max_iters
        self.centroids = self.initialize_centroids()
        self.mapper_stubs = self.create_mapper_stubs()
    
    def initialize_centroids(self):
        # initialize k random centroids
        centroids = []
        for i in range(self.k):
            centroids.append(self.get_random_data_point())    
        print("Initial centroids: ", centroids)    
        return centroids

    def get_random_data_point(self):        
        return (sample(range(10), 1)[0], sample(range(10), 1)[0])

    def read_data_points(self):
        with open(self.data_file, 'r') as f:
            return [tuple(map(float, line.strip().split(','))) for line in f]
    
    def create_mapper_stubs(self):
        mapper_stubs = {}
        for id in self.mapper_ids:
            channel = grpc.insecure_channel(mapper_id_to_address[id])
            stub = kmeans_pb2_grpc.MapperServiceStub(channel)
            mapper_stubs[id] = stub
        return mapper_stubs

    def split_data_for_mappers(self):
        data_points = self.read_data_points()
        split_size = len(data_points) // len(self.mapper_ids)
        # Don't split the data, just give me split indices like 1:3, 3:5, 5:7
        split_indices = [(i * split_size, (i + 1) * split_size) for i in range(len(self.mapper_ids))]
        return split_indices
         

    def run_map_phase(self, data_splits):
        map_responses = []
        for id, stub in self.mapper_stubs.items():            
            centroids_flat = [c for centroid in self.centroids for c in centroid]                            
            split = data_splits[id-1]                                        
            map_request = kmeans_pb2.MapRequest(
                mapper_id=id,
                centroids=centroids_flat,
                index_start = split[0],
                index_end = split[1]
            )
            response = stub.RunMap(map_request)
            map_responses.append(response)
        return map_responses

    def execute(self):
        for iter in range(self.max_iters):
            print(f'Iteration {iter + 1}')
            data_splits = self.split_data_for_mappers()            
            map_responses = self.run_map_phase(data_splits)
            for response in map_responses:
                if not response.success:
                    print(f'Error: {response.message}')
                    return
            else:
                print('Map phase completed successfully')

if __name__ == '__main__':
    mapper_id_to_address = {1: 'localhost:50051', 2: 'localhost:50052'}
    master = Master(mapper_ids=[1,2], data_file='Data/Input/points.txt', k=3, max_iters=1)
    master.execute()
            
