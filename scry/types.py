from __future__ import annotations

import typing as t
from dataclasses import dataclass
from enum import Enum


class Type(Enum):
    INT = 0
    STRING = 1
    BOOL = 2


@dataclass
class Variable:
    name: str
    type: t.Any
    line: int
    value: t.Any = None
