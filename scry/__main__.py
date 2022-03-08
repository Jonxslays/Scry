import sys

from scry.errors import ScryExc
from scry.lexer import Lexer
from scry.parser import Parser


def main() -> None:
    if sys.argv[1:]:
        file = sys.argv[1]
    else:
        raise Exception("You must pass a filepath to run.")

    lexer = Lexer(file)
    lexer.lex()

    parser = Parser()
    parser.parse(lexer.tokens)


if __name__ == "__main__":
    try:
        main()
    except ScryExc as e:
        sys.stderr.write(f"ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        raise
