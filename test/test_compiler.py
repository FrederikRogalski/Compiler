from copy import deepcopy
from timeit import repeat
from compiler.tokens import Token
from compiler.compiler import Source, expression, unoptimized_expression, OptimOr, OptimAnd, TokenParser

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

def test_unoptimized_expression():
    assert unoptimized_expression.parse(Source("1 + 2")) == [[(Token.INTEGER, '1'), (Token.PLUS, '+')], (Token.INTEGER, '2')]
    assert unoptimized_expression.parse(Source("1 - 2")) == [[(Token.INTEGER, '1'), (Token.MINUS, '-')], (Token.INTEGER, '2')]
    assert unoptimized_expression.parse(Source("(1 + 2) - 3")) == [[[[(Token.LPAREN, '('), [[(Token.INTEGER, '1'), (Token.PLUS, '+')], (Token.INTEGER, '2')]], (Token.RPAREN, ')')], (Token.MINUS, '-')], (Token.INTEGER, '3')]
    assert unoptimized_expression.parse(Source("-5*4")) == [[[(Token.MINUS, '-'), (Token.INTEGER, '5')], (Token.STAR, '*')], (Token.INTEGER, '4')]
    assert unoptimized_expression.parse(Source("-5/5-")) == [[[(Token.MINUS, '-'), (Token.INTEGER, '5')], (Token.SLASH, '/')], (Token.INTEGER, '5')]

def test_optimized_or():
    optimized_or_expression = deepcopy(unoptimized_expression)
    optimized_or_expression.traverse(OptimOr(), backwards=True)
    assert optimized_or_expression.parse(Source("1 + 2")) == [[(Token.INTEGER, '1'), (Token.PLUS, '+')], (Token.INTEGER, '2')]
    assert optimized_or_expression.parse(Source("1 - 2")) == [[(Token.INTEGER, '1'), (Token.MINUS, '-')], (Token.INTEGER, '2')]
    assert optimized_or_expression.parse(Source("(1 + 2) - 3")) == [[[[(Token.LPAREN, '('), [[(Token.INTEGER, '1'), (Token.PLUS, '+')], (Token.INTEGER, '2')]], (Token.RPAREN, ')')], (Token.MINUS, '-')], (Token.INTEGER, '3')]
    assert optimized_or_expression.parse(Source("-5*4")) == [[[(Token.MINUS, '-'), (Token.INTEGER, '5')], (Token.STAR, '*')], (Token.INTEGER, '4')]
    assert optimized_or_expression.parse(Source("-5/5-")) == [[[(Token.MINUS, '-'), (Token.INTEGER, '5')], (Token.SLASH, '/')], (Token.INTEGER, '5')]

def test_optimized_and():
    optimized_and_expression = deepcopy(unoptimized_expression)
    optimized_and_expression.traverse(OptimAnd(), backwards=True)
    assert optimized_and_expression.parse(Source("1 + 2")) == [(Token.INTEGER, '1'), (Token.PLUS, '+'), (Token.INTEGER, '2')]
    assert optimized_and_expression.parse(Source("1 - 2")) == [(Token.INTEGER, '1'), (Token.MINUS, '-'), (Token.INTEGER, '2')]
    assert optimized_and_expression.parse(Source("(1 + 2) - 3")) == [[(Token.LPAREN, '('), [(Token.INTEGER, '1'), (Token.PLUS, '+'), (Token.INTEGER, '2')], (Token.RPAREN, ')')], (Token.MINUS, '-'), (Token.INTEGER, '3')]
    assert optimized_and_expression.parse(Source("-5*4")) == [[(Token.MINUS, '-'), (Token.INTEGER, '5')], (Token.STAR, '*'), (Token.INTEGER, '4')]
    assert optimized_and_expression.parse(Source("-5/5-")) == [[(Token.MINUS, '-'), (Token.INTEGER, '5')], (Token.SLASH, '/'), (Token.INTEGER, '5')]

def test_optimizer_and_or_equals_or_and():
    and_or = deepcopy(unoptimized_expression)
    or_and = deepcopy(unoptimized_expression)
    and_or.traverse(OptimAnd(), backwards=True)
    and_or.traverse(OptimOr(), backwards=True)
    or_and.traverse(OptimOr(), backwards=True)
    or_and.traverse(OptimAnd(), backwards=True)
    assert and_or.parse(Source("1 + 2")) == or_and.parse(Source("1 + 2"))
    assert and_or.parse(Source("1 - 2")) == or_and.parse(Source("1 - 2"))
    assert and_or.parse(Source("(1 + 2) - 3")) == or_and.parse(Source("(1 + 2) - 3"))
    assert and_or.parse(Source("-5*4")) == or_and.parse(Source("-5*4"))
    assert and_or.parse(Source("-5/5-")) == or_and.parse(Source("-5/5-"))


if __name__ == "__main__":
    print("Running timeing tests...")
    
    NUMBER = 100
    te = min(repeat('test_expression_parser()', number=NUMBER, globals=globals()))
    print(f"Expression parser: {te * (1_000_000 / NUMBER):.2f} µs")