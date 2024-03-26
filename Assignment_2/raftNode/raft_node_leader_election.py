import grpc
import raftNode_pb2
import raftNode_pb2_grpc
from concurrent import futures
import threading
import random
import os
import datetime


# TODO: The Whole of leader lease is left
# TODO: Ensure a node updates its term whenever it meets a node either in request or response with a higher term
# TODO: NO-OP needs to be sent during start of election

#Assumptions:
#First election at term 1

class RaftNode(raftNode_pb2_grpc.RaftNodeServiceServicer):
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

        self.leaderId = None
        self.old_leader_lease_timestamp=None
        self.leader_lease_timer=None

        # TODO: might have to delete later
        self.data = {}
        self.process_logs_for_intial_status()

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
    
    #Processing logs to get intial status of database
    def process_logs_for_intial_status(self):
        for request in self.log:
            info=request.split()
            if(info[0]=="NO-OP"):
                pass
            elif(info[0]=="SET"):
                key=info[1]
                value=info[2]
                self.data[key]=value
        
    def check_database(self):
        for key in self.data:
            print(key,":",self.data[key])                           
    
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
                    stub = raftNode_pb2_grpc.RaftServiceStub(channel)
                    response = stub.RequestVote(raftNode_pb2.RequestVoteRequest(
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
        '''
        #Leader Lease: Leader needs to send a no-op entry to followers
        #Leader Lease: It must also send lease interval duration whenver the leader starts timer
        #Leader Lease: It must check if the old leader's lease timer hasn't ended
        '''

        while( self.old_leader_lease_timestamp!=None or datetime.now()<self.old_leader_lease_timestamp):



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
        self.stop_leader_lease_timer()
        self.stop_heartbeats()
        self.dump(f'{self.node_id} Stepping down')
        self.state = "follower"        

    def send_heartbeats(self):
        '''
        #Leader Lease: leader reacquires its lease, leader needs to step down if it doesn't get enough ack
        '''
        if self.state != "leader":
            return
        self.dump(f'Leader {self.node_id} sending heartbeat & Renewing Lease')
        ack_received=0
        for peer in self.peers:
            try:
                with grpc.insecure_channel(peer) as channel:
                    stub = raftNode_pb2_grpc.RaftServiceStub(channel)
                    response=stub.AppendEntries(raftNode_pb2.AppendEntriesRequest(
                        term=self.term,
                        leaderId=self.node_id,
                        prevLogIndex=len(self.log) - 1,
                        prevLogTerm=self.log[-1].term if len(self.log)>0 else 0,
                        entries=[],
                        leaderCommit=self.commit_index,
                    ))        
                    if response.success:
                        ack_received += 1

            except Exception as e:
                followerNodeID="{Figure this Id Out}"
                self.dump(f'Error occurred while sending RPC to Node {followerNodeID} with IP {peer}.')
        if ack_received > (len(self.peers)/2):
            self.reset_leader_lease_timer()
           
    
    def start_heartbeats(self):
        self.heartbeats_timer=threading.Timer(1, self.send_heartbeats)
        self.heartbeats_timer.start()
    
    def stop_heartbeats(self):
        if(self.heartbeats_timer):
            self.heartbeats_timer.cancel()
            self.heartbeats_timer=None

    # leader lease related functions
    
    def reset_leader_lease_timer(self):
        self.stop_leader_lease_timer()
        leader_lease_timeout= 2
        self.leader_lease_timer = threading.Timer(leader_lease_timeout, self.become_follower())
        self.leader_lease_timer.start()
    
    def stop_leader_lease_timer(self):
        if(self.leader_lease_timer):
            self.leader_lease_timer.cancel()
            self.leader_lease_timer=None

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
            return raftNode_pb2.RequestVoteResponse(term=self.term, voteGranted=True)
        
        self.dump(f'Vote denied for Node {request.candidateId} in term {request.term}')
        return raftNode_pb2.RequestVoteResponse(term=self.term, voteGranted=False)

    #Node getting an AppendRPC
    #When client will send some write requests, leader needs to send appendRPCs to all its followers. Followers need to add it to their logs after resolving conflicts, if any.
    #Followers need send ACK once log is appended. Depending on the ACK, the leader will commit the index, and inform the followers again.
    
    def AppendEntries(self, request, context):
        if request.term < self.term:
            self.dump(f'Node {self.node_id} rejected AppendEntries RPC from {request.leaderId}.')
            return raftNode_pb2.AppendEntriesResponse(term=self.term, success=False)
        self.reset_election_timer()
        self.term = request.term
        self.become_follower()

        # Log replication and commit logic goes here
        self.dump(f'Node {self.node_id} accepted AppendEntries RPC from {request.leaderId}.')
        return raftNode_pb2.AppendEntriesResponse(term=self.term, success=True)


    def BoradcastCommitMessage(self, request, context):
        '''
        Handles all the replicate logs functions from the leader to the followers
        if leader handle caller
        if follower handle the request

        Pseudo code:
        on request to broadcast msg at node nodeId do
            if currentRole = leader then
                append the record (msg : msg, term : currentTerm) to log
                ackedLength[nodeId] := log.length
                for each follower ∈ nodes \ {nodeId} do
                    ReplicateLog(nodeId, follower )
                end for
            else
                forward the request to currentLeader via a FIFO link
            end if
        end on
        '''
        if self.state == "leader":
            self.log.append(request)
            acked_length = len(self.log)
            replicatedCount = 0
            for peer in self.peers:
                with grpc.insecure_channel(peer) as channel:
                    stub = raftNode_pb2_grpc.RaftServiceStub(channel)
                    response = stub.AppendEntries(raftNode_pb2.AppendEntriesRequest(
                        term=self.term,
                        leaderId=self.node_id,
                        # TODO: unsure of the term and index
                        prevLogIndex=len(self.log) - 2,
                        prevLogTerm=self.log[-2].term if len(self.log)>1 else 0,
                        entries=[request],
                        leaderCommit=self.commit_index,
                    ))

                    if response.AckedLength == acked_length:
                        self.dump(f'Node {self.node_id} received success from {peer}.')
                        replicatedCount += 1
                    else:
                        self.dump(f'Node {self.node_id} received failure from {peer}.')
            if replicatedCount > len(self.peers) // 2:
                # Majority Achieved
                # TODO: send message to client for successful replication
                self.commit_index = acked_length
                self.update_metadata()
                self.dump(f'Node {self.node_id} committed entry {request}.')
            # TODO: handle case of minority
    
        # else case for when the client contacts a Follower, 
        # follower will query the leader to call broadcast message with same request
        else:
            with grpc.insecure_channel(self.leaderId) as channel:
                stub = raftNode_pb2_grpc.RaftServiceStub(channel)
                response = stub.BroadcastMessage(request)
                return response
    




    def BroadcastAppendMessage(self, request, context):
        '''
        Handles all the replicate logs functions from the leader to the followers
        if leader handle caller
        if follower handle the request

        Pseudo code:
        on request to broadcast msg at node nodeId do
            if currentRole = leader then
                append the record (msg : msg, term : currentTerm) to log
                ackedLength[nodeId] := log.length
                for each follower ∈ nodes \ {nodeId} do
                    ReplicateLog(nodeId, follower )
                end for
            else
                forward the request to currentLeader via a FIFO link
            end if
        end on
        '''
        if self.state == "leader":
            self.log.append(request)
            acked_length = len(self.log)
            replicatedCount = 0
            for peer in self.peers:
                with grpc.insecure_channel(peer) as channel:
                    stub = raftNode_pb2_grpc.RaftServiceStub(channel)
                    response = stub.AppendEntries(raftNode_pb2.AppendEntriesRequest(
                        term=self.term,
                        leaderId=self.node_id,
                        # TODO: unsure of the term and index
                        prevLogIndex=len(self.log) - 2,
                        prevLogTerm=self.log[-2].term if len(self.log)>1 else 0,
                        entries=[request],
                        leaderCommit=self.commit_index,
                    ))

                    if response.AckedLength == acked_length:
                        self.dump(f'Node {self.node_id} received success from {peer}.')
                        replicatedCount += 1
                    else:
                        self.dump(f'Node {self.node_id} received failure from {peer}.')
            if replicatedCount > len(self.peers) // 2:
                # Majority Achieved
                # TODO: send message to client for successful replication
                self.commit_index = acked_length
                self.update_metadata()
                self.dump(f'Node {self.node_id} committed entry {request}.')
            # TODO: handle case of minority
    
        # else case for when the client contacts a Follower, 
        # follower will query the leader to call broadcast message with same request
        else:
            with grpc.insecure_channel(self.leaderId) as channel:
                stub = raftNode_pb2_grpc.RaftServiceStub(channel)
                response = stub.BroadcastMessage(request)
                return response
    


    def ReplicateLog(self, request, context):
        '''
        Called on the leader whenever there is a new message in the log, and also
        periodically. If there are no new messages, suffix is the empty list.
        LogRequest messages with suffix = hi serve as heartbeats, letting
        followers know that the leader is still alive

        To synchronize a follower's log with the leader's,
        the leader identifies the latest matching log entry
        (same PrevLogIndex and PrevLogTerm), removes entries in the follower's
        log beyond that point, and transmits all subsequent leader entries.

        '''
        prefix_len = request.PrefixLen
        suffix = request.Suffix

        # Process the log replication
        # Here you would typically send the log entries to the follower node
        
        acked_length = prefix_len + len(suffix)

        return raft_pb2.LogReply(AckedLength=acked_length)




    # private fn
    def internal_get_handler(self, request):
        #  GETs the value of variable passed in the request
        #  if available, returns the value
        #  else returns empty string
        #  Returns the value of the variable
        
        #  Request will be of the form "GET K"
        #  We need to return the value of the key K
        #  If K doesn't exist, return empty string
        key = request.split()[1]
        return self.data.get(key, "")
    
    def GET_handler(self, request):
        # If GET, return the value of the key from the leader node only
        # If the leader node is not known, return failure response to the client

        # If GET, return the value of the key from the leader node only
        value = self.internal_get_handler(request)
        return raftNode_pb2.ServeClientReply(
            successReply=raftNode_pb2.ServeClientSuccessReply(
                data=value,
                leaderId=self.node_id,
                success=True
        ))

    # private fn
    def internal_set_handler(self, request):
        #  SETs the value of variable passed in the request
        #  if variable is not present, creates it
        #  Returns the value of the variable
        key = request.split()[1]
        value = request.split()[2]
        self.data[key] = value
        # TODO: what all to append to the log
        self.update_log(f"SET {key} {value}")


    def SET_handler(self, request):
        # If SET, append the key-value pair to the log of the leader node
        # Send AppendEntries RPC to all the followers
        # Wait for ACK from majority of the followers
        # Commit the entry in the log
        # Return success response to the client

        # Use BroadCast Message
        appendSuccess = self.BroadcastAppendMessage(request=request)
        if(appendSuccess):
            commitSuccess = self.internal_set_handler(request)
            if(commitSuccess):
                self.BoradcastCommitMessage(request=request)
               



    def ServeClient(self, request, context):
        # Request will either be a GET or SET command
        # SWITCH based on command
        # If GET, return the value of the key from the leader node only

        # The operations supported for the client on this database are as follows:

        # SET K V: Maps the key K to value V; for example, {SET x hello} will map the key “x” to value “hello.”
        #  (WRITE OPERATION)
        # GET K: Returns the latest committed value of key K. If K doesn’t exist in the database,
        #  an empty string will be returned as value by default. (READ OPERATION)

        if("GET" in request):
            if(self.state == "leader"):
                return self.GET_handler(request)
            else:
                return raftNode_pb2.ServeClientResponse(
                    failureReply=raftNode_pb2.ServeClientFailureReply(
                        leaderId=self.leaderId,
                        success=False
                    )
                )
            
        elif("SET" in request):
            return self.SET_handler(request)
        else:
            return raftNode_pb2.ServeClientResponse(
                    failureReply=raftNode_pb2.ServeClientFailureReply(
                        leaderId=self.leaderId,
                        success=False
                    )
                )

def serve(node_id, peers):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    raftNode_pb2_grpc.add_RaftNodeServiceServicer_to_server(RaftNode(node_id, peers), server)
    server.add_insecure_port(f'127.0.0.1:{5005 + node_id}')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    import sys
    node_id = int(sys.argv[1])

    # Assumption: Only 5 servers
    peers = [f'127.0.0.1:{5005 + i}' for i in range(5) if i != node_id]
    serve(node_id, peers)
