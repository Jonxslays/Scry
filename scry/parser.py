from __future__ import annotations

import typing as t

from scry.tokens import Token, TokenType
from scry.types import Type


class Parser:
    def __init__(self) -> None:
        self._stack: list[t.Any] = []
        self._state: dict[str, t.Any] = {}

    def parse_type(self, type_token: Token, value_token: Token) -> t.Any:
        if type_token.value is Type.INT:
            return int(value_token.value)

        if type_token.value is Type.BOOL:
            string = value_token.value.lower()

            if string == "true":
                return True

            if string == "false":
                return False

            raise SyntaxError("Invalid boolean value")

        if type_token.value is Type.STRING:
            return value_token.value

        raise Exception("Something went wrong parsing types")

    def parse(self, tokens: list[Token]) -> None:
        while len(tokens) > 0:
            token = tokens.pop(0)

            if token.token_type is TokenType.PUSH:
                self._stack.append(self.parse_type(tokens.pop(0), tokens.pop(0)))

            elif token.token_type is TokenType.ADD:
                if len(self._stack) < 2:
                    raise RuntimeError("Not enough data on the stack add")

                a = self._stack.pop()
                b = self._stack.pop()

                if type(a) != type(b):
                    self._stack.append(str(a) + str(b))
                else:
                    self._stack.append(a + b)

            elif token.token_type is TokenType.SUB:
                if len(self._stack) < 2:
                    raise RuntimeError("Not enough data on the stack sub")

                self._stack.append(self._stack.pop() - self._stack.pop())

            elif token.token_type is TokenType.POP:
                if not self._stack:
                    raise RuntimeError("Not enough data on the stack to print")

                self._state[token.value] = self._stack.pop()

            elif token.token_type is TokenType.PRINT:
                if not self._stack:
                    raise RuntimeError("Not enough data on the stack to print")

                print(self._stack.pop())

            else:
                raise RuntimeError(f"Error parsing token {token}")
