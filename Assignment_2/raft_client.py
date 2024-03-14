import grpc
import raft_pb2
import raft_pb2_grpc

def client_request(command):
    for node_id in range(5):
        try:
            with grpc.insecure_channel(f'localhost:{50051 + node_id}') as channel:
                stub = raft_pb2_grpc.RaftServiceStub(channel)
                response = stub.ClientRequest(raft_pb2.ClientRequest(command=command))
                print(f'Response from node {node_id}: {response.result}')
                break
        except Exception as e:
            print(f'Error connecting to node {node_id}: {e}')

if __name__ == '__main__':
    client_request('SET x 10')
    client_request('GET x')
