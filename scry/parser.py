from __future__ import annotations

import typing as t

from scry.tokens import KEYWORDS, Token, TokenType
from scry.types import Type, Variable


class Parser:
    def __init__(self) -> None:
        self._stack: list[t.Any] = []
        self._state: dict[str, Variable] = {}

    def convert_value_to_type(self, type_token: Token, value_token: Token) -> t.Any:
        if type_token.value is Type.INT:
            if "." in value_token.value:
                return float(value_token.value)

            return int(value_token.value)

        if type_token.value is Type.BOOL:
            string = value_token.value.lower()

            if string == "true":
                return True

            if string == "false":
                return False

            raise SyntaxError("Invalid boolean value")

        if type_token.value is Type.STRING:
            new_string: str = value_token.value

            if not new_string.startswith('"'):
                raise SyntaxError(
                    "String declared, but no \" present to begin the string"
                )

            if not new_string.endswith("\""):
                raise SyntaxError(
                    "String declared, but no \" present to end the string"
                )

            return value_token.value[1:-1]

        raise Exception("Something went wrong parsing types")

    def perform_basic_op(self, op: TokenType) -> None:
        can_be_string = False

        if op is TokenType.ADD:
            error_op = "add"
            can_be_string = True
        elif op is TokenType.SUB:
            error_op = "sub"
        elif op is TokenType.MUL:
            error_op = "mul"
        elif op is TokenType.DIV:
            error_op = "div"
        elif op is TokenType.POW:
            error_op = "pow"
        else:
            raise RuntimeError("Got invalid basic operation")

        if len(self._stack) < 2:
            raise RuntimeError(f"Not enough data on the stack to {error_op!r}")

        a = self._stack.pop()
        b = self._stack.pop()

        if isinstance(a, bool) or isinstance(b, bool):
            raise RuntimeError("Cannot perform basic operations on bools")

        if not can_be_string:
            if isinstance(a, str) or isinstance(b, str):
                raise RuntimeError(f"Cannot perform {error_op!r} on a string")

        if any(isinstance(item, str) for item in (a, b)):
            a = str(a)
            b = str(b)

        if op is TokenType.ADD:
            self._stack.append(a + b)
            return None

        assert not isinstance(a, str) and not isinstance(b, str)

        if op is TokenType.SUB:
            self._stack.append(a - b)
        elif op is TokenType.MUL:
            self._stack.append(a * b)
        elif op is TokenType.DIV:
            self._stack.append(a / b)
        elif op is TokenType.POW:
            self._stack.append(a ** b)

    def parse(self, tokens: list[Token]) -> None:
        while len(tokens) > 0:
            token = tokens.pop(0)

            if token.token_type is TokenType.PUSH:
                next_token = tokens.pop(0)

                if next_token.token_type is TokenType.IDENT:
                    if next_token.value not in self._state:
                        raise RuntimeError(
                            f"Cannot push into unknown variable {next_token.value!r}"
                        )

                    self._stack.append(self._state[next_token.value].value)

                else:
                    self._stack.append(
                        self.convert_value_to_type(next_token, tokens.pop(0))
                    )

            elif token.token_type in (
                TokenType.ADD,
                TokenType.SUB,
                TokenType.POW,
                TokenType.MUL,
                TokenType.DIV,
            ):
                self.perform_basic_op(token.token_type)

            elif token.token_type is TokenType.NEW:
                type_token = tokens.pop(0)
                ident_token = tokens.pop(0)

                if (
                    type_token.token_type is not TokenType.TYPE
                    or ident_token.token_type is not TokenType.IDENT
                ):
                    raise SyntaxError(
                        "You must provide a type and identifier after the new keyword"
                    )

                if ident_token.value.lower() in KEYWORDS:
                    raise SyntaxError(f"{ident_token.value!r} is a reserved keyword")

                if type_token.value is Type.INT:
                    variable_type = int
                elif type_token.value is Type.BOOL:
                    variable_type = bool
                elif type_token.value is Type.STRING:
                    variable_type = str
                else:
                    raise SyntaxError(f"Unknown type {type_token.value!r}")

                if ident_token.value in self._state:
                    raise RuntimeError(f"{ident_token.value!r} is already defined")

                variable = Variable(ident_token.value, variable_type)
                self._state[variable.name] = variable

            elif token.token_type is TokenType.MOVE:
                ident_token = tokens.pop(0)
                value_token = tokens.pop(0)

                if (
                    ident_token.token_type is not TokenType.IDENT
                    or value_token.token_type is not TokenType.VALUE
                ):
                    raise SyntaxError("Move must be followed by an identifier and a value")

                if ident_token.value not in self._state:
                    raise RuntimeError(f"Cannot move into unknown variable {ident_token.value!r}")

                variable = self._state[ident_token.value]
                variable.value = variable.type(value_token.value)

            elif token.token_type is TokenType.POP:
                if not self._stack:
                    raise RuntimeError("Not enough data on the stack to pop")

                ident = tokens.pop(0)
                if ident.token_type is not TokenType.IDENT:
                    raise RuntimeError(f"{ident.value!r} is an invalid token after pop")

                if ident.value not in self._state:
                    raise RuntimeError(f"Cannot pop into unknown variable {ident.value!r}")

                if " " in ident.value:
                    raise SyntaxError("Identifiers can not contain spaces")

                popped = self._stack.pop()
                self._state[ident.value] = Variable(ident.value, type(popped), popped)

            elif token.token_type is TokenType.PRINT:
                if token.value is TokenType.IDENT:
                    next_token = tokens.pop(0)

                    if next_token.value not in self._state:
                            raise RuntimeError(f"{next_token.value} is an unknown variable")

                    target = self._state[next_token.value].value

                else:
                    if not self._stack:
                        raise RuntimeError("Not enough data on the stack to print")

                    target = self._stack.pop()

                print(target)

            else:
                raise RuntimeError(f"Error parsing token {token}")
