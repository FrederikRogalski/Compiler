from abc import abstractmethod, abstractclassmethod
from ccompiler.abstract import Visitable
from ccompiler.parsers import Visitor, Parser, OrParser, AndParser


class Optimizer(Visitor):
    @abstractclassmethod
    def optimize(cls, visitable: Visitable): pass


class ParseTreeOptimizer(Optimizer):
    @classmethod
    def optimize(cls, visitable: Visitable):
        visitable.traverse(cls, backwards=True)

class OrOptimizer(ParseTreeOptimizer):
    @staticmethod
    def visit(node: Parser):
        if not isinstance(node, OrParser): return
        parsers = []
        for parser in node.parsers:
            if isinstance(parser, OrParser):
                parsers.extend(parser.parsers)
            else:
                parsers.append(parser)
        node.parsers = parsers

class AndOptimizer(ParseTreeOptimizer):
    @staticmethod
    def visit(node: Parser):
        if not isinstance(node, AndParser): return
        parsers = []
        for parser in node.parsers:
            if isinstance(parser, AndParser):
                parsers.extend(parser.parsers)
            else:
                parsers.append(parser)
        node.parsers = parsers