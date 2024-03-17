import grpc
import raft_pb2
import raft_pb2_grpc
from concurrent import futures
import threading
import random


#LEFT WORK IN LEADER ELECTION:
#1. creating dump files, log files, metadata files
#2. creating leader lease variable which updates itself when we send heartbeats
#3. retrieving info from files if node crashes

class RaftNode(raft_pb2_grpc.RaftServiceServicer):
    def __init__(self, node_id, peers):
        self.node_id = node_id
        self.peers = peers
        
        self.voted_for = None
        self.log = []
        self.term = self.log[-1].term if len(self.log)>0 else 0
        self.commit_index = 0
        self.state = "follower"
        self.election_timeout = random.uniform(5, 10)
        self.election_timer = threading.Timer(self.election_timeout, self.start_election)
        self.heartbeats_timer=None
        self.election_timer.start()

        print(str(self.node_id)+" has started")
        print(self.term)

    # Contesting elections in case of timeout
    def start_election(self):
        self.term += 1
        print(f'Node {self.node_id} election timer timed out, Starting election For Term {self.term}.')
        self.become_follower() #Done to stop heartbeats if it is a leader
        self.state = "candidate"
        
        self.voted_for = self.node_id
        votes_received = 1
        for peer in self.peers:
            try:
                with grpc.insecure_channel(peer) as channel:
                    stub = raft_pb2_grpc.RaftServiceStub(channel)
                    response = stub.RequestVote(raft_pb2.RequestVoteRequest(
                        term=self.term,
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
                followerNodeID="Figure this Id"
                print(f'Error occurred while sending RPC to Node {followerNodeID}.')
        
        if votes_received > len(self.peers) // 2 and self.status !="leader":
            self.become_leader()
            
            
        if(self.state!="leader"):
            self.term-=1
            self.become_follower()
            print(str(self.node_id)+" became follower")

        self.reset_election_timer()

    
    # Become leader if win election
    def become_leader(self):
        print(f'Node {self.node_id} became the leader for term {self.term}.')
        self.state = "leader"
        # self.next_index = {peer: len(self.log) for peer in self.peers}
        # self.match_index = {peer: 0 for peer in self.peers}

        # Add NO-OP entry to log 

        #Sending heartbeats for first time
        self.send_heartbeats()

        #Starting timer
        self.start_heartbeats()

    # Become follower    
    def become_follower(self):
        print(f'{self.node_id} Stepping down')
        self.state = "follower"
        self.stop_heartbeats()

    def send_heartbeats(self):
        if self.state != "leader":
            return
        print(f'Leader {self.node_id} sending heartbeat & Renewing Lease')
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

    def RequestVote(self, request, context):
        #settingToFollowerIfRequired
        if request.term > self.term:
            self.term=request.term
            self.voted_for=None
            self.become_follower()
        
        #log check
        logCheck=False
        currentLastLogTerm= self.log[-1].term if len(self.log)>0 else 0
        if request.lastLogTerm > currentLastLogTerm or (request.lastLogTerm==currentLastLogTerm and  request.lastLogIndex>=len(self.log)-1):
            logCheck=True
        
        #sending response based on conditions
        if request.term>=self.term and logCheck and self.voted_for in [None, request.candidateId]:
            self.term = request.term
            self.voted_for = request.candidateId    
            self.reset_election_timer()
            print(f'Vote granted for Node {request.candidateId} in term {request.term}')
            return raft_pb2.RequestVoteResponse(term=self.term, voteGranted=True)
        
        print(f'Vote denied for Node {request.candidateId} in term {request.term}')
        return raft_pb2.RequestVoteResponse(term=self.term, voteGranted=False)

    def AppendEntries(self, request, context):
        print(str(self.node_id)+" recieved heartbeat from "+ str(request.leaderId))
        if request.term < self.term:
            print(str(self.node_id)+" rejected AppendRPC from "+ str(request.leaderId))
            return raft_pb2.AppendEntriesResponse(term=self.term, success=False)
        self.reset_election_timer()
        self.term = request.term
        self.become_follower()

        # Log replication and commit logic goes here
        print(f'Node {self.node_id} accepted AppendEntries RPC from {request.leaderId}.')
        return raft_pb2.AppendEntriesResponse(term=self.term, success=True)

    # def ClientRequest(self, request, context):
    #     if self.state != "leader":
    #         return raft_pb2.ClientRequestResponse(result="Not the leader")
    #     # Command handling logic goes here
    #     return raft_pb2.ClientRequestResponse(result="Command executed")

def serve(node_id, peers):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    raft_pb2_grpc.add_RaftServiceServicer_to_server(RaftNode(node_id, peers), server)
    server.add_insecure_port(f'[::]:{5005 + node_id}')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    import sys
    node_id = int(sys.argv[1])

    # Assumption: Only 5 servers
    peers = [f'localhost:{5005 + i}' for i in range(5) if i != node_id]
    serve(node_id, peers)
