from typing import Any

from .enums import Enum as Enum
from .fields import Field as Field, MapField as MapField, RepeatedField as RepeatedField
from .marshal import Marshal as Marshal
from .message import Message as Message
from .modules import define_module as module

DOUBLE: Any
FLOAT: Any
INT64: Any
UINT64: Any
INT32: Any
FIXED64: Any
FIXED32: Any
BOOL: Any
STRING: Any
MESSAGE: Any
BYTES: Any
UINT32: Any
ENUM: Any
SFIXED32: Any
SFIXED64: Any
SINT32: Any
SINT64: Any
