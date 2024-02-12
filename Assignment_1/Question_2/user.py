import zmq
import uuid
import sys
from dotenv import load_dotenv
import os
import socket
hostname = socket.gethostname()
IP_ADDR = socket.gethostbyname(hostname)
# Load environment variables from .env file
load_dotenv()
 
MESSAGE_SERVER_IP=os.getenv("MESSAGE_SERVER_IP")

class User:
    def __init__(self, name,ip):
        self.name=name
        self.ip=ip
        self.context=zmq.Context()
        self.groups=[]
        
        #Message Server Socket
        self.server_socket = self.context.socket(zmq.REQ)
        self.server_socket.connect("tcp://"+MESSAGE_SERVER_IP)

        self.group_socket=self.context.socket(zmq.REQ)

        print("USER ID: "+name)
        print("IP: "+ip)
        print("USER IS READY")
    
    def get_group_list(self):
        
        try:
            self.server_socket.send_json({'action': 'get_group_list','user':self.name,'ip':self.ip})
            response=self.server_socket.recv_json()
            print(response['status'])
            groups=response['groups']
            for group in groups:
                print(group+" - "+groups[group])
        except Exception as e:
            print(e)
    
    def join_group(self, groupIP):
        
        try:
            self.group_socket.connect("tcp://"+groupIP)
            self.group_socket.send_json({'action': 'join_group','user':self.name})
            response=self.group_socket.recv_json()
            print(response['status'])
            if(response['status']=="SUCCESS"):
                self.groups.append(groupIP)
            self.group_socket.disconnect("tcp://"+groupIP)
        except Exception as e:
            print(e)
        
            
        

    def leave_group(self, groupIP):      
        try:
            self.group_socket.connect("tcp://"+groupIP)
            self.group_socket.send_json({'action': 'leave_group','user':self.name})
            response=self.group_socket.recv_json()
            print(response['status'])
            if(response['status']=="SUCCESS"):
                self.groups.remove(groupIP)
            self.group_socket.disconnect("tcp://"+groupIP)

        except Exception as e:
            print(e)
           
    
    def get_messages(self, groupIP,timestamp_str=None):
        try:
            self.group_socket.connect("tcp://"+groupIP)
            self.group_socket.send_json({"action": "get_messages","user":self.name,"timestamp": timestamp_str})
            response=self.group_socket.recv_json()
            print(response['status'])
            if response['status']=="SUCCESS":
                messages = response["messages"]
                if (len(messages)==0):
                    print("No Message")
                for msg in messages:
                    print(msg['sender']+" "+msg["content"]+" "+msg["timestamp"])

        except Exception as e:
            print(e)

    def send_message(self,groupIP,msg):
 
        try:
            self.group_socket.connect("tcp://"+groupIP)
            self.group_socket.send_json({'action': 'send_message','user':self.name,'content':msg})
            response=self.group_socket.recv_json()
            print(response['status'])
            self.group_socket.disconnect("tcp://"+groupIP)
        except Exception as e:
            print(e)
           
    def handleInputs(self):
        while True:
            print("""
Press 1 for sending a message
Press 2 for getting messages from a group
Press 3 for leaving a group
Press 4 for joining a group
Press 5 for getting a list of groups from Main Server
Press 6 to End
""")
            a=input()
            if a=="1":
                print("Here are the groups you are part of: ")
                print(self.groups)
                groupip=input("Enter group ip (Enter NA to exit):")
                if(groupip=="NA"):
                    continue
                msg=input('Enter the message you want to send : ')
                self.send_message(groupip,msg)
            elif a=="2":
                print("Here are the groups you are part of: ")
                print(self.groups)
                groupip=input("Enter group ip (Enter NA to exit):")
                if(groupip=="NA"):
                    continue
                timestamp=input("Enter timestamp in the format %m/%d/%Y, %H:%M:%S (LEAVE EMPTY FOR NO TIMESTAMP): ")
                if(timestamp or timestamp=="NA"):
                    self.get_messages(groupip, timestamp)
                else:
                    self.get_messages(groupip)
            elif a=="3":
                print("Here are the groups you are part of: ")
                print(self.groups)
                groupip=input("Enter group ip (Enter NA to exit):")
                if(groupip=="NA"):
                    continue
                self.leave_group(groupip)
            elif a=="4":
                groupip=input("Enter group ip (Enter NA to exit):")
                if(groupip=="NA"):
                    continue
                self.join_group(groupip)
            elif a=="5":
                self.get_group_list()
            elif a=="6":
                break
            else:
                print("Enter Correct Input")

user=User(str(uuid.uuid4()),IP_ADDR+":"+sys.argv[1])
user.handleInputs()