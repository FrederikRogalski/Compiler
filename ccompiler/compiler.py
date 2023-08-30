from copy import deepcopy
from ccompiler.tokens import Token
from ccompiler.optim import OrOptimizer, AndOptimizer
from ccompiler.parsers import Source, Parser, TokenParser, OrParser, ConstantParser


INT = TokenParser(Token.INT)
FLOAT = TokenParser(Token.FLOAT)
PLUS = TokenParser(Token.PLUS)
MINUS = TokenParser(Token.MINUS)
STAR = TokenParser(Token.STAR)
SLASH = TokenParser(Token.SLASH)
PERCENT = TokenParser(Token.PERCENT)
IDENTIFIER = TokenParser(Token.IDENTIFIER)
DOT = TokenParser(Token.DOT)
EQUALS = TokenParser(Token.EQUALS)
LPAREN = TokenParser(Token.LPAREN)
RPAREN = TokenParser(Token.RPAREN)
LBRACKET = TokenParser(Token.LBRACKET)
RBRACKET = TokenParser(Token.RBRACKET)
LBRACE = TokenParser(Token.LBRACE)
RBRACE = TokenParser(Token.RBRACE)
COMMA = TokenParser(Token.COMMA)
COLON = TokenParser(Token.COLON)
SEMICOLON = TokenParser(Token.SEMICOLON)
INTEGER = TokenParser(Token.INTEGER)
INCREMENT = TokenParser(Token.INCREMENT)
DECREMENT = TokenParser(Token.DECREMENT)
RETURN = TokenParser(Token.RETURN)


# Empty parsers for recursive reference - to be filled later
expression = OrParser()
factor = OrParser()
term = OrParser()

# ---------- TOKEN UNIONS
binary_operator = PLUS | MINUS | STAR | SLASH | PERCENT
binary_operator.name = "BINOP"
unary_operator = PLUS | MINUS
unary_operator.name = "UNOP"
type_identifier = INT | FLOAT
type_identifier.name = "TYPE"

# ---------- EXPRESSIONS
factor.parsers = (IDENTIFIER | INTEGER | (LPAREN & expression & RPAREN) | (unary_operator & factor)).parsers
factor.name = "FACT"
binary_operation_l1 = factor & (STAR | SLASH | PERCENT) & term
binary_operation_l1.name = "BINOP_L1"
term.parsers = (binary_operation_l1 | factor).parsers
term.name = "TERM"
binary_operation_l2 = term & (PLUS | MINUS) & expression
binary_operation_l2.name = "BINOP_L2"
expression.parsers = (binary_operation_l2 | term).parsers
expression.name = "EXP"

# save for tests
unoptimized_expression = deepcopy(expression)

# ---------- SIMPLE STATEMENTS
assignment = IDENTIFIER & EQUALS & expression
assignment.name = "ASSIGN"
definition = type_identifier & (assignment | IDENTIFIER)
definition.name = "DEF"
return_statement = RETURN & expression
return_statement.name = "RTRN_STMT"

statement_body = definition | assignment | return_statement | expression
statement_body.name = "STMT_BODY"
statement = (statement_body & SEMICOLON) | SEMICOLON
statement.name = "STATEMENT"


block = LBRACE & statement.many() & RBRACE
block.name = "BLOCK"
parameter_list = ((definition & COMMA).many() & definition) | ConstantParser([])
parameter_list.name = "PARAMS"
function = type_identifier & IDENTIFIER & LPAREN & parameter_list & RPAREN & block
function.name = "FUNC"

top = (function | statement).many()
top.name = "TOP"

OrOptimizer.optimize(top)
AndOptimizer.optimize(top)

def main():
    import sys
    import argparse
    from pprint import pprint
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--string", type=str)
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("input", nargs="?", type=argparse.FileType("r"), default=sys.stdin)
    args = parser.parse_args()
    assert args.input or args.string, "Either input file or string must be provided"
    input_is_stdin = args.input is sys.stdin
    assert not (args.string and args.input and not input_is_stdin), "Cannot provide both input file and string"
    
    if args.verbose:
        import ccompiler.debug as debug
        debug.init(Parser, Source)
    
    source = Source(args.string or args.input.read())
    pprint(top.parse(source))

if __name__ == "__main__":
    main()