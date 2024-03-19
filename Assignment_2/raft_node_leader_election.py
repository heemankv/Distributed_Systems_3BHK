import grpc
import raft_pb2
import raft_pb2_grpc
from concurrent import futures
import threading
import random
import os

#Assumptions:
#First election at term 1

#LEFT WORK IN LEADER ELECTION:
#2. Creating leader lease variable which updates itself when we send heartbeats

class RaftNode(raft_pb2_grpc.RaftServiceServicer):
    def __init__(self, node_id, peers):
        self.node_id = node_id
        self.create_folders_and_files()
        self.peers = peers
        self.log = self.read_from_logs_file()
        metadata = self.read_from_metadata_file()
        self.term = int(metadata['term']) #self.log[-1].split()[-1] if len(self.log)>0 else 0
        self.commit_index = int(metadata['commitLength'])
        self.voted_for = metadata['voted_for']

        #Checking metadata values if crashed
        print("Checking Values:",self.term,self.commit_index,self.voted_for)

        self.state = "follower"
        self.election_timeout = random.uniform(5, 10)
        self.election_timer = threading.Timer(self.election_timeout, self.start_election)
        self.heartbeats_timer=None
        self.election_timer.start()

        print("Node "+str(self.node_id)+" has started")
    
    # Creating files
    def create_folders_and_files(self):
        # Define folder name
        folder_name='logs_node_'+str(self.node_id)
        
        # Create folder if it don't exist
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
    
        # Define file names
        file_names = ['logs.txt','dump.txt']
        
        for file_name in file_names:
            file_path = os.path.join(folder_name, file_name)
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    pass  # Create an empty file

        file_path = os.path.join(folder_name, 'metadata.txt')
        if not os.path.exists(file_path):
            self.term=0
            self.voted_for=None
            self.commit_index=0
            with open(file_path, 'w') as f:
                f.write(f"commitLength: {self.commit_index}\n")
                f.write(f"term: {self.term}\n")
                f.write(f"voted_for: {self.voted_for}\n")

    #Appending To Log
    def update_log(self,entry):
        folder_name='logs_node_'+str(self.node_id)
        file_path = os.path.join(folder_name, 'logs.txt')
        with open(file_path, 'a') as f:
            f.write(f"{entry}\n")
    
    #Appending to Dump
    def dump(self,entry):
        folder_name='logs_node_'+str(self.node_id)
        file_path = os.path.join(folder_name, 'dump.txt')
        with open(file_path, 'a') as f:
            f.write(f"{entry}\n")

    #Updating Metadata
    def update_metadata(self):
        folder_name='logs_node_'+str(self.node_id)
        file_path = os.path.join(folder_name, 'metadata.txt')
        with open(file_path, 'w') as f:
            f.write(f"commitLength: {self.commit_index}\n")
            f.write(f"term: {self.term}\n")
            f.write(f"voted_for: {self.voted_for}\n")
   
    #Reading from logs file:
    def read_from_logs_file(self):
        try:
            file_path="logs_node_"+str(self.node_id)+"/logs.txt"
            with open(file_path, 'r') as file:
                lines = file.readlines()
            return lines
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            return []
        
    #Reading from metadata file:
    def read_from_metadata_file(self):
        try:
            metadata = {}
            file_path="logs_node_"+str(self.node_id)+"/metadata.txt"
            with open(file_path, 'r') as file:
                for line in file:
                    if ':' in line:
                        key, value = line.strip().split(':', 1)
                        metadata[key.strip()] = value.strip()
            return metadata
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            return {}
    
    # Contesting elections in case of timeout
    def start_election(self):
        self.dump(f'Node {self.node_id} election timer timed out, Starting election For Term {self.term}.')

        self.become_follower() #Done to stop heartbeats if it is a leader
        self.state = "candidate"
        
        self.voted_for = self.node_id
        votes_received = 1
        for peer in self.peers:
            try:
                with grpc.insecure_channel(peer) as channel:
                    stub = raft_pb2_grpc.RaftServiceStub(channel)
                    response = stub.RequestVote(raft_pb2.RequestVoteRequest(
                        term=self.term+1,
                        candidateId=self.node_id,
                        lastLogIndex=len(self.log) - 1,
                        lastLogTerm=self.log[-1].term if len(self.log)>0 else 0,
                    ))
                    if response.voteGranted:
                        votes_received += 1
                        if votes_received > len(self.peers) // 2:
                            self.become_leader()
                            break

            except Exception as e:
                followerNodeID="{Figure this Id Out}"
                self.dump(f'Error occurred while sending RPC to Node {followerNodeID} with IP {peer}.')
        
        if votes_received > len(self.peers) // 2 and self.state !="leader":
            self.become_leader()
            
            
        if(self.state!="leader"):
            self.become_follower()

        self.reset_election_timer()

    
    # Become leader if win election
    def become_leader(self):
        self.term+=1
        self.dump(f'Node {self.node_id} became the leader for term {self.term}.')
        self.state = "leader"        
        self.update_metadata()

        # Add NO-OP entry to log 

        #Sending heartbeats for first time
        self.send_heartbeats()

        #Starting timer
        self.start_heartbeats()

    # Become follower    
    def become_follower(self):
        self.stop_heartbeats()
        self.dump(f'{self.node_id} Stepping down')
        self.state = "follower"        

    def send_heartbeats(self):
        if self.state != "leader":
            return
        self.dump(f'Leader {self.node_id} sending heartbeat & Renewing Lease')
        for peer in self.peers:
            with grpc.insecure_channel(peer) as channel:
                stub = raft_pb2_grpc.RaftServiceStub(channel)
                stub.AppendEntries(raft_pb2.AppendEntriesRequest(
                    term=self.term,
                    leaderId=self.node_id,
                    prevLogIndex=len(self.log) - 1,
                    prevLogTerm=self.log[-1].term if len(self.log)>0 else 0,
                    entries=[],
                    leaderCommit=self.commit_index,
                ))        
    
    def start_heartbeats(self):
        self.heartbeats_timer=threading.Timer(1, self.send_heartbeats)
        self.heartbeats_timer.start()
    
    def stop_heartbeats(self):
        if(self.heartbeats_timer):
            self.heartbeats_timer.cancel()
            self.heartbeats_timer=None

    def reset_election_timer(self):
        self.election_timer.cancel()
        self.election_timeout = random.uniform(5, 10)
        self.election_timer = threading.Timer(self.election_timeout, self.start_election)
        self.election_timer.start()

    #Node getting request for a vote
    def RequestVote(self, request, context):
        #settingToFollowerIfRequired
        if request.term > self.term:
            self.term=request.term
            self.voted_for="None"
            self.become_follower()
        
        #log is verified
        logCheck=False
        currentLastLogTerm= self.log[-1].term if len(self.log)>0 else 0
        if request.lastLogTerm > currentLastLogTerm or (request.lastLogTerm==currentLastLogTerm and  request.lastLogIndex>=len(self.log)-1):
            logCheck=True
        
        #sending response based on conditions
        if request.term>=self.term and logCheck and self.voted_for in [str(request.candidateId),"None"]:
            self.term = request.term
            self.voted_for = str(request.candidateId)    
            self.update_metadata()
            self.reset_election_timer()
            self.dump(f'Vote granted for Node {request.candidateId} in term {request.term}')
            return raft_pb2.RequestVoteResponse(term=self.term, voteGranted=True)
        
        self.dump(f'Vote denied for Node {request.candidateId} in term {request.term}')
        return raft_pb2.RequestVoteResponse(term=self.term, voteGranted=False)

    #Node getting an AppendRPC
    #When client will send some write requests, leader needs to send appendRPCs to all its followers. Followers need to add it to their logs after resolving conflicts, if any.
    #Followers need send ACK once log is appended. Depending on the ACK, the leader will commit the index, and inform the followers again.
    
    def AppendEntries(self, request, context):
        if request.term < self.term:
            self.dump(f'Node {self.node_id} rejected AppendEntries RPC from {request.leaderId}.')
            return raft_pb2.AppendEntriesResponse(term=self.term, success=False)
        self.reset_election_timer()
        self.term = request.term
        self.become_follower()

        # Log replication and commit logic goes here
        self.dump(f'Node {self.node_id} accepted AppendEntries RPC from {request.leaderId}.')
        return raft_pb2.AppendEntriesResponse(term=self.term, success=True)

    # def ClientRequest(self, request, context):
    #     if self.state != "leader":
    #         return raft_pb2.ClientRequestResponse(result="Not the leader")
    #     # Command handling logic goes here
    #     return raft_pb2.ClientRequestResponse(result="Command executed")

def serve(node_id, peers):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    raft_pb2_grpc.add_RaftServiceServicer_to_server(RaftNode(node_id, peers), server)
    server.add_insecure_port(f'127.0.0.1:{5005 + node_id}')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    import sys
    node_id = int(sys.argv[1])

    # Assumption: Only 5 servers
    peers = [f'127.0.0.1:{5005 + i}' for i in range(5) if i != node_id]
    serve(node_id, peers)
