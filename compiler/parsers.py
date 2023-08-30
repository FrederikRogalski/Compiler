import re
from compiler.tokens import Token
from collections import OrderedDict
from abc import ABC, abstractmethod, abstractproperty

class Visitor(ABC):
    @abstractmethod
    def visit(self, host): pass

class Cache(OrderedDict):
    def __init__(self, maxsize=128):
        super().__init__()
        self.maxsize = maxsize
    def __setitem__(self, key, value):
        if len(self) >= self.maxsize:
            self.popitem(last=False)
        super().__setitem__(key, value)

def cache(func):
    def wrapper(self, source: Source):
        h = hash((self, hash(source)))
        if h in source.cache: 
            source.offset = source.cache[h][1]
            return source.cache[h][0]
        source.cache[h] = (func(self, source), source.offset)
        return source.cache[h][0]
    return wrapper

class Source:
    source: str
    offset: int
    cache: dict[int, tuple[any, int]]
    def __init__(self, source: str, offset=0):
        self.source = source
        self.offset = offset
        self.cache = Cache(maxsize=128)
    def __repr__(self):
        return f"Source({repr(self.source)}, {self.offset})"
    def __hash__(self):
        return hash((self.source, self.offset))

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