from __future__ import annotations
import typing as t

from google.protobuf import descriptor_pb2
from proto.primitives import T_enum, T_MESSAGE
from proto.message import Message as ProtoMessage


class Field(t.Generic[T_enum]):
    repeated: bool
    mcls_data: t.Any
    parent: t.Any
    number: t.Any
    proto_type: T_enum
    message: t.Any
    enum: t.Any
    json_name: t.Any
    optional: t.Any
    oneof: t.Any

    @t.overload
    def __init__(
            self: Field[T_enum],
            proto_type: T_enum,
            number: int,
            *,
            message: t.Any | None = ...,
            enum: t.Any | None = ...,
            oneof: str = ...,
            json_name: str = ...,
            optional: bool = ...
    ) -> None: ...

    @t.overload
    def __init__(
            self: Field[T_MESSAGE],
            proto_type: t.Type[ProtoMessage],
            number: int,
            *,
            message: t.Any | None = ...,
            enum: t.Any | None = ...,
            oneof: str = ...,
            json_name: str = ...,
            optional: bool = ...
    ) -> None: ...

    @property
    def descriptor(self) -> descriptor_pb2.FieldDescriptorProto: ...

    @property
    def name(self) -> str: ...

    @property
    def package(self) -> str: ...

    @property
    def pb_type(self): ...


class RepeatedField(Field):
    repeated: bool


class MapField(Field):
    map_key_type: t.Any

    def __init__(
            self,
            key_type,
            value_type,
            number: int,
            *,
            message: t.Any | None = ...,
            enum: t.Any | None = ...
    ) -> None: ...
