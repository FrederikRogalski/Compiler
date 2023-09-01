from copy import deepcopy
from timeit import repeat
from ccompiler.tokens import Token
from ccompiler.optim import OrOptimizer, AndOptimizer
from ccompiler.parsers import Source, TokenParser
from ccompiler.compiler import unoptimized_expression, expression, parameter_list
from ccompiler.ast import BinaryOp, UnaryOp, Immidiate, Parameter, Integer

INT = TokenParser(Token.INT)
IDENTIFIER = TokenParser(Token.IDENTIFIER)

def test_expression_parser():
    out = expression.parse(Source('-5 +(1 + 2 - 7 *                 3 /          \n4)'))

def test_token_parser():
    assert INT.parse(Source("int")) == (Token.INT, "int")
    assert INT.parse(Source("  \n int")) == (Token.INT, "int")

def test_or():
    assert (INT | INT).parse(Source("   \n int")) == (Token.INT, "int")
    assert (INT | IDENTIFIER).parse(Source(" asd12")) == (Token.IDENTIFIER, "asd12")

def test_and():
    assert (INT & INT).parse(Source("int int")) == [(Token.INT, "int"), (Token.INT, "int")]
    assert (INT & INT).parse(Source("int asd")) == None
    assert (INT & INT).parse(Source("int")) == None

def test_optimized_and():
    optimized_and_expression = deepcopy(unoptimized_expression)
    optimized_and_expression.traverse(AndOptimizer(), backwards=True)
    assert optimized_and_expression.parse(Source("1 + 2")) == BinaryOp(Immidiate(Integer, '1'), Token.PLUS, Immidiate(Integer, '2'))
    assert optimized_and_expression.parse(Source("1 - 2")) == BinaryOp(Immidiate(Integer, '1'), Token.MINUS, Immidiate(Integer, '2'))
    assert optimized_and_expression.parse(Source("(1 + 2) - 3")) == BinaryOp(BinaryOp(Immidiate(Integer, '1'), Token.PLUS, Immidiate(Integer, '2')), Token.MINUS, Immidiate(Integer, '3'))
    assert optimized_and_expression.parse(Source("-5*4")) == BinaryOp(UnaryOp(Token.MINUS, Immidiate(Integer, '5')), Token.STAR, Immidiate(Integer, '4'))
    assert optimized_and_expression.parse(Source("-5/5-")) == BinaryOp(UnaryOp(Token.MINUS, Immidiate(Integer, '5')), Token.SLASH, Immidiate(Integer, '5'))

def test_optimizer_and_or_equals_or_and():
    and_or = deepcopy(unoptimized_expression)
    or_and = deepcopy(unoptimized_expression)
    and_or.traverse(AndOptimizer(), backwards=True)
    and_or.traverse(OrOptimizer(), backwards=True)
    or_and.traverse(OrOptimizer(), backwards=True)
    or_and.traverse(AndOptimizer(), backwards=True)
    assert and_or.parse(Source("1 + 2")) == or_and.parse(Source("1 + 2"))
    assert and_or.parse(Source("1 - 2")) == or_and.parse(Source("1 - 2"))
    assert and_or.parse(Source("(1 + 2) - 3")) == or_and.parse(Source("(1 + 2) - 3"))
    assert and_or.parse(Source("-5*4")) == or_and.parse(Source("-5*4"))
    assert and_or.parse(Source("-5/5-")) == or_and.parse(Source("-5/5-"))


def test_parameter_list():
    parameter_list.parse(Source("")) == []
    parameter_list.parse(Source("int a")) == [Parameter(Token.INT, "a")]
    parameter_list.parse(Source("int a, int b")) == [Parameter(Token.INT, "a"), Parameter(Token.INT, "b")]
    parameter_list.parse(Source("int a, int b, int c")) == [Parameter(Token.INT, "a"), Parameter(Token.INT, "b"), Parameter(Token.INT, "c")]
    parameter_list.parse(Source("int")) == None
    parameter_list.parse(Source("int a, int b, int c, ")) == None
    parameter_list.parse(Source("int a, int b, int c, int")) == None

if __name__ == "__main__":
    print("Running timeing tests...")
    
    NUMBER = 100
    te = min(repeat('test_expression_parser()', number=NUMBER, globals=globals()))
    print(f"Expression parser: {te * (1_000_000 / NUMBER):.2f} µs")