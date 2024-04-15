import grpc
import kmeans_pb2
import kmeans_pb2_grpc
from concurrent import futures
import sys
import os
import time

class Reducer(kmeans_pb2_grpc.ReducerServiceServicer):
    def __init__(self, reducer_id):
        self.reducer_id = reducer_id
        self.create_directory()
        print(f"Reducer {self.reducer_id} started.")

    def create_directory(self):
        path = f'Data/Reducers'
        if not os.path.exists(path):
            os.makedirs(path)
    
    def get_mapper_stubs(self, mapper_addresses):
        mapper_stubs = {}
        for id, address in enumerate(mapper_addresses):
            channel = grpc.insecure_channel(address)
            stub = kmeans_pb2_grpc.MapperServiceStub(channel)
            mapper_stubs[id+1] = stub        
        return mapper_stubs
    
    def RunReducer(self, request, context):
        print(f"Reducer {request.mapper_addresses} received request.")
        try:         
            mapper_stubs = self.get_mapper_stubs(request.mapper_addresses)
            intermediate_data = {}
            for id, stub in mapper_stubs.items(): 
                print(f"Sending Intermediate Request RPC to Mapper: {id}")
                intermediate_data_request = kmeans_pb2.IntermediateDataRequest(reducer_id=request.reducer_id)                                                
                response = stub.GetIntermediateData(intermediate_data_request)                
                if response.success:                    
                    pairs = self.parseIntermediateData(response.pairs)                    
                    intermediate_data[id] = pairs                    
                else:
                    raise ValueError("Failed to retrieve data from mapper.")  
                time.sleep(1)                      
            grouped_data = self.shuffle_and_sort(intermediate_data)
            new_centroids = self.calculate_new_centroids(grouped_data)
            self.write_centroids_to_file(new_centroids)
            
            reducerReponse = kmeans_pb2.ReducerResponse(reducer_id = request.reducer_id, success=True, message = "SUCCESS")
            print(new_centroids)
            # TODO: why is this happening?
            for i in new_centroids.keys():
                reducerReponse.new_centroids[i].key = 0
                reducerReponse.new_centroids[i].values.extend(new_centroids[i])

            print(f"Sending Reducer Response RPC to Master: {self.reducer_id}")
            # return kmeans_pb2.ReducerResponse(success=True, message = "SUCCESS", new_centroids=flattened_centroids)
            return reducerReponse

        except Exception as e:
            print(e)
            return kmeans_pb2.ReducerResponse(success=False, message=str(e))
    
    def write_centroids_to_file(self, centroids):
        with open(f'Data/Reducers/R_{self.reducer_id}.txt', 'w') as f:
            for key, value in centroids.items():
                f.write(f"({key}, {str(value)})\n")                    
    
    def parseIntermediateData(self, pairs):
        pair_list = []
        pairs = list(pairs)
        for i in pairs:
            temp = (i.replace('\n','').replace(" ", "").split(",", 1))
            centroid_idx = int(temp[0][1])
            centroid = temp[1][:-1].replace("(", "").replace(")", "")
            centroid = tuple(map(float, centroid.split(',')))
            pair_list.append((centroid_idx, centroid))        
        return pair_list        

    def shuffle_and_sort(self, intermediate_data):
        intermediate_data_pairs = []
        for i in intermediate_data.values():
            for j in i:
                intermediate_data_pairs.append(j)        
        
        grouped_data = {}
        # Group values by key
        for key, value in intermediate_data_pairs:
            if key not in grouped_data:
                grouped_data[key] = []
            grouped_data[key].append(value)
        
        sorted_keys = sorted(grouped_data.keys())
        return {key: grouped_data[key] for key in sorted_keys}        
 
    def calculate_new_centroids(self, grouped_data):
        new_centroids = {}        
        for key in grouped_data.keys():
            data_points = grouped_data[key]
            new_centroid = self.calculate_centroid(data_points)
            new_centroids[key] = new_centroid
        return new_centroids

    def calculate_centroid(self, data_points):
        x = round(sum([point[0] for point in data_points]) / len(data_points), 2)
        y = round(sum([point[1] for point in data_points]) / len(data_points), 2)
        return (x, y)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    reducer_address = reducer_id_to_address[int(sys.argv[1])]        
    kmeans_pb2_grpc.add_ReducerServiceServicer_to_server(Reducer(reducer_id=sys.argv[1]), server)
    server.add_insecure_port(reducer_address)
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    reducer_id_to_address = {1: 'localhost:50061', 2: 'localhost:50062'}
    serve()