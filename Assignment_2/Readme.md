# For Creating the gRPC files for raftClient.proto

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. raftClient.proto
```

# For Creating the gRPC files for raftNode.proto

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. raftNode.proto
```


<!-- TODOs -->

<!-- Broacasting message -->
<!-- When leader sends NoOp, followers are not appending that to it's log -->

<!-- Failure of Replicate log -->
<!-- Call replicate log again with reduced set length in a while loop this it actually works -->
<!-- Solved -->