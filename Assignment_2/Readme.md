# For Creating the gRPC files for raftClient.proto

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. raftClient.proto
```

# For Creating the gRPC files for raftNode.proto

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. raftNode.proto
```
