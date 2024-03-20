# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: raft.proto
# Protobuf Python Version: 4.25.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nraft.proto\x12\x04raft\"b\n\x12RequestVoteRequest\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x13\n\x0b\x63\x61ndidateId\x18\x02 \x01(\x05\x12\x14\n\x0clastLogIndex\x18\x03 \x01(\x05\x12\x13\n\x0blastLogTerm\x18\x04 \x01(\x05\"8\n\x13RequestVoteResponse\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x13\n\x0bvoteGranted\x18\x02 \x01(\x08\"\x98\x01\n\x14\x41ppendEntriesRequest\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x10\n\x08leaderId\x18\x02 \x01(\x05\x12\x14\n\x0cprevLogIndex\x18\x03 \x01(\x05\x12\x13\n\x0bprevLogTerm\x18\x04 \x01(\x05\x12\x1f\n\x07\x65ntries\x18\x05 \x03(\x0b\x32\x0e.raft.LogEntry\x12\x14\n\x0cleaderCommit\x18\x06 \x01(\x05\"6\n\x15\x41ppendEntriesResponse\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x0f\n\x07success\x18\x02 \x01(\x08\")\n\x08LogEntry\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x0f\n\x07\x63ommand\x18\x02 \x01(\t\"\"\n\x0fServeClientArgs\x12\x0f\n\x07request\x18\x01 \x01(\t\"C\n\x10ServeClientReply\x12\x0c\n\x04\x64\x61ta\x18\x01 \x01(\t\x12\x10\n\x08leaderId\x18\x02 \x01(\t\x12\x0f\n\x07success\x18\x03 \x01(\x08\x32\xdf\x01\n\x0bRaftService\x12\x44\n\x0bRequestVote\x12\x18.raft.RequestVoteRequest\x1a\x19.raft.RequestVoteResponse\"\x00\x12J\n\rAppendEntries\x12\x1a.raft.AppendEntriesRequest\x1a\x1b.raft.AppendEntriesResponse\"\x00\x12>\n\x0bServeClient\x12\x15.raft.ServeClientArgs\x1a\x16.raft.ServeClientReply\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'raft_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_REQUESTVOTEREQUEST']._serialized_start=20
  _globals['_REQUESTVOTEREQUEST']._serialized_end=118
  _globals['_REQUESTVOTERESPONSE']._serialized_start=120
  _globals['_REQUESTVOTERESPONSE']._serialized_end=176
  _globals['_APPENDENTRIESREQUEST']._serialized_start=179
  _globals['_APPENDENTRIESREQUEST']._serialized_end=331
  _globals['_APPENDENTRIESRESPONSE']._serialized_start=333
  _globals['_APPENDENTRIESRESPONSE']._serialized_end=387
  _globals['_LOGENTRY']._serialized_start=389
  _globals['_LOGENTRY']._serialized_end=430
  _globals['_SERVECLIENTARGS']._serialized_start=432
  _globals['_SERVECLIENTARGS']._serialized_end=466
  _globals['_SERVECLIENTREPLY']._serialized_start=468
  _globals['_SERVECLIENTREPLY']._serialized_end=535
  _globals['_RAFTSERVICE']._serialized_start=538
  _globals['_RAFTSERVICE']._serialized_end=761
# @@protoc_insertion_point(module_scope)
