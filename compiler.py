from tokens import Token as T, Token
from tokens import regex
from typing import Callable
from abc import ABC, abstractmethod

class Source:
    source: str
    offset: int
    def __init__(self, source, offset=0):
        self.source = source
        self.offset = offset
    def __repr__(self):
        return f"Source({repr(self.source)}, {self.offset})"

class Statement:
    pass
ParseResult =  Token| Statement | None

class Parser(ABC):
    @abstractmethod
    def parse(self, source: Source) -> ParseResult:
        pass
    def _or(self, *other):
        return OrParser(self, *other)
    def __or__(self, other):
        return OrParser(self, other)
    def _and(self, *other):
        return AndParser(self, *other)
    def __and__(self, other):
        return AndParser(self, other)
    def bind(self, callback):
        return BindParser(self, callback)
    def maybe(self, default=False):
        return MaybeParser(self, default)
    def ws(self):
        """Consumes whitespace before the parser"""
        return _and(WHITESPACE.maybe(), self).bind(lambda x: ConstantParser(x[1]))

class OrParser(Parser):
    def __init__(self, *parsers):
        self.parsers = parsers
    def parse(self, source: Source) -> ParseResult:
        offset = source.offset
        for parser in self.parsers:
            parsed = parser.parse(source)
            if parsed is not None: return parsed
            source.offset = offset

class AndParser(Parser):
    def __init__(self, *parsers):
        self.parsers = parsers
    def parse(self, source: Source) -> ParseResult:
        parsed = []
        offset = source.offset
        for parser in self.parsers:
            p = parser.parse(source)
            if p is None: 
                source.offset = offset
                return None
            parsed.append(p)
        return parsed

class BindParser(Parser):
    def __init__(self, parser: Parser, callback: Callable[[ParseResult], Parser]):
        self.parser = parser
        self.callback = callback
    def parse(self, source: Source):
        parsed = self.parser.parse(source)
        if parsed is not None: return self.callback(parsed).parse(source)

class MaybeParser(Parser):
    def __init__(self, parser: Parser, default: ParseResult = False):
        self.parser = parser
        self.default = default
    def parse(self, source: Source) -> ParseResult:
        parsed = self.parser.parse(source)
        if parsed is None: return self.default
        return parsed

class TokenParser(Parser):
    def __init__(self, token):
        self.token = token
    def parse(self, source: Source) -> Token | None:
        if match := regex[T.WHITESPACE].match(source.source, source.offset):
            source.offset = match.end()
        if match := regex[self.token].match(source.source, source.offset):
            source.offset = match.end()
            return self.token

class ConstantParser(Parser):
    def __init__(self, value: Token | Statement):
        self.value = value
    def parse(self, _: Source) -> ParseResult:
        return self.value

_or = Parser._or
_and = Parser._and
_ws = Parser.ws
constant = lambda x: ConstantParser(x)

WHITESPACE = TokenParser(T.WHITESPACE)
INT = TokenParser(T.INT)
PLUS = TokenParser(T.PLUS)
MINUS = TokenParser(T.MINUS)
STAR = TokenParser(T.STAR)
SLASH = TokenParser(T.SLASH)
PERCENT = TokenParser(T.PERCENT)
IDENTIFIER = TokenParser(T.IDENTIFIER)
DOT = TokenParser(T.DOT)
LPAREN = TokenParser(T.LPAREN)
RPAREN = TokenParser(T.RPAREN)
LBRACKET = TokenParser(T.LBRACKET)
RBRACKET = TokenParser(T.RBRACKET)
LBRACE = TokenParser(T.LBRACE)
RBRACE = TokenParser(T.RBRACE)
COMMA = TokenParser(T.COMMA)
COLON = TokenParser(T.COLON)
SEMICOLON = TokenParser(T.SEMICOLON)
INTEGER = TokenParser(T.INTEGER)
INCREMENT = TokenParser(T.INCREMENT)
DECREMENT = TokenParser(T.DECREMENT)


binary_operator = _or(PLUS, MINUS, STAR, SLASH, PERCENT)
unary_operator = _or(PLUS, MINUS)

class Expression(Parser):
    parser: Parser
    def __init__(self):
        self.parser = None
    def parse(self, source: Source) -> ParseResult:
        return self.parser.parse(source)

expression = Expression()
# Unary expressions are only allowed at the start of an expression or after an operator
# OrParser(IDENTIFIER, INTEGER, AndParser(LPAREN, Expression, RPAREN).bind(lambda x: ConstantParser(x[1])))
primary_expression = _or(IDENTIFIER, INTEGER, AndParser(LPAREN, expression, RPAREN).bind(lambda x: constant(x[1])))
unary_expression = unary_operator & expression
binary_expression = _and(_or(primary_expression, unary_expression), binary_operator, expression)
expression.parser = _or(binary_expression, unary_expression, primary_expression)

source = Source(" 2*2 + 4")
ret = expression.parse(source)
print(ret, source.offset)
# ------------------- SIMPLE STATEMENTS

# ------------------- COMPOUND STATEMENTS