import os
import random
import sys
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


# TODO: Store the node ids as an array here : 
# The client stores the IP addresses and ports of all the nodes.
# The client stores the current leader ID, although this information might get outdated.

class RaftClient(raftClient_pb2_grpc.RaftClientServiceServicer):
    def __init__(self, num_nodes):                
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
                    print("DIFFERENT LEADER: ", response.leaderId)             
                    self.leader_address = peers[response.leaderId]
                    self.channel = grpc.insecure_channel(self.leader_address)
                    self.stub = raft_pb2_grpc.RaftNodeServiceStub(self.channel)
            
            except Exception as e:                
                print(f'Error connecting to leader {self.leader_address}')                                                           

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

    # Take the first node as the leader and try to connect to it 
    leader_id = int(os.getenv("NODE_1_ID"))

    peers = {}
    for i in range(1, num_nodes+1):        
            index = str(i)
            key = int(os.getenv(f'NODE_{index}_ID'))
            value = f'{os.getenv(f"NODE_{index}_IP")}:{os.getenv(f"NODE_{index}_PORT")}'
            peers[key] = value
    
    client = RaftClient(num_nodes)

    
    
    while True:
        # EXAMPLE COMMANDS:
        # 'SET x 10' -> SET X
        # 'GET x' -> GET X

        command = input("Enter command: ")
        command = command.upper()

        if isValidCommand(command):
            pass
        else:
            print("Invalid command. Please enter a valid command.")

        response = client.client_request(command)
        
        