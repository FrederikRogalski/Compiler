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
    Token.ALIGNAS: re.compile(r'\s*\balignas\b'),
    Token.ALIGNOF: re.compile(r'\s*\balignof\b'),
    Token.AUTO: re.compile(r'\s*\bauto\b'),
    Token.BOOL: re.compile(r'\s*\bbool\b'),
    Token.BREAK: re.compile(r'\s*\bbreak\b'),
    Token.CASE: re.compile(r'\s*\bcase\b'),
    Token.CHAR: re.compile(r'\s*\bchar\b'),
    Token.CONST: re.compile(r'\s*\bconst\b'),
    Token.CONSTEXPR: re.compile(r'\s*\bconstexpr\b'),
    Token.CONTINUE: re.compile(r'\s*\bcontinue\b'),
    Token.DEFAULT: re.compile(r'\s*\bdefault\b'),
    Token.DO: re.compile(r'\s*\bdo\b'),
    Token.DOUBLE: re.compile(r'\s*\bdouble\b'),
    Token.ELSE: re.compile(r'\s*\belse\b'),
    Token.ENUM: re.compile(r'\s*\benum\b'),
    Token.EXTERN: re.compile(r'\s*\bextern\b'),
    Token.FALSE: re.compile(r'\s*\bfalse\b'),
    Token.FLOAT: re.compile(r'\s*\bfloat\b'),
    Token.FOR: re.compile(r'\s*\bfor\b'),
    Token.GOTO: re.compile(r'\s*\bgoto\b'),
    Token.IF: re.compile(r'\s*\bif\b'),
    Token.INLINE: re.compile(r'\s*\binline\b'),
    Token.INT: re.compile(r'\s*\bint\b'),
    Token.LONG: re.compile(r'\s*\blong\b'),
    Token.NULLPTR: re.compile(r'\s*\bnullptr\b'),
    Token.REGISTER: re.compile(r'\s*\bregister\b'),
    Token.RESTRICT: re.compile(r'\s*\brestrict\b'),
    Token.RETURN: re.compile(r'\s*\breturn\b'),
    Token.SHORT: re.compile(r'\s*\bshort\b'),
    Token.SIGNED: re.compile(r'\s*\bsigned\b'),
    Token.SIZEOF: re.compile(r'\s*\bsizeof\b'),
    Token.STATIC: re.compile(r'\s*\bstatic\b'),
    Token.STATIC_ASSERT: re.compile(r'\s*\bstatic_assert\b'),
    Token.STRUCT: re.compile(r'\s*\bstruct\b'),
    Token.SWITCH: re.compile(r'\s*\bswitch\b'),
    Token.THREAD_LOCAL: re.compile(r'\s*\bthread_local\b'),
    Token.TRUE: re.compile(r'\s*\btrue\b'),
    Token.TYPEDEF: re.compile(r'\s*\btypedef\b'),
    Token.TYPEOF: re.compile(r'\s*\btypeof\b'),
    Token.TYPEOF_UNQUAL: re.compile(r'\s*\btypeof_unqual\b'),
    Token.UNION: re.compile(r'\s*\bunion\b'),
    Token.UNSIGNED: re.compile(r'\s*\bunsigned\b'),
    Token.VOID: re.compile(r'\s*\bvoid\b'),
    Token.VOLATILE: re.compile(r'\s*\bvolatile\b'),
    Token.WHILE: re.compile(r'\s*\bwhile\b'),
    Token._ALIGNAS: re.compile(r'\s*\b_Alignas\b'),
    Token._ALIGNOF: re.compile(r'\s*\b_Alignof\b'),
    Token._ATOMIC: re.compile(r'\s*\b_Atomic\b'),
    Token._BITINT: re.compile(r'\s*\b_BitInt\b'),
    Token._BOOL: re.compile(r'\s*\b_Bool\b'),
    Token._COMPLEX: re.compile(r'\s*\b_Complex\b'),
    Token._DECIMAL128: re.compile(r'\s*\b_Decimal128\b'),
    Token._DECIMAL32: re.compile(r'\s*\b_Decimal32\b'),
    Token._DECIMAL64: re.compile(r'\s*\b_Decimal64\b'),
    Token._GENERIC: re.compile(r'\s*\b_Generic\b'),
    Token._IMAGINARY: re.compile(r'\s*\b_Imaginary\b'),
    Token._NORETURN: re.compile(r'\s*\b_Noreturn\b'),
    Token._STATIC_ASSERT: re.compile(r'\s*\b_Static_assert\b'),
    Token._THREAD_LOCAL: re.compile(r'\s*\b_Thread_local\b'),
    Token.INTEGER: re.compile(r'\s*\d+(?![\.\d])'),
    Token.DOT: re.compile(r'\s*\.'),
    # ------------ OPERATORS
    Token.PLUS: re.compile(r'\s*\+'),
    Token.MINUS: re.compile(r'\s*\-'),
    Token.STAR: re.compile(r'\s*\*'),
    Token.SLASH: re.compile(r'\s*\/'),
    Token.PERCENT: re.compile(r'\s*\%'),
    Token.INCREMENT: re.compile(r'\s*\+\+'),
    Token.DECREMENT: re.compile(r'\s*\-\-'),
    # ------------ PUNCTUATORS
    Token.LPAREN: re.compile(r'\s*\('),
    Token.RPAREN: re.compile(r'\s*\)'),
    Token.LBRACKET: re.compile(r'\s*\['),
    Token.RBRACKET: re.compile(r'\s*\]'),
    Token.LBRACE: re.compile(r'\s*\{'),
    Token.RBRACE: re.compile(r'\s*\}'),
    Token.COMMA: re.compile(r'\s*\,'),
    Token.COLON: re.compile(r'\s*\:'),
    Token.SEMICOLON: re.compile(r'\s*\;'),
    
    
    Token.IDENTIFIER: re.compile(r'\s*[a-zA-Z_][a-zA-Z0-9_]*'),
}