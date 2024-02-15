from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class NotifyRequest(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class NotifyResponse(_message.Message):
    __slots__ = ("status",)
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SUCCESS: _ClassVar[NotifyResponse.Status]
        FAIL: _ClassVar[NotifyResponse.Status]
    SUCCESS: NotifyResponse.Status
    FAIL: NotifyResponse.Status
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: NotifyResponse.Status
    def __init__(self, status: _Optional[_Union[NotifyResponse.Status, str]] = ...) -> None: ...
