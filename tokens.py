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
    
    IDENTIFIER = auto()
    INTEGER = auto()
    DOT = auto()
    

regex = {
    Token.WHITESPACE: re.compile(r'\s+'),
    Token.ALIGNAS: re.compile(r'\balignas\b'),
    Token.ALIGNOF: re.compile(r'\balignof\b'),
    Token.AUTO: re.compile(r'\bauto\b'),
    Token.BOOL: re.compile(r'\bbool\b'),
    Token.BREAK: re.compile(r'\bbreak\b'),
    Token.CASE: re.compile(r'\bcase\b'),
    Token.CHAR: re.compile(r'\bchar\b'),
    Token.CONST: re.compile(r'\bconst\b'),
    Token.CONSTEXPR: re.compile(r'\bconstexpr\b'),
    Token.CONTINUE: re.compile(r'\bcontinue\b'),
    Token.DEFAULT: re.compile(r'\bdefault\b'),
    Token.DO: re.compile(r'\bdo\b'),
    Token.DOUBLE: re.compile(r'\bdouble\b'),
    Token.ELSE: re.compile(r'\belse\b'),
    Token.ENUM: re.compile(r'\benum\b'),
    Token.EXTERN: re.compile(r'\bextern\b'),
    Token.FALSE: re.compile(r'\bfalse\b'),
    Token.FLOAT: re.compile(r'\bfloat\b'),
    Token.FOR: re.compile(r'\bfor\b'),
    Token.GOTO: re.compile(r'\bgoto\b'),
    Token.IF: re.compile(r'\bif\b'),
    Token.INLINE: re.compile(r'\binline\b'),
    Token.INT: re.compile(r'\bint\b'),
    Token.LONG: re.compile(r'\blong\b'),
    Token.NULLPTR: re.compile(r'\bnullptr\b'),
    Token.REGISTER: re.compile(r'\bregister\b'),
    Token.RESTRICT: re.compile(r'\brestrict\b'),
    Token.RETURN: re.compile(r'\breturn\b'),
    Token.SHORT: re.compile(r'\bshort\b'),
    Token.SIGNED: re.compile(r'\bsigned\b'),
    Token.SIZEOF: re.compile(r'\bsizeof\b'),
    Token.STATIC: re.compile(r'\bstatic\b'),
    Token.STATIC_ASSERT: re.compile(r'\bstatic_assert\b'),
    Token.STRUCT: re.compile(r'\bstruct\b'),
    Token.SWITCH: re.compile(r'\bswitch\b'),
    Token.THREAD_LOCAL: re.compile(r'\bthread_local\b'),
    Token.TRUE: re.compile(r'\btrue\b'),
    Token.TYPEDEF: re.compile(r'\btypedef\b'),
    Token.TYPEOF: re.compile(r'\btypeof\b'),
    Token.TYPEOF_UNQUAL: re.compile(r'\btypeof_unqual\b'),
    Token.UNION: re.compile(r'\bunion\b'),
    Token.UNSIGNED: re.compile(r'\bunsigned\b'),
    Token.VOID: re.compile(r'\bvoid\b'),
    Token.VOLATILE: re.compile(r'\bvolatile\b'),
    Token.WHILE: re.compile(r'\bwhile\b'),
    Token._ALIGNAS: re.compile(r'\b_Alignas\b'),
    Token._ALIGNOF: re.compile(r'\b_Alignof\b'),
    Token._ATOMIC: re.compile(r'\b_Atomic\b'),
    Token._BITINT: re.compile(r'\b_BitInt\b'),
    Token._BOOL: re.compile(r'\b_Bool\b'),
    Token._COMPLEX: re.compile(r'\b_Complex\b'),
    Token._DECIMAL128: re.compile(r'\b_Decimal128\b'),
    Token._DECIMAL32: re.compile(r'\b_Decimal32\b'),
    Token._DECIMAL64: re.compile(r'\b_Decimal64\b'),
    Token._GENERIC: re.compile(r'\b_Generic\b'),
    Token._IMAGINARY: re.compile(r'\b_Imaginary\b'),
    Token._NORETURN: re.compile(r'\b_Noreturn\b'),
    Token._STATIC_ASSERT: re.compile(r'\b_Static_assert\b'),
    Token._THREAD_LOCAL: re.compile(r'\b_Thread_local\b'),
    Token.INTEGER: re.compile(r'\d+(?![\.\d])'),
    Token.DOT: re.compile(r'\.'),
    # ------------ OPERATORS
    Token.PLUS: re.compile(r'\+'),
    Token.MINUS: re.compile(r'\-'),
    Token.STAR: re.compile(r'\*'),
    Token.SLASH: re.compile(r'\/'),
    Token.PERCENT: re.compile(r'\%'),
    Token.INCREMENT: re.compile(r'\+\+'),
    Token.DECREMENT: re.compile(r'\-\-'),
    # ------------ PUNCTUATORS
    Token.LPAREN: re.compile(r'\('),
    Token.RPAREN: re.compile(r'\)'),
    Token.LBRACKET: re.compile(r'\['),
    Token.RBRACKET: re.compile(r'\]'),
    Token.LBRACE: re.compile(r'\{'),
    Token.RBRACE: re.compile(r'\}'),
    Token.COMMA: re.compile(r'\,'),
    Token.COLON: re.compile(r'\:'),
    Token.SEMICOLON: re.compile(r'\;'),
    
    
    Token.IDENTIFIER: re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*'),
}