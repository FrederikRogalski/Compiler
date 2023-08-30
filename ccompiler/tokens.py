import re
from enum import Enum, auto

class Token(Enum):
    # ------------ SPECIAL
    WHITESPACE = auto()
    # ------------ KEYWORDS
    ALIGNAS = auto()
    ALIGNOF = auto()
    AUTO = auto()
    BOOL = auto()
    BREAK = auto()
    CASE = auto()
    CHAR = auto()
    CONST = auto()
    CONSTEXPR = auto()
    CONTINUE = auto()
    DEFAULT = auto()
    DO = auto()
    DOUBLE = auto()
    ELSE = auto()
    ENUM = auto()
    EXTERN = auto()
    FALSE = auto()
    FLOAT = auto()
    FOR = auto()
    GOTO = auto()
    IF = auto()
    INLINE = auto()
    INT = auto()
    LONG = auto()
    NULLPTR = auto()
    REGISTER = auto()
    RESTRICT = auto()
    RETURN = auto()
    SHORT = auto()
    SIGNED = auto()
    SIZEOF = auto()
    STATIC = auto()
    STATIC_ASSERT = auto()
    STRUCT = auto()
    SWITCH = auto()
    THREAD_LOCAL = auto()
    TRUE = auto()
    TYPEDEF = auto()
    TYPEOF = auto()
    TYPEOF_UNQUAL = auto()
    UNION = auto()
    UNSIGNED = auto()
    VOID = auto()
    VOLATILE = auto()
    WHILE = auto()
    _ALIGNAS = auto()
    _ALIGNOF = auto()
    _ATOMIC = auto()
    _BITINT = auto()
    _BOOL = auto()
    _COMPLEX = auto()
    _DECIMAL128 = auto()
    _DECIMAL32 = auto()
    _DECIMAL64 = auto()
    _GENERIC = auto()
    _IMAGINARY = auto()
    _NORETURN = auto()
    _STATIC_ASSERT = auto()
    _THREAD_LOCAL = auto()
    
    # ------------ OPERATORS
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    INCREMENT = auto()
    DECREMENT = auto()
    
    # ------------ PUNCTUATORS
    LPAREN = auto()
    RPAREN = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    LBRACE = auto()
    RBRACE = auto()
    COMMA = auto()
    COLON = auto()
    SEMICOLON = auto()
    
    
    # ------------ OTHER
    
    EQUALS = auto()
    IDENTIFIER = auto()
    INTEGER = auto()
    DOT = auto()
    
    @property
    def regex(self):
        return regex[self]
    
    def __repr__(self):
        return f"{self.__class__.__name__}.{self.name}"
    

regex = {
    Token.WHITESPACE: r'\s',
    Token.ALIGNAS: r'\balignas\b',
    Token.ALIGNOF: r'\balignof\b',
    Token.AUTO: r'\bauto\b',
    Token.BOOL: r'\bbool\b',
    Token.BREAK: r'\bbreak\b',
    Token.CASE: r'\bcase\b',
    Token.CHAR: r'\bchar\b',
    Token.CONST: r'\bconst\b',
    Token.CONSTEXPR: r'\bconstexpr\b',
    Token.CONTINUE: r'\bcontinue\b',
    Token.DEFAULT: r'\bdefault\b',
    Token.DO: r'\bdo\b',
    Token.DOUBLE: r'\bdouble\b',
    Token.ELSE: r'\belse\b',
    Token.ENUM: r'\benum\b',
    Token.EXTERN: r'\bextern\b',
    Token.FALSE: r'\bfalse\b',
    Token.FLOAT: r'\bfloat\b',
    Token.FOR: r'\bfor\b',
    Token.GOTO: r'\bgoto\b',
    Token.IF: r'\bif\b',
    Token.INLINE: r'\binline\b',
    Token.INT: r'\bint\b',
    Token.LONG: r'\blong\b',
    Token.NULLPTR: r'\bnullptr\b',
    Token.REGISTER: r'\bregister\b',
    Token.RESTRICT: r'\brestrict\b',
    Token.RETURN: r'\breturn\b',
    Token.SHORT: r'\bshort\b',
    Token.SIGNED: r'\bsigned\b',
    Token.SIZEOF: r'\bsizeof\b',
    Token.STATIC: r'\bstatic\b',
    Token.STATIC_ASSERT: r'\bstatic_assert\b',
    Token.STRUCT: r'\bstruct\b',
    Token.SWITCH: r'\bswitch\b',
    Token.THREAD_LOCAL: r'\bthread_local\b',
    Token.TRUE: r'\btrue\b',
    Token.TYPEDEF: r'\btypedef\b',
    Token.TYPEOF: r'\btypeof\b',
    Token.TYPEOF_UNQUAL: r'\btypeof_unqual\b',
    Token.UNION: r'\bunion\b',
    Token.UNSIGNED: r'\bunsigned\b',
    Token.VOID: r'\bvoid\b',
    Token.VOLATILE: r'\bvolatile\b',
    Token.WHILE: r'\bwhile\b',
    Token._ALIGNAS: r'\b_Alignas\b',
    Token._ALIGNOF: r'\b_Alignof\b',
    Token._ATOMIC: r'\b_Atomic\b',
    Token._BITINT: r'\b_BitInt\b',
    Token._BOOL: r'\b_Bool\b',
    Token._COMPLEX: r'\b_Complex\b',
    Token._DECIMAL128: r'\b_Decimal128\b',
    Token._DECIMAL32: r'\b_Decimal32\b',
    Token._DECIMAL64: r'\b_Decimal64\b',
    Token._GENERIC: r'\b_Generic\b',
    Token._IMAGINARY: r'\b_Imaginary\b',
    Token._NORETURN: r'\b_Noreturn\b',
    Token._STATIC_ASSERT: r'\b_Static_assert\b',
    Token._THREAD_LOCAL: r'\b_Thread_local\b',
    Token.INTEGER: r'\d+(?![\.\d])',
    Token.DOT: r'\.',
    # ------------ OPERATORS
    Token.PLUS: r'\+',
    Token.MINUS: r'\-',
    Token.STAR: r'\*',
    Token.SLASH: r'\/',
    Token.PERCENT: r'\%',
    Token.INCREMENT: r'\+\+',
    Token.DECREMENT: r'\-\-',
    # ------------ PUNCTUATORS
    Token.LPAREN: r'\(',
    Token.RPAREN: r'\)',
    Token.LBRACKET: r'\[',
    Token.RBRACKET: r'\]',
    Token.LBRACE: r'\{',
    Token.RBRACE: r'\}',
    Token.COMMA: r'\,',
    Token.COLON: r'\:',
    Token.SEMICOLON: r'\;',
    
    Token.EQUALS: r'\=',
    Token.IDENTIFIER: r'[a-zA-Z_][a-zA-Z0-9_]*',
}