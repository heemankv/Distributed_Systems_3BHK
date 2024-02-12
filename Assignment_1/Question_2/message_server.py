import zmq
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
 
MESSAGE_SERVER_IP=os.getenv("MESSAGE_SERVER_IP")

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://"+MESSAGE_SERVER_IP)

groups={} #stores registered groups


print("Socket Ready")
while True:
    message = socket.recv_json()

    try:
        if message['action'] == "register_group":
            group_name=message["name"]
            group_ip=message["ip"]
            groups[group_name]=group_ip
            print("JOIN REQUEST FROM "+group_ip)
            socket.send_json({'status': 'SUCCESS'})
        
        elif message['action'] == "get_group_list":
            user_ip=message["ip"]
            print("GROUP LIST REQUEST FROM "+ user_ip)
            socket.send_json({"status":"SUCCESS","groups": groups})
            print("SUCCESS")

        else:
            print("INVALID ACTION")
            socket.send_json({'status': 'INVALID ACTION FAILURE'})



    except Exception:
        socket.send_json({'status': 'FAILURE'})



