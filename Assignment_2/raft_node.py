import grpc
import raft_pb2
import raft_pb2_grpc
from concurrent import futures
import threading
import time
import random

class RaftNode(raft_pb2_grpc.RaftServiceServicer):
    def __init__(self, node_id, peers):
        self.node_id = node_id
        self.peers = peers
        self.term = 0
        self.voted_for = None
        self.log = []
        self.commit_index = 0
        self.last_applied = 0
        self.state = "follower"
        self.election_timeout = random.uniform(5, 10)
        self.election_timer = threading.Timer(self.election_timeout, self.start_election)
        self.election_timer.start()

    def start_election(self):
        self.state = "candidate"
        self.term += 1
        self.voted_for = self.node_id
        votes_received = 1
        for peer in self.peers:
            with grpc.insecure_channel(peer) as channel:
                stub = raft_pb2_grpc.RaftServiceStub(channel)
                response = stub.RequestVote(raft_pb2.RequestVoteRequest(
                    term=self.term,
                    candidateId=self.node_id,
                    lastLogIndex=len(self.log) - 1,
                    lastLogTerm=self.log[-1].term if self.log else 0,
                ))
                if response.voteGranted:
                    votes_received += 1
                    if votes_received > len(self.peers) // 2:
                        self.become_leader()
                        break
        self.reset_election_timer()

    def become_leader(self):
        self.state = "leader"
        self.next_index = {peer: len(self.log) for peer in self.peers}
        self.match_index = {peer: 0 for peer in self.peers}
        self.send_heartbeats()

    def send_heartbeats(self):
        if self.state != "leader":
            return
        for peer in self.peers:
            with grpc.insecure_channel(peer) as channel:
                stub = raft_pb2_grpc.RaftServiceStub(channel)
                stub.AppendEntries(raft_pb2.AppendEntriesRequest(
                    term=self.term,
                    leaderId=self.node_id,
                    prevLogIndex=len(self.log) - 1,
                    prevLogTerm=self.log[-1].term if self.log else 0,
                    entries=[],
                    leaderCommit=self.commit_index,
                ))
        threading.Timer(1, self.send_heartbeats).start()

    def reset_election_timer(self):
        self.election_timer.cancel()
        self.election_timeout = random.uniform(5, 10)
        self.election_timer = threading.Timer(self.election_timeout, self.start_election)
        self.election_timer.start()

    def RequestVote(self, request, context):
        if request.term < self.term:
            return raft_pb2.RequestVoteResponse(term=self.term, voteGranted=False)
        if request.term > self.term or self.voted_for is None or self.voted_for == request.candidateId:
            self.term = request.term
            self.voted_for = request.candidateId
            self.reset_election_timer()
            return raft_pb2.RequestVoteResponse(term=self.term, voteGranted=True)
        return raft_pb2.RequestVoteResponse(term=self.term, voteGranted=False)

    def AppendEntries(self, request, context):
        if request.term < self.term:
            return raft_pb2.AppendEntriesResponse(term=self.term, success=False)
        self.reset_election_timer()
        self.term = request.term
        self.state = "follower"
        # Log replication and commit logic goes here
        return raft_pb2.AppendEntriesResponse(term=self.term, success=True)

    def ClientRequest(self, request, context):
        if self.state != "leader":
            return raft_pb2.ClientRequestResponse(result="Not the leader")
        # Command handling logic goes here
        return raft_pb2.ClientRequestResponse(result="Command executed")

def serve(node_id, peers):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    raft_pb2_grpc.add_RaftServiceServicer_to_server(RaftNode(node_id, peers), server)
    server.add_insecure_port(f'[::]:{50051 + node_id}')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    import sys
    node_id = int(sys.argv[1])
    peers = [f'localhost:{50051 + i}' for i in range(5) if i != node_id]
    serve(node_id, peers)
