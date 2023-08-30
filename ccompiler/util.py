from abc import ABC, abstractmethod

class Visitor(ABC):
    @abstractmethod
    def visit(self, host): pass

class Visitable(ABC):
    @abstractmethod
    def traverse(self, visitor: Visitor, backwards: bool = False): pass