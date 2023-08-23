import re
from enum import Enum, auto

class Token(Enum):
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

ALIGNAS  = Token.ALIGNAS 
ALIGNOF  = Token.ALIGNOF 
AUTO = Token.AUTO
BOOL  = Token.BOOL 
BREAK = Token.BREAK
CASE = Token.CASE
CHAR = Token.CHAR
CONST = Token.CONST
CONSTEXPR  = Token.CONSTEXPR 
CONTINUE = Token.CONTINUE
DEFAULT = Token.DEFAULT
DO = Token.DO
DOUBLE = Token.DOUBLE
ELSE = Token.ELSE
ENUM = Token.ENUM
EXTERN = Token.EXTERN
FALSE  = Token.FALSE 
FLOAT = Token.FLOAT
FOR = Token.FOR
GOTO = Token.GOTO
IF = Token.IF
INLINE  = Token.INLINE 
INT = Token.INT
LONG = Token.LONG
NULLPTR  = Token.NULLPTR 
REGISTER = Token.REGISTER
RESTRICT  = Token.RESTRICT 
RETURN = Token.RETURN
SHORT = Token.SHORT
SIGNED = Token.SIGNED
SIZEOF = Token.SIZEOF
STATIC = Token.STATIC
STATIC_ASSERT  = Token.STATIC_ASSERT 
STRUCT = Token.STRUCT
SWITCH = Token.SWITCH
THREAD_LOCAL  = Token.THREAD_LOCAL 
TRUE  = Token.TRUE 
TYPEDEF = Token.TYPEDEF
TYPEOF  = Token.TYPEOF 
TYPEOF_UNQUAL  = Token.TYPEOF_UNQUAL 
UNION = Token.UNION
UNSIGNED = Token.UNSIGNED
VOID = Token.VOID
VOLATILE = Token.VOLATILE
WHILE = Token.WHILE
_ALIGNAS  = Token._ALIGNAS 
_ALIGNOF  = Token._ALIGNOF 
_ATOMIC  = Token._ATOMIC 
_BITINT  = Token._BITINT 
_BOOL  = Token._BOOL 
_COMPLEX  = Token._COMPLEX 
_DECIMAL128  = Token._DECIMAL128 
_DECIMAL32  = Token._DECIMAL32 
_DECIMAL64  = Token._DECIMAL64 
_GENERIC  = Token._GENERIC 
_IMAGINARY  = Token._IMAGINARY 
_NORETURN  = Token._NORETURN 
_STATIC_ASSERT  = Token._STATIC_ASSERT 
_THREAD_LOCAL = Token._THREAD_LOCAL

regex = {
    ALIGNAS: re.compile(r'\s*\balignas\b'),
    ALIGNOF: re.compile(r'\s*\balignof\b'),
    AUTO: re.compile(r'\s*\bauto\b'),
    BOOL: re.compile(r'\s*\bbool\b'),
    BREAK: re.compile(r'\s*\bbreak\b'),
    CASE: re.compile(r'\s*\bcase\b'),
    CHAR: re.compile(r'\s*\bchar\b'),
    CONST: re.compile(r'\s*\bconst\b'),
    CONSTEXPR: re.compile(r'\s*\bconstexpr\b'),
    CONTINUE: re.compile(r'\s*\bcontinue\b'),
    DEFAULT: re.compile(r'\s*\bdefault\b'),
    DO: re.compile(r'\s*\bdo\b'),
    DOUBLE: re.compile(r'\s*\bdouble\b'),
    ELSE: re.compile(r'\s*\belse\b'),
    ENUM: re.compile(r'\s*\benum\b'),
    EXTERN: re.compile(r'\s*\bextern\b'),
    FALSE: re.compile(r'\s*\bfalse\b'),
    FLOAT: re.compile(r'\s*\bfloat\b'),
    FOR: re.compile(r'\s*\bfor\b'),
    GOTO: re.compile(r'\s*\bgoto\b'),
    IF: re.compile(r'\s*\bif\b'),
    INLINE: re.compile(r'\s*\binline\b'),
    INT: re.compile(r'\s*\bint\b'),
    LONG: re.compile(r'\s*\blong\b'),
    NULLPTR: re.compile(r'\s*\bnullptr\b'),
    REGISTER: re.compile(r'\s*\bregister\b'),
    RESTRICT: re.compile(r'\s*\brestrict\b'),
    RETURN: re.compile(r'\s*\breturn\b'),
    SHORT: re.compile(r'\s*\bshort\b'),
    SIGNED: re.compile(r'\s*\bsigned\b'),
    SIZEOF: re.compile(r'\s*\bsizeof\b'),
    STATIC: re.compile(r'\s*\bstatic\b'),
    STATIC_ASSERT: re.compile(r'\s*\bstatic_assert\b'),
    STRUCT: re.compile(r'\s*\bstruct\b'),
    SWITCH: re.compile(r'\s*\bswitch\b'),
    THREAD_LOCAL: re.compile(r'\s*\bthread_local\b'),
    TRUE: re.compile(r'\s*\btrue\b'),
    TYPEDEF: re.compile(r'\s*\btypedef\b'),
    TYPEOF: re.compile(r'\s*\btypeof\b'),
    TYPEOF_UNQUAL: re.compile(r'\s*\btypeof_unqual\b'),
    UNION: re.compile(r'\s*\bunion\b'),
    UNSIGNED: re.compile(r'\s*\bunsigned\b'),
    VOID: re.compile(r'\s*\bvoid\b'),
    VOLATILE: re.compile(r'\s*\bvolatile\b'),
    WHILE: re.compile(r'\s*\bwhile\b'),
    _ALIGNAS: re.compile(r'\s*\b_Alignas\b'),
    _ALIGNOF: re.compile(r'\s*\b_Alignof\b'),
    _ATOMIC: re.compile(r'\s*\b_Atomic\b'),
    _BITINT: re.compile(r'\s*\b_BitInt\b'),
    _BOOL: re.compile(r'\s*\b_Bool\b'),
    _COMPLEX: re.compile(r'\s*\b_Complex\b'),
    _DECIMAL128: re.compile(r'\s*\b_Decimal128\b'),
    _DECIMAL32: re.compile(r'\s*\b_Decimal32\b'),
    _DECIMAL64: re.compile(r'\s*\b_Decimal64\b'),
    _GENERIC: re.compile(r'\s*\b_Generic\b'),
    _IMAGINARY: re.compile(r'\s*\b_Imaginary\b'),
    _NORETURN: re.compile(r'\s*\b_Noreturn\b'),
    _STATIC_ASSERT: re.compile(r'\s*\b_Static_assert\b'),
    _THREAD_LOCAL: re.compile(r'\s*\b_Thread_local\b'),
}