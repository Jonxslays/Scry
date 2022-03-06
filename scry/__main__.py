import sys

from scry.lexer import Lexer
from scry.parser import Parser

if sys.argv[1:]:
    file = sys.argv[1]
else:
    raise Exception("You must pass a filepath to run.")

lexer = Lexer(file)
lexer.lex()

parser = Parser()
parser.parse(lexer.tokens)
