import random
import grpc
import kmeans_pb2
import kmeans_pb2_grpc
from concurrent import futures
import sys
import os
from dotenv import load_dotenv

probabilistic = 0.3


class Mapper(kmeans_pb2_grpc.MapperServiceServicer):
    def __init__(self, mapper_id):
        self.mapper_id = mapper_id
        self.create_directory()
        print(f"Mapper {self.mapper_id} started.")
    
    def create_directory(self):
        path = f'Data/Mappers/M{self.mapper_id}/'
        if not os.path.exists(path):
            os.makedirs(path)

    def RunMap(self, request, context):

        try:
            # based on the variable probabilistic, the following code will sometimes execute and sometimes an error will be raised
            # get random number between 0 and 1
            random_number = random.random()
            print("Random Number: ", random_number)
            if random_number < probabilistic:
                print("Random Error: ", random_number)
                raise Exception("Random Error")

            self.centroids = self._parse_centroids(request.centroids)
            index_start = request.index_start
            index_end = request.index_end
            points = self.read_data_points(index_start, index_end)
            # print("Centroids: ", self.centroids)            
            
            assignments = []
            for data_point in points:
                closest_centroid_idx = self.find_closest_centroid(data_point, self.centroids)
                # This is actually the closest centroid index and not the centroid itself
                assignments.append((closest_centroid_idx, data_point))
            
            print(f"Mapper {self.mapper_id} working on data points from {index_start} to {index_end} resulting to {assignments} assignments.")
            print(f"Mapper {self.mapper_id} completed mapping.")
            partitions = self.create_partitions(assignments, no_of_reducers=int(os.getenv('n_reducers')))
            self.create_partition_files(partitions, self.mapper_id)   
                                    
            return kmeans_pb2.MapResponse(success=True, message='Mapping completed successfully.')
        except Exception as e:
            return kmeans_pb2.MapResponse(success=False, message=str(e))
    
    def create_partitions(self, assignments, no_of_reducers):
        '''
        In this step, you will write a function that takes the list of key-value pairs generated by the Map function and partitions them into smaller partitions.
        The partitioning function should ensure that all key-value pairs with the same key are sent to the same partition.
        Each partition is picked up by a specific reducer during shuffling and sorting.
        If there are M mappers and R reducers, each mapper should have R file partitions.
        '''
        # number of partitions = number of reducers
        partitions = {}
        for i in range(no_of_reducers):
            partitions[i] = []
        for assignment in assignments:
            # assignment[0] is the closest centroid index, which will be used to partition the data
            # formula : assignment[0] % no_of_reducers
            # explanation: if there are 3 reducers, then the closest centroid index will be divided by 3 and the remainder will be used to assign the partition
            partition_idx = assignment[0] % no_of_reducers
            partitions[partition_idx].append(assignment)
        return partitions

    def create_partition_files(self, partitions, mapper_id):            
        for partition_idx, partition in partitions.items():
            with open(f'Data/Mappers/M{mapper_id}/partition_{partition_idx}.txt', 'w') as f:
                for assignment in partition:                    
                    f.write(f"{str(assignment)}\n")

    def find_closest_centroid(self, data_point, centroids):
        min_distance = float('inf')
        closest_centroid = None
        closest_centroid_idx = None
        for centroid_idx in range(len(centroids)):
            centroid = centroids[centroid_idx]
            distance = self.euclidean_distance(data_point, centroid)
            if distance < min_distance:
                min_distance = distance
                closest_centroid = centroid
                closest_centroid_idx = centroid_idx
        return closest_centroid_idx
    
    def euclidean_distance(self, p1, p2):
        return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5
    
    def read_data_points(self, index_start, index_end):        
        with open('Data/Input/points.txt', 'r') as f:
            data_points = [tuple(map(float, line.strip().split(','))) for line in f][index_start:index_end]   
        return data_points

    def _parse_centroids(self, centroids_flat_list):        
        it = iter(centroids_flat_list)
        return [(x, next(it)) for x in it]

    def GetIntermediateData(self, request, context):
        print("Recieving Intermediate Request RPC from Reducer: ", request.reducer_id)   
            
        with open(f'Data/Mappers/M{self.mapper_id}/partition_{request.reducer_id-1}.txt', 'r') as f:            
            intermediate_data = f.readlines()        
        return kmeans_pb2.IntermediateDataResponse(success=True, pairs=intermediate_data)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    mapper_address = mapper_id_to_address[int(sys.argv[1])]        
    kmeans_pb2_grpc.add_MapperServiceServicer_to_server(Mapper(mapper_id=sys.argv[1]), server)
    server.add_insecure_port(mapper_address)
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    mapper_id_to_address = {1: 'localhost:50051', 2: 'localhost:50052', 3: 'localhost:50053'}
    load_dotenv()
    serve()