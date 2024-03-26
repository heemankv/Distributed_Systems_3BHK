import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'raftClient'))

from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.

import grpc
import raftNode_pb2
import raftNode_pb2_grpc
from concurrent import futures
import threading
import random
from datetime import datetime, timezone, timedelta


# TODO: Change AppendRPCs and VoteRPCs for leader lease
# TODO: Ensure a node updates its term whenever it meets a node either in request or response with a higher term
# TODO: NO-OP needs to be sent during start of election
#  TODO: cancel election timer : is it reset or stop
#Assumptions:
#First election at term 1

class RaftNode(raftNode_pb2_grpc.RaftNodeServiceServicer):
    # 1/9
    def __init__(self, node_id, peers):
        self.node_id = node_id
        self.create_folders_and_files()
        self.peers : dict = peers
        self.log = self.read_from_logs_file()
        self.metadata = self.read_from_metadata_file()
        self.term = int(self.metadata['term']) 
        self.commit_index = int(self.metadata['commitLength'])

        # TODO: remove this and access it from metadata itself
        self.voted_for = self.metadata['voted_for']

        #Checking metadata values if crashed
        print("Checking Values:",self.term,self.commit_index,self.voted_for)

        self.state = "follower"
        self.election_timeout = random.uniform(5, 10)
        self.election_timer = threading.Timer(self.election_timeout, self.start_election)
        self.heartbeats_timer=None
        self.election_timer.start()

        self.leaderId = None

        #LeaderLease related variables
        self.old_leader_lease_timestamp=None
        self.leader_lease_timer=None
        self.leader_lease_end_timestamp=None

        self.sentLength = {}
        self.ackedLength = {}

        # TODO: might have to delete later
        self.data = {}
        self.process_logs_for_intial_status()        

        print("Node "+str(self.node_id)+" has started")
    

    def getTermGivenLog(self,entry):
        return int(entry.split()[-1])

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
        if(entry):
            folder_name='logs_node_'+str(self.node_id)
            file_path = os.path.join(folder_name, 'logs.txt')
            with open(file_path, 'a') as f:
                f.write(f"{entry}\n")

            # Change the self.log as well
            self.log = self.read_from_logs_file()
        
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

        self.metadata = self.read_from_metadata_file()
   
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
        self.dump(f'Node {self.node_id} election timer timed out, Starting election For Term {self.term+1}.')

        self.become_follower() #Done to stop heartbeats if it is a leader
        self.state = "candidate"
        
        self.voted_for = self.node_id
        votes_received = 1
        
        duration_left=max((self.old_leader_lease_timestamp-datetime.now(timezone.utc)).total_seconds(),0) if self.old_leader_lease_timestamp else 0
        for peerID, peerAddress in self.peers.items():
            try:
                with grpc.insecure_channel(peerAddress) as channel:
                    stub = raftNode_pb2_grpc.RaftNodeServiceStub(channel)
                    response = stub.RequestVote(raftNode_pb2.RequestVoteRequest(
                        term=self.term+1,
                        candidateId=self.node_id,
                        lastLogIndex=len(self.log) - 1,
                        lastLogTerm=self.getTermGivenLog(self.log[-1]) if len(self.log)>0 else 0,
                    ))
                    if response.voteGranted:
                        votes_received += 1
                        duration_left=max(duration_left,response.oldLeaderLeaseDuration)
                        # if votes_received > len(self.peers) // 2:
                        #     self.become_leader()
                        #     break

            except Exception as e:                
                followerNodeID=peer.split(":")[1]
                self.dump(f'Error occurred while sending RPC to Node {followerNodeID} with IP {peer}.')
        
        self.old_leader_lease_timestamp=datetime.now(timezone.utc) + timedelta(seconds=duration_left)
        
        if votes_received > len(self.peers) // 2:
            self.become_leader()
                        
        if(self.state!="leader"):
            self.become_follower()

        self.reset_election_timer()

    
    # Become leader if win election
    def become_leader(self):
        '''
        #LeaderLease: Leader needs to send a no-op entry to followers - Done
        #LeaderLease: It must also send lease interval duration whenver the leader starts timer -Done
        #LeaderLease: It must check if the old leader's lease timer hasn't ended - Done
        '''

        while( self.old_leader_lease_timestamp!=None and datetime.now(timezone.utc) < self.old_leader_lease_timestamp):
            pass

        
        self.term+=1
        self.reset_leader_lease_timer()
        self.state = "leader"                
        self.update_metadata()
        self.dump(f'Node {self.node_id} became the leader for term {self.term}.')

        for peerID, peerAddress in self.peers.items():
            self.sentLength[peerID]=len(self.log)
            self.ackedLength[peerID]=0

        self.BroadcastAppendMessage("NO-OP "+str(self.term))            

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
        #LeaderLease: leader reacquires its lease, leader needs to step down if it doesn't get enough ack - Done
        '''
        if self.state != "leader":
            return
        self.dump(f'Leader {self.node_id} sending heartbeat & Renewing Lease')
        ack_received=0
        for followerID, followerAddress in self.peers.items():
                # 5/9
                # if replicated: replicatedCount += 1
                replicatedLogResponse = self.ReplicateLog(self.node_id, followerID)

                if replicatedLogResponse and replicatedLogResponse.success==True:
                    ack_received += 1

        if ack_received > (len(self.peers)/2):
            self.reset_leader_lease_timer()
        else:
            self.become_follower()
           
    def start_heartbeats(self):
        self.heartbeats_timer=threading.Timer(1, self.send_heartbeats)
        self.heartbeats_timer.start()
    
    def stop_heartbeats(self):
        if(self.heartbeats_timer):
            self.heartbeats_timer.cancel()
            self.heartbeats_timer=None

    #LeaderLease related functions
    
    def reset_leader_lease_timer(self):
        self.stop_leader_lease_timer()
        leader_lease_timeout= 2
        self.leader_lease_timer = threading.Timer(leader_lease_timeout, self.become_follower())
        self.leader_lease_timer.start()
        self.leader_lease_end_timestamp= datetime.now(timezone.utc) + timedelta(seconds=leader_lease_timeout)
        self.old_leader_lease_timestamp=self.leader_lease_end_timestamp
    
    def stop_leader_lease_timer(self):
        if(self.leader_lease_timer):
            self.leader_lease_timer.cancel()
            self.leader_lease_timer=None
        self.leader_lease_end_timestamp=None

    def reset_election_timer(self):
        self.election_timer.cancel()
        self.election_timeout = random.uniform(5, 10)
        self.election_timer = threading.Timer(self.election_timeout, self.start_election)
        self.election_timer.start()
    
    def get_lease_duration(self):
        duration_left=max((self.leader_lease_end_timestamp-datetime.now(timezone.utc)).total_seconds(),0)
        return duration_left

    #Node getting request for a vote
    def RequestVote(self, request, context):
        '''
        #LeaderLease: Need to send old leader lease duration - Done
        duration_left=max((self.old_leader_lease_timestamp-datetime.now(timezone.utc)).total_seconds(),0)      
        '''
        duration_left=0
        if(self.old_leader_lease_timestamp):
            duration_left=max((self.old_leader_lease_timestamp-datetime.now(timezone.utc)).total_seconds(),0) 
    
        #settingToFollowerIfRequired
        if request.term > self.term:
            self.term=request.term
            self.voted_for="None"
            self.become_follower()
        
        #log is verified
        logCheck=False
        currentLastLogTerm= self.getTermGivenLog(self.log[-1]) if len(self.log)>0 else 0
        if request.lastLogTerm > currentLastLogTerm or (request.lastLogTerm==currentLastLogTerm and  request.lastLogIndex>=len(self.log)-1):
            logCheck=True
        
        #sending response based on conditions
        if request.term>=self.term and logCheck and self.voted_for in [str(request.candidateId),"None"]:
            self.term = request.term
            self.voted_for = str(request.candidateId)    
            self.update_metadata()
            self.reset_election_timer()
            self.dump(f'Vote granted for Node {request.candidateId} in term {request.term}')
            return raftNode_pb2.RequestVoteResponse(term=self.term, voteGranted=True, oldLeaderLeaseDuration=duration_left)
        
        self.dump(f'Vote denied for Node {request.candidateId} in term {request.term}')
        return raftNode_pb2.RequestVoteResponse(term=self.term, voteGranted=False, oldLeaderLeaseDuration=duration_left)

    #Node getting an AppendRPC
    #When client will send some write requests, leader needs to send appendRPCs to all its followers. Followers need to add it to their logs after resolving conflicts, if any.
    #Followers need send ACK once log is appended. Depending on the ACK, the leader will commit the index, and inform the followers again.
    

    # def AppendEntries(self, request, context):
    #     """
    #     #LeaderLease: Need to compute leader lease end timestamp from leader's lese duration left
    #     self.old_leader_lease_timestamp=datetime.now(timezone.utc) + timedelta(seconds=duration)
    #     """
    #     if request.term < self.term:
    #         self.dump(f'Node {self.node_id} rejected AppendEntries RPC from {request.leaderId}.')
    #         return raftNode_pb2.AppendEntriesResponse(term=self.term, success=False)
        
    #     # Indicates follower has found a leader with higher term
    #     # It resets its election timer, becomes a follower and updates its term
    #     self.reset_election_timer()
    #     self.term = request.term
    #     self.become_follower()

    #     # Log replication and commit logic goes here (7/9)

    #     # 1st of all, the follower will check whether it has enough entries in the log as the request says so i.e. it has request.prefixLen entries in the log
    #     # Then it checks whether prevLogTerm = term of that last entry in the log
        

    #     self.dump(f'Node {self.node_id} accepted AppendEntries RPC from {request.leaderId}.')
    #     return raftNode_pb2.AppendEntriesResponse(term=self.term, success=True)

    # 6/9
    def LogRequest(self, request, context):        
        # request : LogEntriesRequest
        # response : LogEntriesResponse
        
        _leader_id = request.leaderId
        _term = request.term
        _prefix_len = request.prefixLength
        _prefix_term = request.prefixTerm
        _commit_len = request.commitLength
        _suffix = request.suffix

        # Indicates follower has found a leader with higher term
        # It resets its election timer, becomes a follower and updates its term
        if _term >= self.term:
            self.term = _term            
            self.voted_for = "None"            
            self.become_follower()
            self.reset_election_timer()
            self.leaderId = _leader_id

        # 1st of all, the follower will check whether it has enough entries in the log as the request says so i.e. it has request.prefixLen entries in the log
        # Then it checks whether prevLogTerm = term of that last entry in the log
        logCheck=False
        currentLastLogTerm = self.getTermGivenLog(self.log[-1]) if len(self.log)>0 else 0
        acked_length = _prefix_len + len(_suffix)
        
        if len(self.log) >= _prefix_len and _prefix_term == currentLastLogTerm:
            logCheck=True
        
        if _term == self.term and logCheck:            
            self.appendEntries(_prefix_len, _commit_len, _suffix)            
            
            self.dump(f'Node {self.node_id} accepted AppendEntries RPC from {request.leaderId}.')
            return raftNode_pb2.LogEntriesResponse(nodeId=self.node_id, term=self.term, ackedLength=acked_length, success=True)
        
        else:
            self.dump(f'Node {self.node_id} rejected AppendEntries RPC from {request.leaderId}.')
            return raftNode_pb2.LogEntriesResponse(nodeId=self.node_id, term=self.term, ackedLength=acked_length, success=False)    
        
    # 7/9
    def appendEntries(self, prefix_len, leader_commit_len, suffix):
        if len(suffix) > 0 and len(self.log) > prefix_len:
            index = min(len(self.log), prefix_len + len(suffix)) - 1

            log_at_index = self.log[index]
            term_of_log_at_index = self.getTermGivenLog(log_at_index)
            term_of_suffix_at_index=self.getTermGivenLog(suffix[index-prefix_len])

            if(term_of_log_at_index!= term_of_suffix_at_index):
                self.log = self.log[:prefix_len-1]
        
        if prefix_len + len(suffix) > len(self.log):
            for i in range(len(self.log)-prefix_len, len(suffix) - 1):
                self.update_log(suffix[i])

        if leader_commit_len > self.commit_index:
            for i in range(self.commit_index, leader_commit_len-1):
                operation=self.log[i].split()[0]
                if(operation=="SET"):
                    self.internal_set_handler(self.log[i])
                pass
            self.commit_index = leader_commit_len

    # 5/9
    def ReplicateLog(self, leader_id, follower):
        '''
        Returns True if the log was successfully replicated, False otherwise
        '''
        try:
            with grpc.insecure_channel(follower) as channel:
                # prepare the params 
                current_term = self.term

                # prefixLen should be length of the log of the follower till which it matches the leader's log                                   
                prefixLen = self.sentLength[follower]

                # If there's no entry in the log, prefixTerm = 0, else get the term of the last one in the prefix
                prefixTerm = 0
                if prefixLen > 0:
                    prefixTerm = self.getTermGivenLog(self.log[prefixLen - 1])                

                # Make a suffix which will be log[prevLogIndex:] i.e. all entries of leader's log after prevLogIndex
                suffix = self.log[prefixLen: ]

                # The length of the log that has been committed
                commitLength = self.commit_index
                                                                
                #  send the params

                stub = raftNode_pb2_grpc.RaftNodeServiceStub(channel)
                response = stub.LogRequest(raftNode_pb2.LogEntriesRequest(
                    leaderId=leader_id,
                    term=current_term,
                    prefixLength=prefixLen,
                    prefixTerm=prefixTerm,
                    commitLength=commitLength,
                    suffix=suffix,
                    LeaseDuration=self.get_lease_duration()
                ))

                return response
            
        except Exception as e:
            print("Exception1:", e)
            return None
            
            # TODO: validate
            # if response.ackedLength == acked_length:
            #     self.dump(f'Node {self.node_id} received success from {follower}.')
            #     return True
            # else:
            #     self.dump(f'Node {self.node_id} received failure from {follower}.')
            #     return False
        

    def acks(self,length):
        """Define the set of nodes that have acknowledged log entries up to a certain length."""
        return {n for n,v in self.peers.items() if self.ackedLength[n] >= length}

    def commitLogEntries(self):
        # Assuming nodes is a list of node identifiers in the Raft cluster
        # Assuming ackedLength is a dictionary with nodes as keys and the length of the log they have acknowledged as values
        # Assuming log is a list of log entries and each entry has a 'term' and 'msg' field

        minAcks = (len(self.peers) + 1) // 2

        # Find indices that are ready to be committed
        ready = {len_idx for len_idx in range(1, len(self.log) + 1) if len(self.acks(self,len_idx)) >= minAcks}

        if ready and max(ready) > self.commit_index and self.getTermGivenLog(self.log[max(ready) - 1]) == self.term:
            for i in range(self.commit_index, max(ready)):      
                self.internal_set_handler(self.log[i])          
                self.dump(f'Node {self.node_id} committed entry {self.log[i]}.')                
            self.commit_index = max(ready)


    def BroadcastAppendMessage(self, request):
        # 4/9
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
            self.update_log(request)            
            acked_length = len(self.log)
            replicatedCount = 0
            for followerID, followerAddress in self.peers.items():
                # 5/9
                # if replicated: replicatedCount += 1
                replicatedLogResponse = self.ReplicateLog(self.node_id, followerID)

                if(replicatedLogResponse==None):
                    self.dump(f'Error occurred while sending RPC to Node {followerID}')
                    break

                # 8/9
                followerId = replicatedLogResponse.nodeId
                followerTerm = replicatedLogResponse.term
                followerAckedLength = replicatedLogResponse.ackedLength
                followerSuccess = replicatedLogResponse.success

                if followerTerm == self.term and self.state == "leader"  :
                    if followerSuccess and followerAckedLength  >= self.ackedLength[followerId]:
                        self.sentLength[followerId] = followerAckedLength
                        self.ackedLength[followerId] = followerAckedLength
                        # TODO: implement the commitLogEntries()
                        self.commitLogEntries()
                    elif self.sentLength[followerId] > 0:
                        self.sentLength[followerId] -= 1
                        # TODO: Validate : Call ReplicateLog on that follower exact node again
                        self.ReplicateLog(self.node_id, followerId)
                    
                elif followerTerm > self.term:
                    # cancel election timer
                    # current role  = follower
                    # 
                    self.become_follower()
                    self.reset_election_timer()
                    self.term = followerTerm
                    self.voted_for = "None"
                    return
                    

            # if replicatedCount > len(self.peers) // 2:
            #     # Majority Achieved
            #     # TODO: send message to client for successful replication
            #     return True
            # else:   
            #     # Majority not achieved
            #     return False
            
       
    
        # else case for when the client contacts a Follower, 
        # follower will query the leader to call broadcast message with same request
        else:
            with grpc.insecure_channel(self.leaderId) as channel:
                stub = raftNode_pb2_grpc.RaftNodeServiceStub(channel)
                response = stub.BroadcastMessage(request)
                return response
    


    # def ReplicateLog(self, request, context):
    #     '''
    #     Called on the leader whenever there is a new message in the log, and also
    #     periodically. If there are no new messages, suffix is the empty list.
    #     LogRequest messages with suffix = hi serve as heartbeats, letting
    #     followers know that the leader is still alive

    #     To synchronize a follower's log with the leader's,
    #     the leader identifies the latest matching log entry
    #     (same PrevLogIndex and PrevLogTerm), removes entries in the follower's
    #     log beyond that point, and transmits all subsequent leader entries.

    #     '''
    #     prefix_len = request.PrefixLen
    #     suffix = request.Suffix

    #     # Process the log replication
    #     # Here you would typically send the log entries to the follower node
        
    #     acked_length = prefix_len + len(suffix)

    #     return raft_pb2.LogReply(AckedLength=acked_length)




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
        '''
        Cater to the text : deliver msg to the application 
        '''
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

def serve(starterID,node_id, peers):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    raftNode_pb2_grpc.add_RaftNodeServiceServicer_to_server(RaftNode(node_id, peers), server)
    node_address = f'{os.getenv(f"NODE_{starterID}_IP")}:{os.getenv(f"NODE_{starterID}_PORT")}'    
    server.add_insecure_port(node_address)
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    starterID = int(sys.argv[1])

    num_nodes = int(os.getenv("NUM_NODES"))
    
    node_ID = os.getenv(f"NODE_{starterID}_ID")

    peers = {}
    for i in range(1, num_nodes+1):
        if i != starterID:
            index = str(i)
            key = os.getenv(f'NODE_{index}_ID')
            value = f'{os.getenv(f"NODE_{index}_IP")}:{os.getenv(f"NODE_{index}_PORT")}'
            peers[key] = value

    print(peers)
    serve(starterID,node_ID, peers)
