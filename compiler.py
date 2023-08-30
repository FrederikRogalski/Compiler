import re
from collections import OrderedDict
from copy import deepcopy
from tokens import Token
from abc import ABC, abstractmethod, abstractproperty

class Cache(OrderedDict):
    def __init__(self, maxsize=128):
        super().__init__()
        self.maxsize = maxsize
    def __setitem__(self, key, value):
        if len(self) >= self.maxsize:
            self.popitem(last=False)
        super().__setitem__(key, value)

class Source:
    source: str
    offset: int
    cache: dict[int, tuple[any, int]]
    def __init__(self, source: str, offset=0):
        self.source = source
        self.offset = offset
        self.cache = Cache(maxsize=256)
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
    # TODO: we don't need _parse, we can just use parse and call super().parse
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
        return parseds

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


# Empty parsers for recursive reference - to be filled later
expression = OrParser()
factor = OrParser()
term = OrParser()

# ---------- TOKEN UNIONS
binary_operator = PLUS | MINUS | STAR | SLASH | PERCENT
binary_operator.name = "BINOP"
unary_operator = PLUS | MINUS
unary_operator.name = "UNOP"
type_identifier = INT
type_identifier.name ="TYPE"

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
return_statement = TokenParser(Token.RETURN) & expression


statement = ((definition | assignment | return_statement | expression) & SEMICOLON) | SEMICOLON
statement.name = "STATEMENT"


block = LBRACE & statement.many() & RBRACE
block.name = "BLOCK"
parameter_list = ((definition & COMMA).many() & definition) | ConstantParser([])
parameter_list.name = "PARAMS"
function = type_identifier & IDENTIFIER & LPAREN & parameter_list & RPAREN & block
function.name = "FUNC"

top = (function | statement).many()

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

top.traverse(OptimOr(), backwards=True)
top.traverse(OptimAnd(), backwards=True)
        
if __name__ == "__main__":
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
        import debug
        debug.init(Parser, Source)
    
    source = Source(args.string or args.input.read())
    pprint(top.parse(source))