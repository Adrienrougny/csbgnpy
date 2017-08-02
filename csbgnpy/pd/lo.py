from copy import deepcopy
# from LogicalOperatorClazz import *

class LogicalOperator(object):
    def __init__(self, children = None, id = None):
        self.children = children if children else []

    def add_child(self, child):
        if child not in self.children:
            self.children.append(child)

    def __hash__(self):
        return hash((self.__class__, frozenset(self.children)))

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
        set(self.children) == set(other.children)

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result

class AndOperator(LogicalOperator):
    pass

class OrOperator(LogicalOperator):
    pass

class NotOperator(LogicalOperator):
    pass


