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
        with open(self._file) as f:
            for line in f:
                line = line.lstrip()

                if not line:
                    continue

                self.lex_next_token(line)

        # # For debugging
        # from pprint import pprint
        # pprint(self.tokens)

    def lex_with_type(self, line: str) -> list[Token]:
        data = [l.lstrip() for l in line.split(" ", maxsplit=1)]

        if len(data) == 1:
            return [Token(token_type=TokenType.IDENT, value=data[0])]

        type_, value = data

        if type_.lower() == "int":
            return [
                Token(TokenType.TYPE, value=Type.INT),
                Token(TokenType.VALUE, value=value),
            ]

        if type_.lower() == "bool":
            return [
                Token(TokenType.TYPE, value=Type.BOOL),
                Token(TokenType.VALUE, value=value),
            ]

        if type_.lower() == "string":
            return [
                Token(TokenType.TYPE, value=Type.STRING),
                Token(TokenType.VALUE, value=value),
            ]

        raise SyntaxError(f"Invalid type: {line}")

    def lex_new_var(self, line: str) -> None:
        data = self.lex_with_type(line)
        self._tokens.append(data.pop(0))
        self._tokens.append(Token(TokenType.IDENT, value=data.pop(0).value))

    def lex_next_token(self, line: str) -> None:
        if line.lower().startswith("push"):
            raw_value = line[4:].lstrip().rstrip("\n")
            self._tokens.append(Token(TokenType.PUSH))
            return self._tokens.extend(self.lex_with_type(raw_value))

        if line.lower().startswith("add"):
            return self._tokens.append(Token(TokenType.ADD))

        if line.lower().startswith("sub"):
            return self._tokens.append(Token(TokenType.SUB))

        if line.lower().startswith("mul"):
            return self._tokens.append(Token(TokenType.MUL))

        if line.lower().startswith("div"):
            return self._tokens.append(Token(TokenType.DIV))

        if line.lower().startswith("fdiv"):
            return self._tokens.append(Token(TokenType.FDIV))

        if line.lower().startswith("pow"):
            return self._tokens.append(Token(TokenType.POW))

        if line.lower().startswith("pop"):
            value = line[3:].lstrip().rstrip("\n")
            self._tokens.append(Token(TokenType.POP))
            return self._tokens.append(Token(TokenType.IDENT, value=value))

        if line.lower().startswith("new"):
            value = line[3:].lstrip(" ").rstrip("\n")
            self._tokens.append(Token(TokenType.NEW))
            return self.lex_new_var(value)

        if line.lower().startswith("move"):
            value = line[4:].lstrip().rstrip("\n")
            ident, data = value.split(" ", maxsplit=1)
            self._tokens.append(Token(TokenType.MOVE))
            self._tokens.append(Token(TokenType.IDENT, value=ident))
            return self._tokens.append(Token(TokenType.VALUE, value=data.lstrip()))

        if line.lower().startswith("print"):
            self._tokens.append(Token(TokenType.PRINT))

            if not line.lower().rstrip("\n").endswith("print"):
                value = line[5:].lstrip().rstrip("\n")
                self._tokens[-1].value = TokenType.IDENT
                self._tokens.append(Token(TokenType.IDENT, value=value))

            return None

        raise SyntaxError(f"Invalid syntax:\n{line}")
