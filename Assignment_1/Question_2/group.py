import zmq
import datetime
import sys
import uuid
from dotenv import load_dotenv
import os
import socket
hostname = socket.gethostname()
IP_ADDR = socket.gethostbyname(hostname)

# Load environment variables from .env file
load_dotenv()
 
MESSAGE_SERVER_IP=os.getenv("MESSAGE_SERVER_IP")

class Group:
    def __init__(self, name, ip):
        self.name=name
        self.ip=ip
        self.users=[]
        self.messages=[]
        self.context=zmq.Context()
        
        #Reply Socket
        self.rep_socket = self.context.socket(zmq.REP)
        self.rep_socket.bind(f"tcp://{ip}")

        #Request Socket
        self.req_socket=self.context.socket(zmq.REQ)
        self.req_socket.connect("tcp://"+MESSAGE_SERVER_IP)
        print("GROUP ID: "+name)
        print("IP: "+ip)
        print("GROUP SERVER IS READY")

    def handle_requests(self):
       
            while True:
                try:
                    message = self.rep_socket.recv_json()
                    
                    if message['action'] == 'join_group':
                        if message['user'] not in self.users:
                            self.users.append(message['user'])
                        print("JOIN REQUEST FROM "+message['user'])
                        self.rep_socket.send_json({'status': 'SUCCESS'})

                    elif message['action'] == 'leave_group':
                        self.users.remove(message['user'])
                        print("LEAVE REQUEST FROM "+message['user'])
                        self.rep_socket.send_json({'status': 'SUCCESS'})

                    elif message['action'] == 'send_message':
                        user = message['user']
                        print("MESSAGE SEND FROM "+user)
                        if user in self.users:
                            content = message['content']
                            self.messages.append({'sender': user, 'content': content,"timestamp": datetime.datetime.now() })
                            self.rep_socket.send_json({"status": "SUCCESS"})
                        else:
                            self.rep_socket.send_json({"status":"FAILURE"})

                    elif message['action'] == 'get_messages':
                        user=message['user']
                        print("MESSAGE REQUEST FROM "+ message['user'])
                        if user in self.users: 
                            
                            if message['timestamp']:
                                timestamp = datetime.datetime.strptime(message["timestamp"], "%m/%d/%Y, %H:%M:%S")
                                filtered_msgs = [{"sender":msg['sender'],"content":msg['content'],"timestamp":msg['timestamp'].strftime("%m/%d/%Y, %H:%M:%S")} for msg in self.messages if msg['timestamp'] >= timestamp]
                            else:
                                filtered_msgs = [{"sender":msg['sender'],"content":msg['content'],"timestamp":msg['timestamp'].strftime("%m/%d/%Y, %H:%M:%S")} for msg in self.messages]
                            self.rep_socket.send_json({"status": "SUCCESS", "messages":filtered_msgs})
                        else:
                            self.rep_socket.send_json({"status":"FAILURE"})
                    else:
                        self.rep_socket.send_json({"status":"FAILURE IN ACTION"})
                
                except Exception as e:
                    print(e)
                    self.rep_socket.send_json({"status":"FAILURE"})
    
    
    def register_group(self):
        self.req_socket.send_json({'action': 'register_group','name':self.name,'ip':self.ip})
        print("REGISTER GROUP REQUEST SENT")
        try:
            response=self.req_socket.recv_json()
            print(response['status'])
        except Exception as e:
            print(e)
            sys.exit(1)

groupid=str(uuid.uuid4())
group = Group(groupid, IP_ADDR+":"+sys.argv[1])
group.register_group()
group.handle_requests()

