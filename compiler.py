import re
import pytest
from typing import Literal
from tokens import *
import tokens as t

class Source:
    source: str
    offset: int
    def __init__(self, source, offset=0):
        self.source = source
        self.offset = offset
    def __repr__(self):
        return f"Source({repr(self.source)}, {self.offset})"

class TokenParser:
    def __init__(self, token):
        self.token = token
    def parse(self, source: Source) -> Token | None:
        if match := regex[self.token].match(source.source, source.offset):
            source.offset += match.end()
            return self.token

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
    parser = TokenParser(parser_token)
    source = Source(source)
    assert parser.parse(source) == expected_token
    assert source.offset == expected_offset