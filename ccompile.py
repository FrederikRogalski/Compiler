from dataclasses import dataclass
import re


# Define token types and their respective patterns
TOKEN_TYPES = {
    'INTEGER': r'\d+',
    'KEYWORD': r'\b(int|return)\b',  # Recognizes the keywords 'int' and 'return'
    'OPERATOR': r'[\+\-\*/]',
    'EQUALS': r'=',
    'IDENTIFIER': r'[a-zA-Z_][a-zA-Z0-9_]*',
    'LPAREN': r'\(',
    'RPAREN': r'\)',
    'LBRACE': r'\{',  # Recognizes '{'
    'RBRACE': r'\}',  # Recognizes '}'
    'SEMICOLON': r';',  # Recognizes ';'
    'WHITESPACE': r'\s+',  # We will recognize whitespace but won't return it as a token
    "COMMA": r',',
}



class Offset:
    def __init__(self, value=0):
        self.value = value
    def inc(self, value=1):
        self.value += value
        return self.value
    def __add__(self, other):
        return Offset(self.value + other)
        

# Higher level language constructs will be recognized by a function. Those functions may use other functions to recognize lower level constructs.
# the functions return the number of tokens they consumed, 0 if they didn't recognize anything.

class Parser:
    @classmethod
    def parse(cls, toks):
        pass
    def __or__(self, other):
        return OrParser(self, other)
    def __and__(self, other):
        return AndParser(self, other)
    def many(self):
        return ManyParser(self)
    def maybe(self, default):
        return MaybeParser(self, default)
    def bind(self, callback):
        return BindParser(self, callback)

class LogicalParser(Parser):
    parsers: list[Parser]
    @property
    def parser(self):
        return self.parsers[0]

class OrParser(LogicalParser):
    def __init__(self, *parsers):
        self.parsers = parsers
    def parse(self, toks):
        for parser in self.parsers:
            parsed, stop = parser.parse(toks)
            if not parsed is None: return parsed, stop
        return None, 0

class AndParser(LogicalParser):
    """This parser will return a list of the results of the parsers it contains if all of them succeed."""
    def __init__(self, *parsers):
        self.parsers = parsers
    def parse(self, toks):
        parsed = []
        stop = 0
        for parser in self.parsers:
            p, s = parser.parse(toks[stop:])
            if p is None: return None, 0
            parsed.append(p)
            stop += s
        return parsed, stop

class ManyParser(LogicalParser):
    def __init__(self, parser):
        self.parsers = [parser]
    def parse(self, toks):
        parsed = []
        stop = 0
        while True:
            p, s = self.parser.parse(toks[stop:])
            if p is None: break
            parsed.append(p)
            stop += s
        return parsed, stop

class MaybeParser(LogicalParser):
    def __init__(self, parser, default):
        self.parsers = [parser]
        self.default = default
    def parse(self, toks):
        parsed, stop = self.parser.parse(toks)
        if parsed is None: return self.default, 0
        return parsed, stop

class BindParser(LogicalParser):
    def __init__(self, parser, callback):
        self.parsers = [parser]
        self.callback = callback
    def parse(self, toks):
        stop = 0
        p, s = self.parser.parse(toks)
        if p is None: return None, 0
        stop += s
        p, s =  self.callback(p).parse(toks[stop:])
        return p, stop + s

class TokenParser(Parser):
    def __init__(self, token_type):
        self.token_type = token_type
    def parse(self, toks):
        if len(toks) < 1: return None, 0
        if toks[0][0] == self.token_type: return toks[0][1], 1
        return None, 0
    
class ConstantParser(Parser):
    def __init__(self, value):
        self.value = value
    def parse(self, toks):
        return self.value, 0

@dataclass
class Declaration(Parser):
    name: str
    @classmethod
    def parse(cls, toks):
        if len(toks) < 2: return None, 0
        if toks[0][1] != 'int' or toks[1][0] != 'IDENTIFIER': return None, 0
        return cls(toks[1][1]), 2

@dataclass
class Statement(Parser):
    @classmethod
    def parse(cls, toks):
        if toks[0][0] == 'SEMICOLON': return cls(), 1
        return_statement, stop = ReturnStatement.parse(toks)
        if return_statement and toks[stop][0] == 'SEMICOLON': return return_statement, stop + 1
        declaration, stop = Declaration.parse(toks)
        if declaration and toks[stop][0] == 'SEMICOLON': return declaration, stop + 1
        assignment, stop = Assignment.parse(toks)
        if assignment and toks[stop][0] == 'SEMICOLON': return assignment, stop + 1
        expression, stop = Expression.parse(toks)
        if expression and toks[stop][0] == 'SEMICOLON': return expression, stop + 1
        return None, 0

@dataclass
class ReturnStatement:
    expression: "Expression"
    @classmethod
    def parse(cls, toks):
        if toks[0][0] != 'KEYWORD' or toks[0][1] != 'return': return None, 0
        expression, stop = Expression.parse(toks[1:])
        if not expression: return None, 0
        return cls(expression), 1 + stop

@dataclass
class Assignment:
    name: str
    expression: "Expression"
    @classmethod
    def parse(cls, toks):
        if toks[0][0] != 'IDENTIFIER' or toks[1][0] != 'EQUALS': return None, 0
        expression, stop = Expression.parse(toks[2:])
        if not expression: return None, 0
        return cls(toks[0][1], expression), 2 + stop

LPAREN = TokenParser('LPAREN')
RPAREN = TokenParser('RPAREN')
COMMA = TokenParser('COMMA')
LBRACE = TokenParser('LBRACE')
RBRACE = TokenParser('RBRACE')
OPERATOR = TokenParser('OPERATOR')
IDENTIFIER = TokenParser('IDENTIFIER')
INTEGER = TokenParser('INTEGER')
SEMICOLON = TokenParser('SEMICOLON')

class Expression(Parser):
    parser = None
    @classmethod
    def parse(cls, toks):
        return cls.parser.parse(toks)

PrimaryExpression = OrParser(IDENTIFIER, INTEGER, AndParser(LPAREN, Expression, RPAREN).bind(lambda x: ConstantParser(x[1])))
UnaryExpression = OPERATOR & Expression
BinaryExpression = AndParser(OrParser(UnaryExpression, PrimaryExpression), OPERATOR, Expression)
Expression.parser = OrParser(BinaryExpression, 
                             UnaryExpression, 
                             PrimaryExpression)
Statement = OrParser(SEMICOLON, ReturnStatement, Declaration, Assignment, Expression)

ArgumentList = AndParser(BindParser(MaybeParser(Declaration, False), 
                                    lambda arg: 
                                        (COMMA & Declaration).bind(
                                            lambda comma_dec: 
                                                ConstantParser(comma_dec[1])).many().maybe([]).bind(
                                                    lambda args: 
                                                        ConstantParser(([arg] if arg else []) + args)))).bind(
                                                            lambda args_in_list: 
                                                                ConstantParser(args_in_list[0]))

class Block(Parser):
    parser = (LBRACE & ManyParser(Statement) & RBRACE)
    @classmethod
    def parse(cls, toks):
        block, stop = cls.parser.parse(toks)
        return block[0][1], stop
        
@dataclass
class FunctionDefinition:
    name: str
    args: ArgumentList
    body: Block
    @classmethod
    def parse(cls, toks):
        o = Offset()
        if toks[o.value][0] != 'KEYWORD' or toks[o.value][1] != 'int': return None, 0
        if toks[o.inc()][0] != 'IDENTIFIER': return None, 0
        name = toks[o.value][1]
        if toks[o.inc()][0] != 'LPAREN': return None, 0
        args, stop = ArgumentList.parse(toks[o.inc():])
        o += stop
        if toks[o.value][0] != 'RPAREN': return None, 0
        body, stop = Block.parse(toks[o.inc():])
        if not body: return None, 0
        return cls(name, args, body), o.inc() + stop

def lexer(source_code):
    tokens = []
    i = 0
    while i < len(source_code):
        matched = False
        for token_type, pattern in TOKEN_TYPES.items():
            if not (match := re.match(pattern, source_code[i:])): continue
            value = match.group(0)
            if token_type != 'WHITESPACE':  # We skip whitespaces
                tokens.append((token_type, value))
            i += len(value)  # Move the cursor by the matched length
            matched = True
            break  # If we found a match, we break out of the inner loop
        if not matched:
            raise ValueError(f"Unexpected character '{source_code[i]}' at index {i}.")
    return tokens

def test_lexer():
    assert lexer("") == []
def test_argument_list():
    assert ArgumentList.parse(lexer("")) == ([], 0)
    assert ArgumentList.parse(lexer("int a")) == ([Declaration("a")], 2)
    assert ArgumentList.parse(lexer("int a, int b")) == ([Declaration("a"), Declaration("b")], 5)
    assert ArgumentList.parse(lexer("int a, int b, int c")) == ([Declaration("a"), Declaration("b"), Declaration("c")], 8)

def test_expression():
    assert Expression.parse(lexer("1")) == ("1", 1)
    assert Expression.parse(lexer("a")) == ("a", 1)
    assert Expression.parse(lexer("a + 1")) == (["a", "+", "1"], 3)
    assert Expression.parse(lexer("a + 1 + b")) == (["a", "+", ["1", "+", "b"]], 5)
    assert Expression.parse(lexer("(a)")) == ("a", 3)
    assert Expression.parse(lexer("(a + 1)")) == (["a", "+", "1"], 5)
    assert Expression.parse(lexer("(a + 1) + b")) == ([["a", "+", "1"], "+", "b"], 7)
    assert Expression.parse(lexer("a + (1 + b)")) == (["a", "+", ["1", "+", "b"]], 7)
    


test_expression()