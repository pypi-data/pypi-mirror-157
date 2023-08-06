from __future__ import annotations
import abc
import typing as t


class Rule(abc.ABC):
    @classmethod
    def __subclasshook__(cls, C): ...


class BaseMarshal:
    def __init__(self) -> None: ...

    def register(self, proto_type: type, rule: Rule = ...): ...

    def reset(self) -> None: ...

    def to_python(self, proto_type, value, *, absent: bool = ...): ...

    def to_proto(self, proto_type, value, *, strict: bool = ...): ...


_T_Marshal = t.TypeVar('_T_Marshal', bound=Marshal)


class Marshal(BaseMarshal):
    def __new__(cls: _T_Marshal, name: str) -> _T_Marshal: ...

    def __init__(self, name: str) -> None: ...


class NoopRule:
    def to_python(self, pb_value, *, absent: bool = ...): ...

    def to_proto(self, value): ...
