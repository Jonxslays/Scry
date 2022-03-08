from __future__ import annotations

import re
import typing as t

from scry.tokens import KEYWORDS, Token, TokenType
from scry.types import Type, Variable


class Parser:
    def __init__(self) -> None:
        self._stack: list[t.Any] = []
        self._state: dict[str, Variable] = {}

    def convert_value_to_type(self, type_token: Token, value_token: Token) -> t.Any:
        if type_token.value in (Type.INT, Type.UINT):
            if "." in value_token.value:
                raise ValueError(
                    "Value incompatible with type, line "
                    f"{value_token.line} -> {value_token.value!r}"
                )

            converted = int(type_token.value)

            if type_token.value is Type.UINT and converted < 0:
                raise ValueError(
                    "Unsigned int can not be negative, line "
                    f"{type_token.line} -> {value_token.value!r}"
                )

            return converted

        if type_token.value in (Type.FLOAT, Type.UFLOAT):
            converted = float(value_token.value)

            if type_token.value is Type.UFLOAT and converted < 0:
                raise ValueError(
                    "Unsigned float can not be negative, line "
                    f"{type_token.line} -> {value_token.value!r}"
                )

            return converted

        if type_token.value is Type.BOOL:
            string = value_token.value.lower()

            if string == "true":
                return True

            if string == "false":
                return False

            raise SyntaxError(
                "Invalid boolean value, line " f"{type_token.line} -> {string!r}"
            )

        if type_token.value is Type.STRING:
            new_string: str = value_token.value

            if not new_string.startswith('"'):
                raise SyntaxError(f'Missing opening `"`, line {type_token.line}')

            if not new_string.endswith('"'):
                raise SyntaxError(f'Missing closing `"`, line {type_token.line}')

            var_regex = re.compile(r"\$\{(.*)\}")
            var_matches = var_regex.findall(new_string)

            for match in var_matches:
                if match not in self._state:
                    raise SyntaxError(
                        f"Unknown symbol, line {type_token.line} -> {match!r}"
                    )

                replacement = self._state[match].value
                new_string = new_string.replace(
                    "${" + match + "}",
                    replacement if isinstance(replacement, str) else str(replacement),
                )

            return new_string[1:-1]

        raise Exception(f"Failed to parse types, line {type_token.line}")

    def get_op_func(
        self, line: int, op: TokenType, a: t.Any, b: t.Any
    ) -> t.Callable[[], t.Any]:
        if op is TokenType.ADD:
            return lambda: a + b

        elif op is TokenType.SUB:
            return lambda: a - b

        elif op is TokenType.MUL:
            return lambda: a * b

        elif op is TokenType.DIV:
            return lambda: a / b

        elif op is TokenType.FDIV:
            return lambda: a // b

        elif op is TokenType.POW:
            return lambda: a**b

        raise SyntaxError(f"Invalid basic op, line {line}")

    def perform_basic_op(self, op: TokenType, line: int) -> None:
        try:
            a = self._stack.pop()
            b = self._stack.pop()
        except IndexError:
            raise RuntimeError(f"Not enough data on the stack, line {line} ")

        if isinstance(a, bool) or isinstance(b, bool):
            raise RuntimeError(f"Cannot perform basic ops on bools, line {line}")

        op_func = self.get_op_func(line, op, a, b)

        try:
            self._stack.append(op_func())
        except TypeError:
            return self._stack.append(str(a) + str(b))

    def parse(self, tokens: list[Token]) -> None:
        while len(tokens) > 0:
            token = tokens.pop(0)

            if token.token_type is TokenType.PUSH:
                next_token = tokens.pop(0)

                if next_token.token_type is TokenType.IDENT:
                    if next_token.value not in self._state:
                        raise RuntimeError(
                            f"Unknown variable, line {token.line}"
                            f" -> {next_token.value!r}"
                        )

                    self._stack.append(self._state[next_token.value].value)

                else:
                    self._stack.append(
                        self.convert_value_to_type(next_token, tokens.pop(0))
                    )

            elif token.token_type is TokenType.PUSHD:
                next_token = tokens.pop(0)

                if next_token.token_type is TokenType.IDENT:
                    popped = self._state.pop(next_token.value, None)

                    if popped is None:
                        raise RuntimeError(
                            f"Unknown variable, line {token.line}"
                            f" -> {next_token.value!r}"
                        )

                    self._stack.append(popped.value)

                else:
                    self._stack.append(
                        self.convert_value_to_type(next_token, tokens.pop(0))
                    )

            elif token.token_type is TokenType.DROP:
                ident_token = tokens.pop(0)

                if ident_token.token_type is not TokenType.IDENT:
                    raise RuntimeError(
                        f"Invalid token after drop, line {token.line}"
                        f" -> {ident_token.value!r}"
                    )

                popped = self._state.pop(ident_token.value, None)
                if popped is None:
                    raise RuntimeError(
                        f"Unknown variable, line {token.line}"
                        f" -> {ident_token.value!r}"
                    )

            elif token.token_type is TokenType.POP:
                if not self._stack:
                    raise RuntimeError(
                        f"Not enough data on the stack, line {token.line}"
                    )

                ident_token = tokens.pop(0)
                if ident_token.token_type is TokenType.DROP:
                    self._stack.pop()
                    continue

                if ident_token.token_type is not TokenType.IDENT:
                    raise RuntimeError(
                        f"Invalid token after pop, line {token.line}"
                        f" -> {ident_token.value!r}"
                    )

                if ident_token.value not in self._state:
                    if ident_token.value is None:
                        raise RuntimeError(
                            f"Missing token after pop, line {token.line}"
                        )

                    raise RuntimeError(
                        f"Unknown variable, line {token.line}"
                        f" -> {ident_token.value!r}"
                    )

                popped = self._stack.pop()
                self._state[ident_token.value] = Variable(
                    ident_token.value, type(popped), ident_token.line, popped
                )

            elif token.token_type in (
                TokenType.ADD,
                TokenType.SUB,
                TokenType.POW,
                TokenType.MUL,
                TokenType.DIV,
                TokenType.FDIV,
            ):
                self.perform_basic_op(token.token_type, token.line)

            elif token.token_type is TokenType.VAR:
                type_token = tokens.pop(0)
                ident_token = tokens.pop(0)
                variable_type: type

                if (
                    type_token.token_type is not TokenType.TYPE
                    or ident_token.token_type is not TokenType.IDENT
                ):
                    raise SyntaxError(
                        f"Invalid syntax, line {token.line} "
                        f"-> var must be followed by type and then name"
                    )

                if ident_token.value.lower() in KEYWORDS:
                    raise SyntaxError(
                        f"Reserved keyword, line {token.line} -> {ident_token.value!r}"
                    )

                if any(
                    delim in ident_token.value
                    for delim in (" ", "(", ")", "{", "}", "[", "]")
                ):
                    raise SyntaxError(
                        f"Bad variable name, line {token.line} -> "
                        f"{ident_token.value!r} can not contain spaces but does"
                    )

                if type_token.value is Type.INT:
                    variable_type = int
                elif type_token.value is Type.BOOL:
                    variable_type = bool
                elif type_token.value is Type.STRING:
                    variable_type = str
                else:
                    raise SyntaxError(
                        f"Unknown type, line {token.line}" f" -> {type_token.value!r}"
                    )

                if ident_token.value in self._state:
                    raise RuntimeError(
                        f"Cannot redefine, line {token.line} "
                        f"-> {ident_token.value!r} is already defined"
                    )

                variable = Variable(ident_token.value, variable_type, ident_token.line)
                self._state[variable.name] = variable

            elif token.token_type is TokenType.MOVE:
                ident_token = tokens.pop(0)
                value_token = tokens.pop(0)

                if (
                    ident_token.token_type is not TokenType.IDENT
                    or value_token.token_type is not TokenType.VALUE
                ):
                    raise SyntaxError(
                        f"Syntax error, line {token.line} -> "
                        "move requires a variable and a value to move"
                    )

                if ident_token.value not in self._state:
                    raise RuntimeError(
                        f"Unknown variable, line {ident_token.line} "
                        f"-> {ident_token.value!r}"
                    )

                variable = self._state[ident_token.value]

                if variable.type is str:
                    variable.value = self.convert_value_to_type(
                        Token(
                            TokenType.TYPE,
                            line=ident_token.line,
                            value=Type.STRING,
                        ),
                        value_token,
                    )

                else:
                    variable.value = variable.type(value_token.value)

            elif token.token_type is TokenType.PRINT:
                if token.value is TokenType.IDENT:
                    next_token = tokens.pop(0)

                    if next_token.value not in self._state:
                        raise RuntimeError(
                            f"Unknown variable, line {token.line} -> "
                            f"{next_token.value!r} is an unknown variable"
                        )

                    target = self._state[next_token.value].value

                else:
                    if not self._stack:
                        raise RuntimeError(
                            f"Failed to print, line {token.line} "
                            "-> Not enough data on the stack"
                        )

                    target = self._stack.pop()

                print(target)

            elif token.token_type is TokenType.EOF:
                if self._stack:
                    raise RuntimeError(
                        f"Unhandled data on the stack, line {token.line} "
                        f"-> {len(self._stack)} items"
                    )

                if self._state:
                    raise RuntimeError(
                        "Variables not dropped: %s"
                        % ", ".join(
                            f"line {v.line} -> {v.name!r}" for v in self._state.values()
                        )
                    )

            else:
                raise RuntimeError(f"Error parsing token, line {token.line} -> {token}")
