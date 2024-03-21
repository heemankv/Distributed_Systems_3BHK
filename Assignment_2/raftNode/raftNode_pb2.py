# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: raftNode.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0eraftNode.proto\x12\x08raftNode\"b\n\x12RequestVoteRequest\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x13\n\x0b\x63\x61ndidateId\x18\x02 \x01(\x05\x12\x14\n\x0clastLogIndex\x18\x03 \x01(\x05\x12\x13\n\x0blastLogTerm\x18\x04 \x01(\x05\"8\n\x13RequestVoteResponse\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x13\n\x0bvoteGranted\x18\x02 \x01(\x08\"\x9c\x01\n\x14\x41ppendEntriesRequest\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x10\n\x08leaderId\x18\x02 \x01(\x05\x12\x14\n\x0cprevLogIndex\x18\x03 \x01(\x05\x12\x13\n\x0bprevLogTerm\x18\x04 \x01(\x05\x12#\n\x07\x65ntries\x18\x05 \x03(\x0b\x32\x12.raftNode.LogEntry\x12\x14\n\x0cleaderCommit\x18\x06 \x01(\x05\"6\n\x15\x41ppendEntriesResponse\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x0f\n\x07success\x18\x02 \x01(\x08\")\n\x08LogEntry\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x0f\n\x07\x63ommand\x18\x02 \x01(\t\"\"\n\x0fServeClientArgs\x12\x0f\n\x07request\x18\x01 \x01(\t\"J\n\x17ServeClientSuccessReply\x12\x0c\n\x04\x64\x61ta\x18\x01 \x01(\t\x12\x10\n\x08leaderId\x18\x02 \x01(\t\x12\x0f\n\x07success\x18\x03 \x01(\x08\"<\n\x17ServeClientFailureReply\x12\x10\n\x08leaderId\x18\x02 \x01(\t\x12\x0f\n\x07success\x18\x03 \x01(\x08\"\x94\x01\n\x13ServeClientResponse\x12\x39\n\x0csuccessReply\x18\x01 \x01(\x0b\x32!.raftNode.ServeClientSuccessReplyH\x00\x12\x39\n\x0c\x66\x61ilureReply\x18\x02 \x01(\x0b\x32!.raftNode.ServeClientFailureReplyH\x00\x42\x07\n\x05reply2\xfe\x01\n\x0fRaftNodeService\x12L\n\x0bRequestVote\x12\x1c.raftNode.RequestVoteRequest\x1a\x1d.raftNode.RequestVoteResponse\"\x00\x12R\n\rAppendEntries\x12\x1e.raftNode.AppendEntriesRequest\x1a\x1f.raftNode.AppendEntriesResponse\"\x00\x12I\n\x0bServeClient\x12\x19.raftNode.ServeClientArgs\x1a\x1d.raftNode.ServeClientResponse\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'raftNode_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_REQUESTVOTEREQUEST']._serialized_start=28
  _globals['_REQUESTVOTEREQUEST']._serialized_end=126
  _globals['_REQUESTVOTERESPONSE']._serialized_start=128
  _globals['_REQUESTVOTERESPONSE']._serialized_end=184
  _globals['_APPENDENTRIESREQUEST']._serialized_start=187
  _globals['_APPENDENTRIESREQUEST']._serialized_end=343
  _globals['_APPENDENTRIESRESPONSE']._serialized_start=345
  _globals['_APPENDENTRIESRESPONSE']._serialized_end=399
  _globals['_LOGENTRY']._serialized_start=401
  _globals['_LOGENTRY']._serialized_end=442
  _globals['_SERVECLIENTARGS']._serialized_start=444
  _globals['_SERVECLIENTARGS']._serialized_end=478
  _globals['_SERVECLIENTSUCCESSREPLY']._serialized_start=480
  _globals['_SERVECLIENTSUCCESSREPLY']._serialized_end=554
  _globals['_SERVECLIENTFAILUREREPLY']._serialized_start=556
  _globals['_SERVECLIENTFAILUREREPLY']._serialized_end=616
  _globals['_SERVECLIENTRESPONSE']._serialized_start=619
  _globals['_SERVECLIENTRESPONSE']._serialized_end=767
  _globals['_RAFTNODESERVICE']._serialized_start=770
  _globals['_RAFTNODESERVICE']._serialized_end=1024
# @@protoc_insertion_point(module_scope)