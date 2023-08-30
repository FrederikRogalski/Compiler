from abc import ABC, abstractmethod
from compiler.parsers import Visitor, Parser, OrParser, AndParser

class OptimOr(Visitor):
    def visit(self, node: Parser):
        if not isinstance(node, OrParser): return
        parsers = []
        for parser in node.parsers:
            if isinstance(parser, OrParser):
                parsers.extend(parser.parsers)
            else:
                parsers.append(parser)
        node.parsers = parsers

class OptimAnd(Visitor):
    def visit(self, node: Parser):
        if not isinstance(node, AndParser): return
        parsers = []
        for parser in node.parsers:
            if isinstance(parser, AndParser):
                parsers.extend(parser.parsers)
            else:
                parsers.append(parser)
        node.parsers = parsers