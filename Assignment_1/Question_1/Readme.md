### Command to generate python grpc  file :
run this inside python folder
- python3 -m grpc_tools.protoc -I ../protos --python_out=. --pyi_out=. --grpc_python_out=. ../protos/buyer.proto 
- python3 -m grpc_tools.protoc -I ../protos --python_out=. --pyi_out=. --grpc_python_out=. ../protos/market.proto 
- python3 -m grpc_tools.protoc -I ../protos --python_out=. --pyi_out=. --grpc_python_out=. ../protos/seller.proto 

### Command to run the server :
- Change the IP inside the .env file
- then run this inside python folder
- python3 Market.py -> runs on port 50051
- python3 Seller.py {Port}
- python3 Buyer.py {Port}

# Relevant Links : 
- https://grpc.io/docs/languages/python/quickstart/
- https://protobuf.dev/getting-started/pythontutorial/
- https://grpc.io/docs/what-is-grpc/introduction/
- https://protobuf.dev/overview/
