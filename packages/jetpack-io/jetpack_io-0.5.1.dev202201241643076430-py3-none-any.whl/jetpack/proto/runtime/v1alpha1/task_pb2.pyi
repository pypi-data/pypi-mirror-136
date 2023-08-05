"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""
import builtins
import google.protobuf.descriptor
import google.protobuf.internal.enum_type_wrapper
import google.protobuf.message
import jetpack.proto.runtime.v1alpha1.remote_pb2
import typing
import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor = ...

class PersistedTask(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor = ...
    class Status(_Status, metaclass=_StatusEnumTypeWrapper):
        pass
    class _Status:
        V = typing.NewType('V', builtins.int)
    class _StatusEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_Status.V], builtins.type):
        DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor = ...
        UNKNOWN = PersistedTask.Status.V(0)
        CREATED = PersistedTask.Status.V(1)
        WAITING = PersistedTask.Status.V(2)
        READY = PersistedTask.Status.V(3)
        RUNNING = PersistedTask.Status.V(4)
        SUCCEEDED = PersistedTask.Status.V(5)
        CANCELLING = PersistedTask.Status.V(6)
        CANCELLED = PersistedTask.Status.V(7)
        FAILING = PersistedTask.Status.V(8)
        FAILED = PersistedTask.Status.V(9)

    UNKNOWN = PersistedTask.Status.V(0)
    CREATED = PersistedTask.Status.V(1)
    WAITING = PersistedTask.Status.V(2)
    READY = PersistedTask.Status.V(3)
    RUNNING = PersistedTask.Status.V(4)
    SUCCEEDED = PersistedTask.Status.V(5)
    CANCELLING = PersistedTask.Status.V(6)
    CANCELLED = PersistedTask.Status.V(7)
    FAILING = PersistedTask.Status.V(8)
    FAILED = PersistedTask.Status.V(9)

    ID_FIELD_NUMBER: builtins.int
    QUALIFIED_SYMBOL_FIELD_NUMBER: builtins.int
    ENCODED_ARGS_FIELD_NUMBER: builtins.int
    MANIFEST_FIELD_NUMBER: builtins.int
    STATUS_FIELD_NUMBER: builtins.int
    RESULT_FIELD_NUMBER: builtins.int
    id: typing.Text = ...
    qualified_symbol: typing.Text = ...
    encoded_args: builtins.bytes = ...
    # sdk version? to build command?
    # or just store the command?
    manifest: builtins.bytes = ...
    status: global___PersistedTask.Status.V = ...
    @property
    def result(self) -> jetpack.proto.runtime.v1alpha1.remote_pb2.Result: ...
    def __init__(self,
        *,
        id : typing.Text = ...,
        qualified_symbol : typing.Text = ...,
        encoded_args : builtins.bytes = ...,
        manifest : builtins.bytes = ...,
        status : global___PersistedTask.Status.V = ...,
        result : typing.Optional[jetpack.proto.runtime.v1alpha1.remote_pb2.Result] = ...,
        ) -> None: ...
    def HasField(self, field_name: typing_extensions.Literal[u"result",b"result"]) -> builtins.bool: ...
    def ClearField(self, field_name: typing_extensions.Literal[u"encoded_args",b"encoded_args",u"id",b"id",u"manifest",b"manifest",u"qualified_symbol",b"qualified_symbol",u"result",b"result",u"status",b"status"]) -> None: ...
global___PersistedTask = PersistedTask
