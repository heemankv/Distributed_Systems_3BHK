# For Creating the gRPC files for raftClient.proto

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. raftClient.proto
```


