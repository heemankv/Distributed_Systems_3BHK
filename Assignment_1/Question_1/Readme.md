### Command to generate protos file :
run inside pythonfolder
python3 -m grpc_tools.protoc -I ../protos --python_out=. --pyi_out=. --grpc_python_out=. ../protos/buyer.proto 

Proto banao, voh python code banaega using the above mentioned command, and use the generated code to create the server and client.

# Relevant Links : 
https://grpc.io/docs/languages/python/quickstart/
https://protobuf.dev/getting-started/pythontutorial/
https://grpc.io/docs/what-is-grpc/introduction/
https://protobuf.dev/overview/


TODO: Fix issue of Category being shown as a number, rather it's equivalent string value.

# seller updates Items, buyers gets notified
