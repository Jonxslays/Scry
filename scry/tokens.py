from __future__ import annotations

import enum
import typing as t
from dataclasses import dataclass


class TokenType(enum.Enum):
    PUSH = 0
    ADD = 1
    SUB = 2
    PRINT = 3
    POP = 4
    MOVE = 5
    TYPE = 6
    VALUE = 7


@dataclass
class Token:
    token_type: TokenType
    value: t.Any = None
