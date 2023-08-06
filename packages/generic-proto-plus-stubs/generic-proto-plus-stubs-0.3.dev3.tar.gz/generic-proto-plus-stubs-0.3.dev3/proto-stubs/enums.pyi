import enum
from typing import Any

from proto.marshal.rules.enums import EnumRule as EnumRule

class ProtoEnumMeta(enum.EnumMeta):
    def __new__(mcls, name, bases, attrs): ...

class Enum(enum.IntEnum, metaclass=ProtoEnumMeta): ...

class _EnumInfo:
    full_name: Any
    pb: Any
    def __init__(self, full_name: str, pb) -> None: ...
