import os
from copy import deepcopy
from ccompiler.tokens import Token
from ccompiler.optim import OrOptimizer, AndOptimizer
from ccompiler.parsers import Source, Parser, TokenParser, OrParser, BindParser
from ccompiler.ast import BinaryOp, UnaryOp, Immidiate, Variable, Assignment, Definition, Return, EmptyStatement, Top, Function, Parameter, Block, Integer, Float, Arm64Program, Scope





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

# TODO: Come up with a better way then bind for the creation of AST nodes. Bind destroys optimization.

# Empty parsers for recursive reference - to be filled later
expression = OrParser()
factor = OrParser()
term = OrParser()
block = BindParser(None, None)

# ---------- TOKEN UNIONS
binary_operator = PLUS | MINUS | STAR | SLASH | PERCENT
binary_operator.name = "BINOP"
unary_operator = PLUS | MINUS
unary_operator.name = "UNOP"

_type_conversion = {Token.INT: Integer, Token.FLOAT: Float}
_type = (INT | FLOAT).bind(lambda x: _type_conversion[x[0]])
_type.name = "TYPE"
identifier = IDENTIFIER.bind(lambda x: x[1])

# ---------- EXPRESSIONS
variable = identifier.bind(lambda x: Variable(x))
_immidiate_conversion = {Token.INTEGER: Integer, Token.FLOAT: Float}
immidiate = (INTEGER).bind(lambda x: Immidiate(_immidiate_conversion[x[0]], x[1]))
factor.parsers = (variable | immidiate | (LPAREN & expression & RPAREN).bind(lambda x: x[1]) | (unary_operator & factor).bind(lambda x: UnaryOp(x[0][0], x[1]))).parsers
factor.name = "FACT"
binary_operation_l1 = (factor & (STAR | SLASH | PERCENT) & term).bind(lambda x: BinaryOp(x[0], x[1][0], x[2]))
binary_operation_l1.name = "BINOP_L1"
term.parsers = (binary_operation_l1 | factor).parsers
term.name = "TERM"
binary_operation_l2 = (term & (PLUS | MINUS) & expression).bind(lambda x: BinaryOp(x[0], x[1][0], x[2]))
binary_operation_l2.name = "BINOP_L2"
expression.parsers = (binary_operation_l2 | term).parsers
expression.name = "EXP"

# save for tests
unoptimized_expression = deepcopy(expression)

# ---------- SIMPLE STATEMENTS
assignment = (identifier & EQUALS & expression).bind(lambda x: Assignment(x[0], x[2]))
assignment.name = "ASSIGN"
def extract_definition(x):
    if isinstance(x[1], Assignment):
        return Definition(x[0], x[1].identifier, x[1].expression)
    return Definition(*x)
definition = (_type & (assignment | IDENTIFIER)).bind(extract_definition)
definition.name = "DEF"
return_statement = (RETURN & expression).bind(lambda x: Return(x[1]))
return_statement.name = "RTRN_STMT"

statement_body = definition | assignment | return_statement | expression
statement_body.name = "STMT_BODY"
statement = (statement_body & SEMICOLON).bind(lambda x: x[0]) | SEMICOLON.bind(lambda _: EmptyStatement())
statement.name = "STATEMENT"


_tmp = (LBRACE & (statement | block).many() & RBRACE).bind(lambda x: Block(x[1]))
block.parsers = _tmp.parsers
block.callback = _tmp.callback
block.name = "BLOCK"
parameter = (_type & identifier).bind(lambda x: Parameter(*x))
parameter.name = "PARAM"
def extract_parameter_list(x: list):
    if len(x) == 0: return x
    return [x[0], *map(lambda a: a[1],x[1])]
parameter_list = (parameter & (COMMA & parameter).many()).default([]).bind(extract_parameter_list)
parameter_list.name = "PARAMS"
function = (_type & identifier & LPAREN & parameter_list & RPAREN & block).bind(lambda x: Function(x[0], x[1], x[3], x[-1]))
function.name = "FUNC"

top = (function | statement).many().bind(lambda x: Top(Block(x)))
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
    # required
    parser.add_argument("-o", "--output", type=argparse.FileType("w"), required=True)
    parser.add_argument("input", nargs="?", type=argparse.FileType("r"), default=sys.stdin)
    args = parser.parse_args()
    provided_string = args.string is not None
    assert args.input or provided_string, "Either input file or string must be provided"
    input_is_stdin = args.input is sys.stdin
    assert not (provided_string and args.input and not input_is_stdin), "Cannot provide both input file and string"
    
    if args.verbose:
        import ccompiler.debug as debug
        debug.init(Parser, Source)
    
    source = Source(args.string if provided_string else args.input.read())
    ast = top.parse(source)
    pprint(ast)
    program = str(Arm64Program.build(ast))
    with open(f"{args.output.name}.s", "w") as f:
        f.write(program)
    # now assemble with as
    os.system(f"as {args.output.name}.s -o {args.output.name}.o")
    # now link with ld
    os.system(f"ld {args.output.name}.o -o {args.output.name} -lSystem -syslibroot /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk")
    
    

if __name__ == "__main__":
    main()