from __future__ import annotations

from pathlib import Path

from scry.tokens import Token, TokenType
from scry.types import Type


class Lexer:
    def __init__(self, file: str | Path) -> None:
        self._file = Path(file) if isinstance(file, str) else file
        self._tokens: list[Token] = []

    @property
    def tokens(self) -> list[Token]:
        return self._tokens

    def lex(self) -> None:
        last_line = 0

        with open(self._file) as f:
            for i, line in enumerate(f):
                line = line.lstrip()
                last_line = i + 1

                if not line:
                    continue

                self.lex_next_token(last_line, line)

        self._tokens.append(Token(TokenType.EOF, line=last_line))

        # # For debugging
        # from pprint import pprint
        # pprint(self.tokens)

    def lex_with_type(self, line_num: int, line: str) -> list[Token]:
        data = [l.lstrip() for l in line.split(" ", maxsplit=1)]

        if len(data) == 1:
            return [Token(TokenType.IDENT, line=line_num, value=data[0])]

        type_, value = data

        if type_.lower() == "int":
            return [
                Token(TokenType.TYPE, line=line_num, value=Type.INT),
                Token(TokenType.VALUE, line=line_num, value=value),
            ]

        if type_.lower() == "uint":
            return [
                Token(TokenType.TYPE, line=line_num, value=Type.UINT),
                Token(TokenType.VALUE, line=line_num, value=value),
            ]

        if type_.lower() == "float":
            return [
                Token(TokenType.TYPE, line=line_num, value=Type.FLOAT),
                Token(TokenType.VALUE, line=line_num, value=value),
            ]

        if type_.lower() == "ufloat":
            return [
                Token(TokenType.TYPE, line=line_num, value=Type.UFLOAT),
                Token(TokenType.VALUE, line=line_num, value=value),
            ]

        if type_.lower() == "bool":
            return [
                Token(TokenType.TYPE, line=line_num, value=Type.BOOL),
                Token(TokenType.VALUE, line=line_num, value=value),
            ]

        if type_.lower() == "string":
            return [
                Token(TokenType.TYPE, line=line_num, value=Type.STRING),
                Token(TokenType.VALUE, line=line_num, value=value),
            ]

        raise SyntaxError(f"Invalid type, line {line_num} -> {line}")

    def lex_new_var(self, line_num: int, line: str) -> None:
        data = self.lex_with_type(line_num, line)
        self._tokens.append(data.pop(0))
        self._tokens.append(
            Token(TokenType.IDENT, line=line_num, value=data.pop(0).value)
        )

    def lex_next_token(self, line_num: int, line: str) -> None:
        if line.lower().startswith("pushd"):
            raw_value = line[5:].lstrip().rstrip("\n")
            self._tokens.append(Token(TokenType.PUSHD, line=line_num))
            return self._tokens.extend(self.lex_with_type(line_num, raw_value))

        if line.lower().startswith("push"):
            raw_value = line[4:].lstrip().rstrip("\n")
            self._tokens.append(Token(TokenType.PUSH, line=line_num))
            self._tokens.extend(self.lex_with_type(line_num, raw_value))
            return

        if line.lower().startswith("add"):
            return self._tokens.append(Token(TokenType.ADD, line=line_num))

        if line.lower().startswith("sub"):
            return self._tokens.append(Token(TokenType.SUB, line=line_num))

        if line.lower().startswith("mul"):
            return self._tokens.append(Token(TokenType.MUL, line=line_num))

        if line.lower().startswith("div"):
            return self._tokens.append(Token(TokenType.DIV, line=line_num))

        if line.lower().startswith("fdiv"):
            return self._tokens.append(Token(TokenType.FDIV, line=line_num))

        if line.lower().startswith("pow"):
            return self._tokens.append(Token(TokenType.POW, line=line_num))

        if line.lower().startswith("pop"):
            value = line[3:].lstrip().rstrip("\n")
            self._tokens.append(Token(TokenType.POP, line=line_num))

            if value == "drop":
                return self._tokens.append(Token(TokenType.DROP, line=line_num))

            return self._tokens.append(
                Token(
                    TokenType.IDENT, line=line_num, value=None if value == "" else value
                )
            )

        if line.lower().startswith("drop"):
            value = line[4:].lstrip().rstrip("\n")
            self._tokens.append(Token(TokenType.DROP, line=line_num))
            return self._tokens.append(
                Token(TokenType.IDENT, line=line_num, value=value)
            )

        if line.lower().startswith("var"):
            value = line[3:].lstrip(" ").rstrip("\n")
            self._tokens.append(Token(TokenType.VAR, line=line_num))
            return self.lex_new_var(line_num, value)

        if line.lower().startswith("move"):
            value = line[4:].lstrip().rstrip("\n")

            try:
                ident, data = value.split(" ", maxsplit=1)
            except ValueError:
                raise SyntaxError(
                    f"Invalid syntax, line {line_num} -> "
                    "move requires a variable and a value to move"
                )

            if ident.isdigit():
                raise SyntaxError(
                    f"Invalid syntax, line {line_num} -> "
                    "variables can not contain only numbers"
                )

            self._tokens.append(Token(TokenType.MOVE, line=line_num))
            self._tokens.append(Token(TokenType.IDENT, line=line_num, value=ident))

            return self._tokens.append(
                Token(TokenType.VALUE, line=line_num, value=data.lstrip())
            )

        if line.lower().startswith("print"):
            self._tokens.append(Token(TokenType.PRINT, line=line_num))

            if not line.lower().rstrip("\n").endswith("print"):
                value = line[5:].lstrip().rstrip("\n")
                self._tokens[-1].value = TokenType.IDENT
                self._tokens.append(Token(TokenType.IDENT, line=line_num, value=value))

            return None

        raise SyntaxError(f"Invalid syntax, line {line_num} -> {line}")
