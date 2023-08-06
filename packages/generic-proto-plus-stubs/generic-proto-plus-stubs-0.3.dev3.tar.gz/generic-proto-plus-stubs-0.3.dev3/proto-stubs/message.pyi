import typing as t

from google.protobuf import descriptor_pb2, message
from proto.fields import Field

from proto.marshal import Marshal

MessageType = t.TypeVar('MessageType', bound='Message')


class MessageMeta(type):
    def __new__(mcls, name, bases, attrs): ...

    @classmethod
    def __prepare__(mcls, name, bases, **kwargs): ...

    @property
    def meta(cls): ...

    @t.overload
    def pb(cls, obj: None = ..., *, coerce: bool = ...) -> t.Type[message.Message]: ...

    @t.overload
    def pb(cls, obj: t.Any = ..., *, coerce: bool = ...) -> message.Message: ...

    def pb(cls, obj: t.Any | None = ..., *, coerce: bool = ...) -> message.Message: ...

    def wrap(cls, pb): ...

    def serialize(cls, instance) -> bytes: ...

    def deserialize(cls: t.Type[MessageType], payload: bytes) -> MessageType: ...

    def to_json(
            cls,
            instance,
            *,
            use_integers_for_enums: bool = ...,
            including_default_value_fields: bool = ...,
            preserving_proto_field_name: bool = ...
    ) -> str: ...

    def from_json(cls: t.Type[MessageType],
                  payload,
                  *,
                  ignore_unknown_fields: bool = ...) -> MessageType: ...

    def to_dict(
            cls: t.Type[MessageType],
            instance,
            *,
            use_integers_for_enums: bool = ...,
            preserving_proto_field_name: bool = ...
    ) -> t.Dict[str, t.Any]: ...

    def copy_from(cls, instance, other) -> None: ...


class Message(metaclass=MessageMeta):
    def __init__(
            self, mapping: t.Any | None = None, *, ignore_unknown_fields: bool = False, **kwargs
    ) -> None: ...

    def __bool__(self) -> bool: ...

    def __contains__(self, key) -> bool: ...

    def __delattr__(self, key) -> None: ...

    def __eq__(self, other) -> bool: ...

    def __getattr__(self, key): ...

    def __ne__(self, other) -> bool: ...

    def __setattr__(self, key, value) -> None: ...


class _MessageInfo:
    package: t.Any
    full_name: t.Any
    options: t.Any
    fields: t.Any
    fields_by_number: t.Any
    marshal: t.Any

    def __init__(
            self,
            fields: t.List[Field],
            package: str,
            full_name: str,
            marshal: Marshal,
            options: descriptor_pb2.MessageOptions,
    ) -> None: ...

    @property
    def pb(self) -> t.Type[message.Message]: ...
