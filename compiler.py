import logging
import inspect
import argparse
from tokens import Token as T, Token
from tokens import regex
from typing import Callable
from abc import ABC, abstractmethod

WC1 = 20
WC2 = 100
COLORS = {
    "DEBUG": "\033[94m",
    "INFO": "\033[92m",
    "WARNING": "\033[93m",
    "ERROR": "\033[91m",
}
color = lambda s, c: f"{COLORS[c]}{s}\033[0m"

logger = logging.getLogger(__name__)
class Source:
    source: str
    offset: int
    callstack: list["Parser"]
    def __init__(self, source, offset=0):
        logger.debug(f"{color('SOURCE', 'WARNING').ljust(WC1+WC2)}'{source}'")
        self.source = source
        self.offset = offset
        self.callstack = []
    def __repr__(self):
        return f"Source({repr(self.source)}, {self.offset})"

class Statement:
    pass
ParseResult =  Token| Statement | None

class Parser(ABC):
    name = None
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
    def ws(self):
        """Consumes whitespace before the parser"""
        return _and(WHITESPACE.maybe(), self).bind(lambda x: ConstantParser(x[1]))
    def __str__(self):
        return self.__class__.__name__

class OrParser(Parser):
    def __init__(self, *parsers):
        # If one of the parsers is an or parser, we can just add its parsers to this one
        self.parsers = []
        for parser in parsers:
            if isinstance(parser, OrParser):
                self.parsers += parser.parsers
                if self.name: self.name += f" | {str(parser)}"
                else: self.name = str(parser)
            else:
                self.parsers.append(parser)
    def _parse(self, source: Source) -> ParseResult:
        offset = source.offset
        for parser in self.parsers:
            parsed = parser.parse(source)
            if parsed is not None: return parsed
            source.offset = offset
    def __str__(self):
        return self.name or f'({" | ".join(map(str, self.parsers))})'

class AndParser(Parser):
    def __init__(self, *parsers):
        # If one of the parsers is an and parser, we can just add its parsers to this one
        self.parsers = []
        for parser in parsers:
            if isinstance(parser, AndParser):
                self.parsers += parser.parsers
            else:
                self.parsers.append(parser)
    def _parse(self, source: Source) -> ParseResult:
        parsed = []
        offset = source.offset
        for parser in self.parsers:
            p = parser.parse(source)
            if p is None: 
                source.offset = offset
                return None
            parsed.append(p)
        return parsed
    def __str__(self):
        return self.name or f'({" & ".join(map(str, self.parsers))})'

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


binary_operator = PLUS | MINUS | STAR | SLASH | PERCENT
binary_operator.name = "BIN_OP"
unary_operator = PLUS | MINUS
unary_operator.name = "UN_OP"

class Expression(Parser):
    parser: Parser
    def __init__(self):
        self.parser = None
    def parse(self, source: Source) -> ParseResult:
        return self.parser.parse(source)

expression = Expression()
# Unary expressions are only allowed at the start of an expression or after an operator
# OrParser(IDENTIFIER, INTEGER, AndParser(LPAREN, Expression, RPAREN).bind(lambda x: ConstantParser(x[1])))
primary_expression = IDENTIFIER | INTEGER | (LPAREN & expression & RPAREN).bind(lambda x: constant(x[1]))
primary_expression.name = "PRIM_EXP"
unary_expression = unary_operator & expression
unary_expression.name = "UN_EXP"
# TODO: change this to respect operator precedence
# Basicaly this is a recursive descent parser
binary_expression = (primary_expression | unary_expression) & binary_operator & expression
binary_expression.name = "BIN_EXP"
expression.parser = binary_expression | unary_expression | primary_expression
expression.parser.name = "EXP"

# ------------------- SIMPLE STATEMENTS

# ------------------- COMPOUND STATEMENTS

if __name__ == "__main__":
    # set up logging
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    
    if args.verbose:
        # we inject the following code into the parser
        def str_call(callstack):
            s = " -> ".join(map(str,callstack))
            return s if len(s)<WC2 else len(callstack)*" " + str(callstack[-1])
            
        def parse(self, source: Source) -> ParseResult:
            source.callstack.append(self)
            label = str_call(source.callstack)
            offset = source.offset
            logger.debug(f"{color('PARSING', 'WARNING').ljust(WC1)}{label.ljust(WC2)}'{source.source[source.offset:][:20]}'")
            parse_result = self._parse(source)
            if parse_result is not None:
                logger.debug(f"{color('PARSED', 'INFO').ljust(WC1)}{label.ljust(WC2)}'{source.source[source.offset:offset]}")
            else:
                logger.debug(f"{color('FAILED', 'ERROR').ljust(WC1)}{label.ljust(WC2)}'{source.source[source.offset:][:20]}'")
            source.callstack.pop()
            return parse_result
        
        Parser.parse = parse
    
    source = Source(" 2*2 + 4")
    ret = expression.parse(source)
    print(ret, source.offset)