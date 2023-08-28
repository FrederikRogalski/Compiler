import re
import pytest
from timeit import timeit, repeat
import tokens as t
import time
from tokens import Token
from compiler import Source, expression


def test_expression_parser():
    out = expression.parse(Source('-5 +(1 + 2 - 7 *                 3 /          \n4)'))
    # assert out == ((((Token.MINUS, '-'), (Token.INTEGER, '5')), (Token.PLUS, '+')), (((Token.INTEGER, '1'), (Token.PLUS, '+')), (((Token.INTEGER, '2'), (Token.MINUS, '-')), (((Token.INTEGER, '7'), (Token.STAR, '*')), (((Token.INTEGER, '3'), (Token.SLASH, '/')), (Token.INTEGER, '4'))))))

if __name__ == "__main__":
    print("Running timeing tests...")
    
    NUMBER = 100
    te = min(repeat('test_expression_parser()', number=NUMBER, globals=globals()))
    print(f"Expression parser: {te * (1_000_000 / NUMBER):.2f} µs")
    
    
    # test speed of regex aaaaaaaaaaaaab|aaaaaaaaaaaaaa
    NUM = 100000
    rege = re.compile(rf"(?P<a>{'a'*NUM+'a'})|((?P<b>{'a'*NUM+'b'}) | (?P<c>{'a'*NUM+'c'}))")
    tr = min(repeat(rf'rege.match("{"a"*NUM+"b"}")', number=NUMBER, globals=globals()))
    print(f"Regex: {tr * (1_000_000 / NUMBER):.2f} µs")