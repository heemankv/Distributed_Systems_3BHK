import os
import sys
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'raftNode'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))


from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.

import grpc
import raftNode_pb2 as raft_pb2
import raftNode_pb2_grpc as raft_pb2_grpc
import raftClient_pb2 as raftClient_pb2
import raftClient_pb2_grpc as raftClient_pb2_grpc


class RaftClient(raftClient_pb2_grpc.RaftClientServiceServicer):
    def __init__(self):                
        self.leader_address = None

    def client_request(self, command):
        # It sends a GET/SET request to the leader node.
        # In case of a failure, it updates its leader ID and resends the request to the updated leader.
        # The node returns what it thinks is the current leader and a failure message
        # If there is no leader in the system, then the node will return NULL for the current leader and a failure message
        # The client continues sending the request until it receives a SUCCESS reply from any node.

        node_ids = list(peers.keys())
        self.idx = 0
        self.leader_address = peers[node_ids[self.idx]]
        self.channel = grpc.insecure_channel(self.leader_address)
        self.stub = raft_pb2_grpc.RaftNodeServiceStub(self.channel)        

        while True:
            try:
                print("Leader:", self.leader_address)
                response = self.stub.ServeClient(raft_pb2.ServeClientArgs(request=command))
                
                print(f'Response: \n{response}')

                if response.success:
                    print("SUCCESS")
                    return response
                else:       
                    print("FAILURE")
                    print("Different leader: ", response.leaderId)             
                    self.leader_address = peers[response.leaderId]
                    self.channel = grpc.insecure_channel(self.leader_address)
                    self.stub = raft_pb2_grpc.RaftNodeServiceStub(self.channel)
            
            except Exception as e:                
                print(f'Error connecting to leader {self.leader_address}')                                                           
                time.sleep(0.5)
                self.idx += 1
                self.leader_address = peers[node_ids[self.idx % len(node_ids)]]
                self.channel = grpc.insecure_channel(self.leader_address)
                self.stub = raft_pb2_grpc.RaftNodeServiceStub(self.channel)

                print("Trying to connect to leader:", self.leader_address)                                
                


def isValidCommand(command):
    # This function checks if the command is a valid command
    # The command is valid if it is either GET or SET
    # The function returns True if the command is valid, otherwise it returns False
    if  "GET" in command or "SET" in command:
        return True
    else:
        return False


if __name__ == "__main__":
    # Example usage of the RaftClient class
    # Take commnd input from the user
    # Send the command to the leader
    # Print the response

    num_nodes = int(os.getenv("NUM_NODES"))    
    peers = {}
    for i in range(1, num_nodes+1):        
            index = str(i)
            key = int(os.getenv(f'NODE_{index}_ID'))
            value = f'{os.getenv(f"NODE_{index}_IP")}:{os.getenv(f"NODE_{index}_PORT")}'
            peers[key] = value
    
    client = RaftClient()
    
    while True:
        command = input("Enter command: ")
        command = command.upper()

        if isValidCommand(command):
            pass
        else:
            print("Invalid command. Please enter a valid command.")

        response = client.client_request(command)
        
        