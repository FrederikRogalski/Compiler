from abc import abstractmethod, ABC
from copy import deepcopy
from numbers import Number
from collections import OrderedDict
from dataclasses import dataclass
from ccompiler.tokens import Token
from ccompiler.util import Visitor, Visitable
from ccompiler.optim import OrOptimizer, AndOptimizer
from ccompiler.parsers import Source, Parser, TokenParser, OrParser


class Program(ABC):
    header: list[str]
    code: list[str]
    text: list[str]
    local_vars: list[OrderedDict[str, int]]
    max_offset_sp: int
    depth: int
    
    def __init__(self):
        self._depth
        self.variables = [OrderedDict()]
        self.code = []
        self.text = []
        self.max_offset_sp = 0
    
    @property
    def depth(self):
        return self._depth
    
    @depth.setter
    def depth(self, value):
        assert value >= 0, "Indent cannot be negative"
        if value > self._depth:
            self.variables += [OrderedDict() for _ in range(value - self._depth)]
        elif value < self._depth:
            self.variables = self.variables[:value]
        self._depth = value
    
    def create_local_var(self, identifier: str, size: int = 8) -> int:
        """address is offset from stack pointer"""
        assert identifier not in self.variables[self.depth],\
            f"Redefinition of variable {identifier}"
        # variable offset from sp is last variable offset from sp + size
        self.variables[self.depth][identifier] = \
            self.variables[self._depth][next(reversed(self.variables[self._depth]))] + size
        self.max_offset_sp = max(self.variables[self.depth][identifier], self.max_offset_sp)
        return self.variables[self.depth][identifier]
    
    def get_local_var(self, identifier: str):
        for scope in reversed(self.variables[:self.depth]):
            if identifier in scope:
                return scope[identifier]
        raise Exception(f"Variable {identifier} not found")
    
    @abstractmethod
    def __str__(self): pass

class Arm64Program(Program):
    def __init__(self):
        super().__init__()
        self.header = [
            ".globl _main",
            ".p2align 2"
        ]
    
    def __str__(self):
        return "\n".join(self.header + self.code + self.text)

class AstNode(ABC):
    def emit(self, program: Program): pass

@dataclass
class Top(AstNode):
    body: list
    def emit(self, program: Program):
        inner = self.body.emit(program)
        return [
            "_main:",
            f"sub sp, sp, #{program.max_offset_sp}",
            *inner
        ]
        

@dataclass
class Variable(AstNode):
    identifier: str
    
@dataclass
class Immidiate(AstNode):
    type_identifier: Token
    value: Number
@dataclass
class Function(AstNode):
    return_type: Token
    identifier: str
    parameter_list: list
    body: list

@dataclass
class EmptyStatement(AstNode):
    pass

@dataclass
class Expression(AstNode):
    pass

@dataclass
class UnaryOp(AstNode):
    operator: Token
    expression: Expression

@dataclass
class BinaryOp(AstNode):
    left: Expression
    operator: Token
    right: Expression

@dataclass
class Return(AstNode):
    expression: Expression

@dataclass
class Assignment(AstNode):
    identifier: str
    expression: Expression

@dataclass
class Definition(AstNode):
    type_identifier: Token
    identifier: str
    expression: Expression = None


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

# ---------- TOKEN UNIONS
binary_operator = PLUS | MINUS | STAR | SLASH | PERCENT
binary_operator.name = "BINOP"
unary_operator = PLUS | MINUS
unary_operator.name = "UNOP"
type_identifier = (INT | FLOAT).bind(lambda x: x[0])
type_identifier.name = "TYPE"

# ---------- EXPRESSIONS
variable = IDENTIFIER.bind(lambda x: Variable(x[1]))
immidiate = (FLOAT | INTEGER).bind(lambda x: Immidiate(*x))
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
assignment = (IDENTIFIER & EQUALS & expression).bind(lambda x: Assignment(x[0][1], x[2]))
assignment.name = "ASSIGN"
def extract_definition(x):
    if isinstance(x[1], Assignment):
        return Definition(x[0], x[1].identifier, x[1].expression)
    return Definition(*x)
definition = (type_identifier & (assignment | IDENTIFIER)).bind(extract_definition)
definition.name = "DEF"
return_statement = (RETURN & expression).bind(lambda x: Return(x[1]))
return_statement.name = "RTRN_STMT"

statement_body = definition | assignment | return_statement | expression
statement_body.name = "STMT_BODY"
statement = (statement_body & SEMICOLON).bind(lambda x: x[0]) | SEMICOLON.bind(lambda _: EmptyStatement())
statement.name = "STATEMENT"


block = LBRACE & statement.many() & RBRACE
block.name = "BLOCK"
parameter = (type_identifier & IDENTIFIER).bind(lambda x: [x[0], x[1][1]])
parameter.name = "PARAM"
def extract_parameter_list(x: list):
    if len(x) == 0: return x
    return [x[0], *map(lambda a: a[1],x[1])]
parameter_list = (parameter & (COMMA & parameter).many()).default([]).bind(extract_parameter_list)
parameter_list.name = "PARAMS"
function = (type_identifier & IDENTIFIER & LPAREN & parameter_list & RPAREN & block).bind(lambda x: Function(x[0], x[1], x[3], x[-2]))
function.name = "FUNC"

top = (function | statement).many().bind(lambda x: Top(x))
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
    provided_string = args.string is not None
    assert args.input or provided_string, "Either input file or string must be provided"
    input_is_stdin = args.input is sys.stdin
    assert not (provided_string and args.input and not input_is_stdin), "Cannot provide both input file and string"
    
    if args.verbose:
        import ccompiler.debug as debug
        debug.init(Parser, Source)
    
    source = Source(args.string if provided_string else args.input.read())
    pprint(top.parse(source))

if __name__ == "__main__":
    main()