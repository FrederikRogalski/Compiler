from __future__ import annotations
from abc import ABC
from numbers import Number
from dataclasses import dataclass, field
from ccompiler.tokens import Token


@dataclass
class AstNode(ABC):
    pass
class Type(ABC):
    size: int

class Integer(Type):
    size = 4

class Float(Type):
    size = 4

@dataclass
class Block(AstNode):
    statements: list

@dataclass
class Top(AstNode):
    body: Block
        

@dataclass
class Function(AstNode):
    return_type: Token
    identifier: str
    parameter_list: list
    body: Block

@dataclass
class EmptyStatement(AstNode):
    pass

@dataclass
class Expression(AstNode):
    pass

@dataclass
class Variable(Expression):
    identifier: str
    
@dataclass
class Constant(Expression):
    type_identifier: Token
    value: Number

@dataclass
class UnaryExpression(Expression):
    operator: Token
    expression: Expression

@dataclass
class BinaryExpression(Expression):
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

@dataclass
class Parameter(AstNode):
    type_identifier: Token
    identifier: str


class Arm64Emitter:
    # depth of 0 means global scope
    # functions are at depth 1
    depth: int
    text: list[str]
    symbols: dict[str, list[Symbol]]
    # the current stack offset
    offset: int
    # the maximum stack offset
    stack_size: int
    _token_type_conversion = {Token.INTEGER: Integer, Token.FLOAT: Float}
    _type_directives_conversion = {Integer: ".word", Float: ".float"}
    
    @dataclass
    class Symbol:
        _type: Type
    
    class LocalSymbol(Symbol):
        depth: int = 0
        # offset from (stack pointer + stack_size)
        offset: int = None
        line_of_declaration: int
        lines_of_use: list[int] = field(default_factory=list)
        
    
    class GlobalSymbol(Symbol):
        value: Number
        
    def __init__(self):
        pass
    def __call__(self, ast: AstNode):
        match ast:
            case Top(body):
                self.depth = 0
                self.text = []
                global_symbols = {}
                for statement in body.statements:
                    match statement:
                        case Definition(type_identifier, identifier, expression):
                            assert expression is None or isinstance(expression, Constant), "Global variables must be initialized with compile time constants"
                            symbol = self.Symbol(self._token_type_conversion[type_identifier])
                            global_symbols[identifier] = symbol
                            self.symbols[identifier] = symbol
                        case Function():
                            self(statement)
                        case _:
                            raise NotImplementedError(statement)
                # resolve global variables
                for identifier, symbol in global_symbols.items():
                    self.text.extend([
                        f"_{identifier}:",
                        f"  .{self._type_directives_conversion[symbol._type]} {symbol.value}"
                    ])
            case Block(statements):
                self.depth += 1
                for statement in statements:
                    self(statement)
                self.depth -= 1
            case Function(return_type, identifier, parameter_list, body):
                self.stack_size = 0
                self.text.extend([
                    f"  .globl _{identifier}",
                     "  .align      2",
                ])
                self(body)
                # resolve local variables
                for symbol in self.local_symbols.values():
                    self.text[symbol.line] = f"str w8 [sp, #{self.stack_size-symbol.offset}]"
            case Definition(type_identifier, identifier, expression):
                self(expression)
                symbol = self.Symbol(self._token_type_conversion[type_identifier], self.depth, self.stack_size, expression.line)
                
            case _:
                raise NotImplementedError(ast)
                