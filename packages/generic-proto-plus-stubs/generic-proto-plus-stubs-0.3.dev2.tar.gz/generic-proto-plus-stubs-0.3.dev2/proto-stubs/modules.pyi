from typing import NamedTuple, Set
from proto import Marshal


class _ProtoModule(NamedTuple):
    package: str
    marshal: Marshal
    manifest: Set[str]

def define_module(
    package: str, *, marshal: str = ..., manifest: Set[str] = ...
) -> _ProtoModule: ...
