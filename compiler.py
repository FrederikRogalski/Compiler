import re
import string
import logging
import random
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
    # Optional regex to match. If a parser has a regex, it will be used.
    regex = None
    def parse(self, source: Source) -> ParseResult:
        return self._parse(source)
    def __or__(self, other):
        _name = f"({self} | {other})"
        tmp_regex_parsers = []
        parsers = []
        for parser in (self, other):
            parsers.extend(parser.parsers if isinstance(parser, OrParser) else [parser])
        _parsers = []
        for parser in parsers:
            if isinstance(p, RegexParser):
                tmp_regex_parsers.append(p)
                continue
            self._append_tmp(tmp_regex_parsers, _parsers, RegexParser._or)
            _parsers.append(p)
        self._append_tmp(tmp_regex_parsers, _parsers, RegexParser._or)
        ret_inst = OrParser(*_parsers) if len(_parsers) > 1 else _parsers[0]
        ret_inst._name = _name
        return ret_inst
                
    @staticmethod
    def _append_tmp(tmp: list, parsers, aggregator):
        if (len_tmp := len(tmp)) > 0:
            parsers.append(tmp[0]) if len_tmp == 1 else parsers.append(aggregator(*tmp))
            tmp.clear()
        
        
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
    """Non commutative or parser. Optimizes nested or parsers by flattening them."""
    def __init__(self, *parsers):
        self.parsers = parsers
        
    def _parse(self, source: Source) -> ParseResult:
        for parser in self.parsers:
            if (parsed := parser.parse(source)) is not None: return parsed
    

class AndParser(Parser):
    def __init__(self, p1, p2):
        self._name = f'({p1} & {p2})'
        self.parsers = []
        for parser in (p1, p2):
            if isinstance(parser, AndParser):
                self.parsers.extend(parser.parsers)
            else:
                self.parsers.append(parser)
        # now we combine all regex parsers that follow after each other
        _parsers = []
        tmp = []
        for parser in self.parsers:
            if isinstance(parser, RegexParser):
                tmp.append(parser)
            else:
                if tmp != []:
                    if len(tmp) == 1:
                        _parsers.append(tmp[0])
                    else:
                        _parsers.append(RegexParser._and(*tmp))
                    tmp = []
                _parsers.append(parser)
        if tmp != []:
            if len(tmp) == 1:
                _parsers.append(tmp[0])
            else:
                _parsers.append(RegexParser._and(*tmp))
        self._parsers = _parsers
    def _parse(self, source: Source) -> ParseResult:
        offset = source.offset
        parsed = []
        for parser in self._parsers:
            if (p := parser.parse(source)) is None:
                source.offset = offset
                return None
            parsed.append(p)
        return tuple(parsed)
            

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

class ConstantParser(Parser):
    def __init__(self, value: Token | Statement):
        self.value = value
    def _parse(self, _: Source) -> ParseResult:
        return self.value

constant = lambda x: ConstantParser(x) 

class RegexParser(Parser):
    def __init__(self, returns: dict[str, object], regex: str):
        self.returns = returns
        self.regex = regex
        self._regex = re.compile(rf"\s*({self.regex})")
        self._name = regex
    def _parse(self, source: Source):
        if match := self._regex.match(source.source, source.offset):
            source.offset = match.end()
            # The regex was matched. Now we build the return value from the matched groups
            return self.build_return(self.returns, match)
        
    @staticmethod
    def build_return(returns: dict[str, Token | dict], match):
        """builds the return value recursively from the matched groups"""
        rets = []
        for ret in returns:
            if (s:=match.group(ret)) is not None:
                if not isinstance(returns[ret], dict):
                    return returns[ret], s
                rets.append(RegexParser.build_return(returns[ret], match))
        return tuple(rets)
    
    @classmethod
    def _or(cls, *parsers):
        returns = {}
        regex = ""
        for parser in parsers:
            id_parser = f"l{id(parser)}"
            returns[id_parser] = parser.returns
            regex += rf"(?P<{id_parser}>{parser.regex})|"
        regex = regex[:-1]
        return RegexParser(returns, regex)
    
    @classmethod
    def _and(cls, *parsers):
        returns = {}
        regex = ""
        for parser in parsers:
            id_parser = f"l{id(parser)}"
            returns[id_parser] = parser.returns
            regex += rf"(?P<{id_parser}>{parser.regex})"
        regex = regex[:-1]
        return RegexParser(returns, regex)
            

def token(token: Token):
    return RegexParser({token.name: token}, fr"(?P<{token.name}>{token.regex})")

INT = token(Token.INT)
PLUS = token(Token.PLUS)
MINUS = token(Token.MINUS)
STAR = token(Token.STAR)
SLASH = token(Token.SLASH)
PERCENT = token(Token.PERCENT)
IDENTIFIER = token(Token.IDENTIFIER)
DOT = token(Token.DOT)
LPAREN = token(Token.LPAREN)
RPAREN = token(Token.RPAREN)
LBRACKET = token(Token.LBRACKET)
RBRACKET = token(Token.RBRACKET)
LBRACE = token(Token.LBRACE)
RBRACE = token(Token.RBRACE)
COMMA = token(Token.COMMA)
COLON = token(Token.COLON)
SEMICOLON = token(Token.SEMICOLON)
INTEGER = token(Token.INTEGER)
INCREMENT = token(Token.INCREMENT)
DECREMENT = token(Token.DECREMENT)


binary_operator = PLUS | MINUS | STAR | SLASH | PERCENT
binary_operator.name = "BIN_OP"
unary_operator = PLUS | MINUS
unary_operator.name = "UN_OP"


class Expression(Parser):
    pass

expression = Expression()
# Unary expressions are only allowed at the start of an expression or after an operator
# OrParser(IDENTIFIER, INTEGER, AndParser(LPAREN, Expression, RPAREN).bind(lambda x: ConstantParser(x[1])))
lp_exp_rp = LPAREN & expression & RPAREN
primary_expression = IDENTIFIER | INTEGER | (lp_exp_rp).bind(lambda x: constant(x[0][1]))
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
            _Debug.counter = 0
            _debug("SOURCE", source)
            self.source = source
            self.offset = offset
            self.callstack = []
        
        Source.__init__ = source_init
        
        # we inject the following code into the parser
        def parse(self, source: Source) -> ParseResult:
            # if self.name is None: return self._parse(source)
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
    
    logging.getLogger("graphviz._tools").setLevel(logging.WARNING)
    import graphviz
    from uuid import uuid1
        
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