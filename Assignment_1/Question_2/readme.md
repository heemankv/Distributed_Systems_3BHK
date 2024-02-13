## Steps to run: 
1) Run the message_server.py file. COMMAND: python message_server.py
2) Change the ip address of the message server in the env file
3) Run the group.py file in another machine. COMMAND: python group.py PORT_NO
4) RUn the user.py file in another machine. COMMAND: python user.py PORT_NO

## Modifications to run in gcp:
1) Enter the External IP of the message_server in the env file.
2) Message_Server will use its own INTERNAL IP in its code to connect.
3) Enter the External IP of groups from user side whenever connecting user to group.
4) Group will use its own INTERNAL_IP in its code to connect.

#### Assumptions:
1) Port used for MESSAGE_SERVER: 3000
2) All servers are in same timezone
