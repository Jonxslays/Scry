from __future__ import annotations

import enum
import typing as t
from dataclasses import dataclass


KEYWORDS = (
    "push",     # Push a variable or literal onto the stack (stack1)
    "add",      # Add top 2 elements on the stack (stack1 = stack1 + stack2)
    "sub",      # Subtract top 2 elements on the stack (stack1 = stack1 - stack2)
    "print",    # Pass a variable to print, pops and prints the top of stack by default
    "pop",      # Pop 1 from the stack into a declared variable
    "move",     # Move a value into a declared variable
    "mul",      # Multiply the top 2 elements on the stack (stack1 = stack1 * stack2)
    "div",      # Divide the top 2 elements on the stack (stack1 = stack1 / stack2)
    "fdiv",     # Floor divide the top 2 elements on the stack (stack1 = stack1 // stack2)
    "pow",      # Exponentiate the top 2 elements on the stack (stack1 = stack1 ** stack2)
    "new",      # Create a new variable, requires a type and name
    "//",       # Floor divide
    "in",       # TODO: implement me
    "if",       # TODO: implement me
    "loop",     # TODO: implement me
    "for",      # TODO: implement me
    "end",      # TODO: implement me
    "start",    # TODO: implement me
    "funk",     # TODO: implement me - maybe?
)


class TokenType(enum.Enum):
    PUSH = 0
    ADD = 1
    SUB = 2
    PRINT = 3
    POP = 4
    MOVE = 5
    TYPE = 6
    VALUE = 7
    MUL = 8
    DIV = 9
    POW = 10
    IDENT = 11
    NEW = 12
    FDIV = 13


@dataclass
class Token:
    token_type: TokenType
    value: t.Any = None
