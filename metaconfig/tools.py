from abc import abstractmethod, ABCMeta
import collections

class Primitive(metaclass=ABCMeta):
    @abstractmethod
    def __call__(self): pass

class Constant(Primitive):
    def __init__(self, value):
        assert not isinstance(value, Primitive)
        self.value = value
    def __call__(self):
        return self.value

class Function(Primitive):
    def __init__(self, func, *args):
        assert isinstance(func, collections.Callable)
        self.func = func
        for value in args:
            assert isinstance(value, Primitive)
        self.args = args
    def __call__(self):
        return self.func(*(arg() for arg in self.args))