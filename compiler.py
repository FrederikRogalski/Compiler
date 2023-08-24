import logging
import inspect
import argparse
from tokens import Token as T, Token
from tokens import regex
from typing import Callable
from abc import ABC, abstractmethod




logger = logging.getLogger(__name__)
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
    # user given name
    name = None
    # human readable string created programmatically
    _name = None
    def parse(self, source: Source) -> ParseResult:
        return self._parse(source)
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
    def __str__(self):
        return self.name or self._name or self.__class__.__name__

class OrParser(Parser):
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self._name = f'({p1} | {p2})'
    def _parse(self, source: Source) -> ParseResult:
        offset = source.offset
        if (parsed := self.p1.parse(source)) is not None: return parsed
        source.offset = offset
        if (parsed := self.p2.parse(source)) is not None: return parsed
        source.offset = offset

class AndParser(Parser):
    def __init__(self, p1, p2):
        # If one of the parsers is an and parser, we can just add its parsers to this one
        self.p1 = p1
        self.p2 = p2
        self._name = f'({p1} & {p2})'
    def _parse(self, source: Source) -> ParseResult:
        offset = source.offset
        if (parsed1 := self.p1.parse(source)) is None: return None
        if (parsed2 := self.p2.parse(source)) is None: return None
        return (parsed1, parsed2)

class BindParser(Parser):
    def __init__(self, parser: Parser, callback: Callable[[ParseResult], Parser]):
        self.parser = parser
        self.callback = callback
    def _parse(self, source: Source):
        parsed = self.parser.parse(source)
        if parsed is not None: return self.callback(parsed).parse(source)

class MaybeParser(Parser):
    def __init__(self, parser: Parser, default: ParseResult = False):
        self.parser = parser
        self.default = default
    def _parse(self, source: Source) -> ParseResult:
        parsed = self.parser.parse(source)
        if parsed is None: return self.default
        return parsed

class TokenParser(Parser):
    def __init__(self, token):
        self.token = token
    def _parse(self, source: Source) -> Token | None:
        if match := regex[self.token].match(source.source, source.offset):
            source.offset = match.end()
            return self.token
    def __repr__(self):
        return f"TokenParser({self.token})"
    def __str__(self):
        return self.token.name

class ConstantParser(Parser):
    def __init__(self, value: Token | Statement):
        self.value = value
    def _parse(self, _: Source) -> ParseResult:
        return self.value

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


binary_operator = PLUS | MINUS | STAR | SLASH | PERCENT
binary_operator.name = "BIN_OP"
unary_operator = PLUS | MINUS
unary_operator.name = "UN_OP"

class Expression(Parser):
    pass

expression = Expression()
# Unary expressions are only allowed at the start of an expression or after an operator
# OrParser(IDENTIFIER, INTEGER, AndParser(LPAREN, Expression, RPAREN).bind(lambda x: ConstantParser(x[1])))
primary_expression = IDENTIFIER | INTEGER | (LPAREN & expression & RPAREN).bind(lambda x: constant(x[0][1]))
primary_expression.name = "PRIM_EXP"
unary_expression = unary_operator & primary_expression
unary_expression.name = "UN_EXP"
# TODO: change this to respect operator precedence
# Basicaly this is a recursive descent parser
binary_expression = (primary_expression | unary_expression) & binary_operator & expression
binary_expression.name = "BIN_EXP"
_expression = binary_expression | unary_expression | primary_expression
expression._parse = _expression._parse
expression.name = "EXP"

# ------------------- SIMPLE STATEMENTS

# ------------------- COMPOUND STATEMENTS

if __name__ == "__main__":
    # set up logging
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()
    args.verbose = True
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    
    if args.verbose:
        class _Debug:
            COLORS = {
                "DEBUG": "\033[94m",
                "INFO": "\033[92m",
                "WARNING": "\033[93m",
                "ERROR": "\033[91m",
            }
            STAT2COL = {
                "SOURCE": COLORS["DEBUG"],
                "PARSING": COLORS["WARNING"],
                "SUCCEEDED": COLORS["INFO"],
                "FAILED": COLORS["ERROR"]
            }
            CALLSTACK_WIDTH = 100
            counter = 0
            @classmethod
            def color(cls, s, c):
                return f"{c}{s}\033[0m"
            @classmethod
            def debug(cls, status: str, source: str, callstack: list = None):
                cls.counter += 1
                callstack = callstack or []
                callstack_str = ""
                if callstack:
                    page = 0
                    callstack_str = str(callstack[0])
                    for call in callstack[1:]:
                        callstack_str += f" -> {str(call)}"
                        if len(callstack_str) > cls.CALLSTACK_WIDTH:
                            page += 1
                            callstack_str = f"({page})".ljust(4) + "-> " + str(call)
                logger.debug(str(cls.counter).ljust(6) + str(len(callstack)).ljust(4) + cls.color(f'{status.ljust(20)} {callstack_str.ljust(cls.CALLSTACK_WIDTH)[:cls.CALLSTACK_WIDTH]} "{source}"', cls.STAT2COL[status]))

        _debug = _Debug.debug
        
        def source_init(self, source, offset=0):
            _debug("SOURCE", source)
            self.source = source
            self.offset = offset
            self.callstack = []
        
        Source.__init__ = source_init
        
        # we inject the following code into the parser
        def parse(self, source: Source) -> ParseResult:
            if self.name is None and not isinstance(self, TokenParser): return self._parse(source)
            source.callstack.append(self)
            offset = source.offset
            _debug("PARSING", source.source[offset:], source.callstack)
            parse_result = self._parse(source)
            if parse_result is not None:
                _debug("SUCCEEDED", source.source[offset:source.offset], source.callstack)
            else:
                _debug("FAILED", source.source[offset:source.offset], source.callstack)
            source.callstack.pop()
            return parse_result
        
        Parser.parse = parse
    
    source = Source("-5 * (10 +10)")
    ret = expression.parse(source)
    print(ret, source.offset)
    
    import graphviz
    from uuid import uuid1
    from typing import Iterable
    g = graphviz.Digraph("out")
    p = g.node("Top")
    def add_nodes(nodes: tuple, p: str):
        for node in nodes:
            u = str(uuid1())
            g.node(u,repr(node))
            g.edge(u, p)
            try:
                add_nodes(node, u)
            except:
                pass
    add_nodes(ret, "Top")
    g.save()