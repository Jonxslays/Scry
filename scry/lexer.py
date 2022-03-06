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
                self.get_next_token(line)

    def get_next_token(self, line: str) -> None:
        if line.lower().startswith("push"):
            raw_value = line[4:].lstrip().rstrip("\n")
            self._tokens.append(Token(TokenType.PUSH))
            return self.get_next_token(raw_value)

        if line.lower().startswith("add"):
            return self._tokens.append(Token(TokenType.ADD))

        if line.lower().startswith("sub"):
            return self._tokens.append(Token(TokenType.SUB))

        if line.lower().startswith("pop"):
            value = line[3:].lstrip().rstrip("\n")
            return self._tokens.append(Token(TokenType.POP, value=value))

        if line.lower().startswith("move"):
            raise NotImplementedError("move instruction is not yet implemented")
            # value = line[4:].lstrip().rstrip("\n")
            # return self._tokens.append(Token(TokenType.MOVE, value=value))

        if line.lower().startswith("print"):
            return self._tokens.append(Token(TokenType.PRINT))

        if line.lower().startswith("int"):
            value = line[3:].lstrip().rstrip("\n")
            self._tokens.append(Token(TokenType.TYPE, value=Type.INT))
            return self._tokens.append(Token(TokenType.VALUE, value=value))

        if line.lower().startswith("bool"):
            value = line[4:].lstrip().rstrip("\n")
            self._tokens.append(Token(TokenType.TYPE, value=Type.BOOL))
            return self._tokens.append(Token(TokenType.VALUE, value=value))

        if line.lower().startswith("string"):
            value = line[6:].lstrip().rstrip("\n")
            self._tokens.append(Token(TokenType.TYPE, value=Type.STRING))
            return self._tokens.append(Token(TokenType.VALUE, value=value))

        raise SyntaxError(f"Invalid syntax:\n{line}")
