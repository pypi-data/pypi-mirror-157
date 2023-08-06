import enum
from typing import Literal, TypeVar


class ProtoType(enum.IntEnum):
    DOUBLE: int
    FLOAT: int
    INT64: int
    UINT64: int
    INT32: int
    FIXED64: int
    FIXED32: int
    BOOL: int
    STRING: int
    MESSAGE: int
    BYTES: int
    UINT32: int
    ENUM: int
    SFIXED32: int
    SFIXED64: int
    SINT32: int
    SINT64: int


T_DOUBLE = Literal[ProtoType.DOUBLE]
T_FLOAT = Literal[ProtoType.FLOAT]
T_INT64 = Literal[ProtoType.INT64]
T_UINT64 = Literal[ProtoType.UINT64]
T_INT32 = Literal[ProtoType.INT32]
T_FIXED64 = Literal[ProtoType.FIXED64]
T_FIXED32 = Literal[ProtoType.FIXED32]
T_BOOL = Literal[ProtoType.BOOL]
T_STRING = Literal[ProtoType.STRING]
T_MESSAGE = Literal[ProtoType.MESSAGE]
T_BYTES = Literal[ProtoType.BYTES]
T_UINT32 = Literal[ProtoType.UINT32]
T_ENUM = Literal[ProtoType.ENUM]
T_SFIXED32 = Literal[ProtoType.SFIXED32]
T_SFIXED64 = Literal[ProtoType.SFIXED64]
T_SINT32 = Literal[ProtoType.SINT32]
T_SINT64 = Literal[ProtoType.SINT64]

T_enum = TypeVar(
    'T_enum',
    T_DOUBLE,
    T_FLOAT,
    T_INT64,
    T_UINT64,
    T_INT32,
    T_FIXED64,
    T_FIXED32,
    T_BOOL,
    T_STRING,
    T_MESSAGE,
    T_BYTES,
    T_UINT32,
    T_ENUM,
    T_SFIXED32,
    T_SFIXED64,
    T_SINT32,
    T_SINT64,
)
