import pytest
import tokens as t
from tokens import *
from compiler import Source, TokenParser, expression


@pytest.mark.parametrize("source, parser_token, expected_token, expected_offset", [
    ("int", INT, INT, 3),
    ("int ", INT, INT, 3),
    (" int", INT, INT, 4),
    (" int ", INT, INT, 4),
    ("intint", INT, None, 0),
    ("int3 int", INT, None, 0),
    ("int int", INT, INT, 3),
    ("   int", INT, INT, 6),
    ("   int   ", INT, INT, 6),
    ("   \nint   int", INT, INT, 7),
    ("  \n_Static_assert", t._STATIC_ASSERT, t._STATIC_ASSERT, 17)
])
def test_token_parser(source, parser_token, expected_token, expected_offset):
    parser = TokenParser(parser_token).ws()
    source = Source(source)
    assert parser.parse(source) == expected_token
    assert source.offset == expected_offset
    
@pytest.mark.parametrize("source, expected, expected_offset", [
    ("1", "1", 1),
    ("1 + 2", 3, 5),
def test_expression_parser(
    