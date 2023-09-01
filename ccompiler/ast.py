from enum import Enum
from numbers import Number
from dataclasses import dataclass
from ccompiler.tokens import Token
from abc import abstractmethod, ABC
from collections import OrderedDict
from string import Template


class Scope(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.offset = 0
        self.max_offset = kwargs.get("max_offset", MaxOffset())
    def create_var(self, identifier: str, size: int = 8) -> int:
        """address is offset from stack pointer"""
        # early return if variable was defined before
        if identifier in self: return self[identifier]
        self[identifier] = self.offset
        self.offset += size
        self.max_offset.check(self.offset)
        return self[identifier]
    def __getitem__(self, key):
        if key not in self:
            raise Exception(f"Variable '{key}' not found")
        return super().__getitem__(key)
    def create_child(self):
        return Scope(self, max_offset=self.max_offset)

class Program(ABC):
    header: list[str]
    code: list[str]
    text: list[str]
    
    def __init__(self):
        self.code = []
        self.text = []
    
    @classmethod
    def build(cls, ast):
        o = cls()
        o.code = ast.emit(Scope())
        return o
        
    
    def create_local_var(self, identifier: str, size: int = 8) -> int:
        """address is offset from stack pointer"""
        assert identifier not in self.variables[self.depth],\
            f"Redefinition of variable {identifier}"
        # variable offset from sp is last variable offset from sp + size
        self.variables[self.depth][identifier] = \
            self.variables[self._depth][next(reversed(self.variables[self._depth]))] + size
        self.max_offset_sp = max(self.variables[self.depth][identifier], self.max_offset_sp)
        return self.variables[self.depth][identifier]
    
    def get_local_var(self, identifier: str):
        for scope in reversed(self.variables[:self.depth]):
            if identifier in scope:
                return scope[identifier]
        raise Exception(f"Variable {identifier} not found")
    
    def __str__(self):
        return "\n".join([*self.header, *self.code, *self.text])

class Arm64Program(Program):
    def __init__(self):
        super().__init__()
        self.header = [
            ".globl _main",
            ".p2align 2"
        ]

class MaxOffset:
    value: int
    def __init__(self):
        self.value = 0
    def check(self, value: int):
        value = value + value % 16
        self.value = max(self.value, value)



class Type(ABC):
    size: int

class Integer(Type):
    size = 4

class Float(Type):
    size = 4
    

@dataclass
class AstNode(ABC):
    def emit(self, scope: Scope): 
        raise NotImplementedError(f"emit not implemented for {self.__class__.__name__}")
    
class Block(list, AstNode):
    def emit(self, scope: Scope):
        scope = scope.create_child()
        inner = [instruction for sublist in map(lambda x: x.emit(scope), self) for instruction in sublist]
        return inner

@dataclass
class Top(AstNode):
    body: Block
    def emit(self, scope: Scope):
        inner = self.body.emit(scope)
        return inner
        

@dataclass
class Variable(AstNode):
    identifier: str
    def emit(self, scope: Scope):
        return [
            f"ldr w8, [sp, #{scope[self.identifier]}]"
        ]
    
@dataclass
class Immidiate(AstNode):
    type_identifier: Token
    value: Number
    def emit(self, scope: Scope):
        return [
            f"mov w8, #{self.value}",
        ]
        

@dataclass
class Function(AstNode):
    return_type: Token
    identifier: str
    parameter_list: list
    body: Block
    def emit(self, scope: Scope):
        inner = self.body.emit(scope)
        stack_size = scope.max_offset.value
        # now we know the stack size and can add it to the scope
        # TODO: variables on stack or reversed in comparison to standard.
        return [
            f"_{self.identifier}:",
            f"sub sp, sp, #{stack_size}", # TODO: Does this have to be aligned by 16?
            *inner
        ]

@dataclass
class EmptyStatement(AstNode):
    pass

@dataclass
class Expression(AstNode):
    pass

@dataclass
class UnaryOp(AstNode):
    operator: Token
    expression: Expression

@dataclass
class BinaryOp(AstNode):
    left: Expression
    operator: Token
    right: Expression
    _operator_map = {
        Token.PLUS: "add",
        Token.MINUS: "sub",
        Token.STAR: "mul",
        Token.SLASH: "sdiv",
        Token.PERCENT: "srem",
    }
        
    def emit(self, scope: Scope):
        return [
            *self.left.emit(scope),
            "mov w9, w8",
            *self.right.emit(scope),
            f"{self._operator_map[self.operator]} w8, w9, w8"
        ]

@dataclass
class Return(AstNode):
    expression: Expression
    def emit(self, scope: Scope):
        return [
            *self.expression.emit(scope),
            "mov w0, w8",
            f"add sp, sp, #{scope.max_offset.value}",
            "ret"
        ]

@dataclass
class Assignment(AstNode):
    identifier: str
    expression: Expression
    def emit(self, scope: Scope):
        return [
            *self.expression.emit(scope),
            f"str w8, [sp, #{scope[self.identifier]}]"
        ]

@dataclass
class Definition(AstNode):
    type_identifier: Token
    identifier: str
    expression: Expression = None
    def emit(self, scope: Scope):
        address = scope.create_var(self.identifier)
        if self.expression is None: return []
        return [
            *self.expression.emit(scope),
            f"str w8, [sp, #{address}]"
        ]

@dataclass
class Parameter(AstNode):
    type_identifier: Token
    identifier: str