import os
import grpc
import raft_pb2
import raft_pb2_grpc

from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.

# TODO: Store the node ids as an array here : 
# The client stores the IP addresses and ports of all the nodes.
# The client stores the current leader ID, although this information might get outdated.


def CreateNodeAddresses(numNodes):
    # This function creates an array of IP addresses and ports of all the nodes.
    # The IP addresses and ports are read from the .env file.
    # The array is returned.
    node_ips = []
    for i in range(numNodes):
        index = i + 1
        node_ips.append(f'{os.getenv(f"NODE{index}_IP")}:{os.getenv(f"NODE{index}_PORT")}')
    return node_ips

class RaftClient:
    def __init__(self, num_nodes, leader_address):
        self.node_ips = CreateNodeAddresses(num_nodes)
        self.channel = grpc.insecure_channel(leader_address)
        self.stub = raft_pb2_grpc.RaftClusterStub(self.channel)
        self.leader_address = leader_address
        self.leader_id = None


    def client_request(self, command):
        # It sends a GET/SET request to the leader node.
        # In case of a failure, it updates its leader ID and resends the request to the updated leader.
        # The node returns what it thinks is the current leader and a failure message
        # If there is no leader in the system, then the node will return NULL for the current leader and a failure message
        # The client continues sending the request until it receives a SUCCESS reply from any node.

        while True:
            try:
                response = self.stub.ServeClient(raft_pb2.ServeClientArgs(request=command))
                if response.success:
                    return response
                else:
                    self.leader_address = response.leader_id
                    self.channel = grpc.insecure_channel(self.leader_address)
                    self.stub = raft_pb2_grpc.RaftClusterStub(self.channel)
            except Exception as e:
                # TODO: In this case will the client not contact any other node?
                print(f'Error connecting to leader {self.leader_address} : {e}')
                self.leader_address = None
                self.stub = None
                self.leader_id = None
                


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

    num_nodes = os.getenv("NUM_NODES")

    # Take the first node as the leader and try to connect to it
    leader_address = f'{os.getenv("NODE1_IP")}:{os.getenv("NODE1_PORT")}'

    client = RaftClient(num_nodes, leader_address)


    while True:
        # Take input from the user
        # Send the command to the leader
        # Print the response

        command = input("Enter command: ")
        command = command.upper()

        if isValidCommand(command):
            pass
        else:
            print("Invalid command. Please enter a valid command.")

        response = client.client_request(command)
        print(response)
        print("Leader ID: ", response.leader_id)
        print("Success: ", response.success)