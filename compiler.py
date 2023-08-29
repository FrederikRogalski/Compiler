import re
import argparse
from functools import lru_cache
from copy import deepcopy
from tokens import Token
from abc import ABC, abstractmethod, abstractproperty

class Source:
    source: str
    offset: int
    cache: dict[int, tuple[any, int]]
    def __init__(self, source: str, offset=0):
        self.source = source
        self.offset = offset
        self.cache = {}
    def __repr__(self):
        return f"Source({repr(self.source)}, {self.offset})"
    def __hash__(self):
        return hash((self.source, self.offset))

class Visitor(ABC):
    @abstractmethod
    def visit(self, host): pass

def cache(func):
    
    def wrapper(self, source: Source):
        h = hash((self, hash(source)))
        if h in source.cache: 
            source.offset = source.cache[h][1]
            return source.cache[h][0]
        source.cache[h] = (func(self, source), source.offset)
        return source.cache[h][0]
    return wrapper

class Parser(ABC):
    name: str = None
    _name: str = None
    _visited = False
    @abstractmethod
    def _parse(self, source: Source): pass
    @cache
    def parse(self, source: Source):
        return self._parse(source)
    def __or__(self, other):
        return OrParser(self, other)
    def __and__(self, other):
        return AndParser(self, other)
    def many(self):
        return ManyParser(self)
    def bind(self, callback: 'Parser'):
        return BindParser(self, callback)
        
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

class ManyParser(ParserNode):
    symbol = "*"
    @property
    def _name(self): return f"({self.parsers[0]}){self.symbol}"
    def _parse(self, source: Source):
        parseds = []
        while (parsed:=self.parsers[0].parse(source)) is not None:
            parseds.append(parsed)
        return parseds[0] if len(parseds) == 1 else parseds

class BindParser(ParserNode):
    symbol = ">>"
    def __init__(self, parser: Parser, callback: Parser):
        self.parsers = [parser]
        self.callback = callback
    def _parse(self, source: Source):
        if (parsed:=self.parsers[0].parse(source)) is None: return None
        return self.callback(parsed).parse(source)

class ConstantParser(ParserLeave):
    def __init__(self, parsed):
        self.parsed = parsed
        self._name = str(parsed)
    def _parse(self, source: Source):
        return self.parsed


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

expression = OrParser()
expression.name = "EXP"

binary_operator = PLUS | MINUS | STAR | SLASH | PERCENT


binary_operator.name = "BINOP"
unary_operator = PLUS | MINUS
unary_operator.name = "UNOP"


factor = OrParser()
factor.parsers = (IDENTIFIER | INTEGER | (LPAREN & expression & RPAREN) | (unary_operator & factor)).parsers
factor.name = "FACT"

term = OrParser()
term.parsers = ((factor & (STAR | SLASH | PERCENT) & term) | factor).parsers
term.name = "TERM"

expression.parsers = ((term & (PLUS | MINUS) & expression) | term).parsers
unoptimized_expression = deepcopy(expression)

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

expression.traverse(OptimOr(), backwards=True)
expression.traverse(OptimAnd(), backwards=True)
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()
    if args.verbose:
        import debug
        debug.init(Parser, Source)
    print(expression.parse(Source('-5 + 5')))