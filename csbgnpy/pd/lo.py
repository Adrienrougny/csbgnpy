from copy import deepcopy
# from LogicalOperatorClazz import *

class LogicalOperator(object):
    """The class to model logical operators"""
    def __init__(self, children = None, id = None):
        self.children = children if children else []
        self.id = id

    def add_child(self, child):
        """Adds a child to the logical operator

        :param child: the child to be added
        :return None
        """
        if child not in self.children:
            self.children.append(child)

    def __hash__(self):
        return hash((self.__class__, frozenset(self.children)))

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
        set(self.children) == set(other.children)

    # def __deepcopy__(self, memo):
    #     cls = self.__class__
    #     result = cls.__new__(cls)
    #     memo[id(self)] = result
    #     for k, v in self.__dict__.items():
    #         setattr(result, k, deepcopy(v, memo))
    #     return result

    def __str__(self):
        s = self.__class__.__name__
        s += "(["
        s += "|".join([str(child) for child in self.children])
        s += "])"
        return s

class AndOperator(LogicalOperator):
    """The class to model and operators"""
    pass

class OrOperator(LogicalOperator):
    """The class to model or operators"""
    pass

class NotOperator(LogicalOperator):
    """The class to model not operators"""
    pass


