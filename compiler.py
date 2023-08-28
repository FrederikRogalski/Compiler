import re
import argparse
from copy import deepcopy
from tokens import Token
from abc import ABC, abstractmethod, abstractproperty

class Source:
    source: str
    offset: int
    def __init__(self, source: str, offset=0):
        self.source = source
        self.offset = offset
    def __repr__(self):
        return f"Source({repr(self.source)}, {self.offset})"

class Visitor(ABC):
    @abstractmethod
    def visit(self, host): pass

class Parser(ABC):
    name: str = None
    _name: str = None
    _visited = False
    @abstractmethod
    def _parse(self, source: Source): pass
    def parse(self, source: Source):
        return self._parse(source)
    def __or__(self, other):
        return OrParser(self, other)
    def __and__(self, other):
        return AndParser(self, other)
    @abstractmethod
    def traverse(self, visitor: Visitor, backwards: bool = False): pass
    def __str__(self):
        return self.name or self._name or self.__class__.__name__
        

class ParserNode(Parser):
    parsers: list[Parser]
    @abstractproperty
    def symbol(self): pass
    def __init__(self, *parsers):
        self.parsers = parsers
    @property
    def _name(self): 
        return f'({f" {self.symbol} ".join(map(str, self.parsers))})'
    def traverse(self, visitor: Visitor, backwards=False):
        self._visited = True
        if not backwards: visitor.visit(self)
        for parser in self.parsers:
            if parser._visited: continue
            parser.traverse(visitor, backwards=backwards)
        if backwards: visitor.visit(self)
        self._visited = False

class ParserLeave(Parser):
    def traverse(self, visitor: Visitor, backwards=False):
        visitor.visit(self)

class TokenParser(ParserLeave):
    def __init__(self, token: Token):
        self.token = token
        self.pattern = re.compile(rf"\s*({token.regex})")
        self._name = token.name
    def _parse(self, source: Source):
        if match:=self.pattern.match(source.source, source.offset):
            source.offset = match.end()
            return self.token, match.group(1)

class OrParser(ParserNode):
    symbol = "|"
    def _parse(self, source: Source):
        for parser in self.parsers:
            if (parsed:=parser.parse(source)) is not None: 
                return parsed

class AndParser(ParserNode):
    symbol = "&"
    def _parse(self, source: Source):
        parseds = []
        offset = source.offset
        for parser in self.parsers:
            if (parsed:=parser.parse(source)) is None:
                source.offset = offset
                return None
            parseds.append(parsed)
        return parseds

INT = TokenParser(Token.INT)
PLUS = TokenParser(Token.PLUS)
MINUS = TokenParser(Token.MINUS)
STAR = TokenParser(Token.STAR)
SLASH = TokenParser(Token.SLASH)
PERCENT = TokenParser(Token.PERCENT)
IDENTIFIER = TokenParser(Token.IDENTIFIER)
DOT = TokenParser(Token.DOT)
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

def test_token_parser():
    assert INT.parse(Source("int")) == (Token.INT, "int")
    assert INT.parse(Source("  \n int")) == (Token.INT, "int")

def test_or():
    assert (INT | INT).parse(Source("   \n int")) == (Token.INT, "int")
    assert (INT | IDENTIFIER).parse(Source(" asd12")) == (Token.IDENTIFIER, "asd12")

def test_and():
    assert (INT & INT).parse(Source("int int")) == [(Token.INT, "int"), (Token.INT, "int")]
    assert (INT & INT).parse(Source("int asd")) == None
    assert (INT & INT).parse(Source("int")) == None

expression = OrParser()
expression.name = "EXP"

binary_operator = PLUS | MINUS | STAR | SLASH | PERCENT


binary_operator.name = "BINOP"
unary_operator = PLUS | MINUS
unary_operator.name = "UNOP"

primary_expression = IDENTIFIER | INTEGER | (LPAREN & expression & RPAREN)
primary_expression.name = "PRIMEXP"
unary_expression = unary_operator & primary_expression
unary_expression.name = "UNEXP"
binary_expression = (primary_expression | unary_expression) & binary_operator & expression
binary_expression.name = "BINEXP"
expression.parsers = (binary_expression | unary_expression | primary_expression).parsers

unoptimized_expression = deepcopy(expression)

def test_expression():
    assert unoptimized_expression.parse(Source("1 + 2")) == [[(Token.INTEGER, '1'), (Token.PLUS, '+')], (Token.INTEGER, '2')]
    assert unoptimized_expression.parse(Source("1 - 2")) == [[(Token.INTEGER, '1'), (Token.MINUS, '-')], (Token.INTEGER, '2')]
    assert unoptimized_expression.parse(Source("(1 + 2) - 3")) == [[[[(Token.LPAREN, '('), [[(Token.INTEGER, '1'), (Token.PLUS, '+')], (Token.INTEGER, '2')]], (Token.RPAREN, ')')], (Token.MINUS, '-')], (Token.INTEGER, '3')]
    assert unoptimized_expression.parse(Source("-5*4")) == [[[(Token.MINUS, '-'), (Token.INTEGER, '5')], (Token.STAR, '*')], (Token.INTEGER, '4')]
    assert unoptimized_expression.parse(Source("-5/5-")) == [[[(Token.MINUS, '-'), (Token.INTEGER, '5')], (Token.SLASH, '/')], (Token.INTEGER, '5')]

class OptimOr(Visitor):
    def visit(self, node: Parser):
        if not isinstance(node, OrParser): return
        parsers = []
        for parser in node.parsers:
            if isinstance(parser, OrParser):
                parsers.extend(parser.parsers)
            else:
                parsers.append(parser)
        node.parsers = parsers

expression.traverse(OptimOr(), backwards=True)
optim_or_expression = deepcopy(expression)

def test_optim_or():
    test_token_parser()
    test_or()
    test_and()
    assert optim_or_expression.parse(Source("1 + 2")) == [[(Token.INTEGER, '1'), (Token.PLUS, '+')], (Token.INTEGER, '2')]
    assert optim_or_expression.parse(Source("1 - 2")) == [[(Token.INTEGER, '1'), (Token.MINUS, '-')], (Token.INTEGER, '2')]
    assert optim_or_expression.parse(Source("(1 + 2) - 3")) == [[[[(Token.LPAREN, '('), [[(Token.INTEGER, '1'), (Token.PLUS, '+')], (Token.INTEGER, '2')]], (Token.RPAREN, ')')], (Token.MINUS, '-')], (Token.INTEGER, '3')]
    assert optim_or_expression.parse(Source("-5*4")) == [[[(Token.MINUS, '-'), (Token.INTEGER, '5')], (Token.STAR, '*')], (Token.INTEGER, '4')]
    assert optim_or_expression.parse(Source("-5/5-")) == [[[(Token.MINUS, '-'), (Token.INTEGER, '5')], (Token.SLASH, '/')], (Token.INTEGER, '5')]

class OptimAnd(Visitor):
    def visit(self, node: Parser):
        if not isinstance(node, AndParser): return
        parsers = []
        for parser in node.parsers:
            if isinstance(parser, AndParser):
                parsers.extend(parser.parsers)
            else:
                parsers.append(parser)
        node.parsers = parsers

expression.traverse(OptimAnd(), backwards=True)
optim_and_or_expression = deepcopy(expression)

def test_optim_and():
    assert optim_and_or_expression.parse(Source("1 + 2")) == [(Token.INTEGER, '1'), (Token.PLUS, '+'), (Token.INTEGER, '2')]
    assert optim_and_or_expression.parse(Source("1 - 2")) == [(Token.INTEGER, '1'), (Token.MINUS, '-'), (Token.INTEGER, '2')]
    assert optim_and_or_expression.parse(Source("(1 + 2) - 3")) == [[(Token.LPAREN, '('), [(Token.INTEGER, '1'), (Token.PLUS, '+'), (Token.INTEGER, '2')], (Token.RPAREN, ')')], (Token.MINUS, '-'), (Token.INTEGER, '3')]
    assert optim_and_or_expression.parse(Source("-5*4")) == [[(Token.MINUS, '-'), (Token.INTEGER, '5')], (Token.STAR, '*'), (Token.INTEGER, '4')]
    assert optim_and_or_expression.parse(Source("-5/5-")) == [[(Token.MINUS, '-'), (Token.INTEGER, '5')], (Token.SLASH, '/'), (Token.INTEGER, '5')]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()
    if True:
        import debug
        debug.init(Parser, Source)