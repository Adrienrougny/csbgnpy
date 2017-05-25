# from LogicalOperatorClazz import *

class LogicalOperator(object):
    def __init__(self, children = None, id = None):
        if children is None:
            self.children = set()
        else:
            self.children = children
        self.id = id

    def add_child(self, child):
        self.children.add(child)

    def __hash__(self):
        hashcode = hash(self.__class__)
        for child in self.children:
            hashcode += hash(child)
        return hashcode

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
        self.children == other.children

class AndOperator(LogicalOperator):
    pass

class OrOperator(LogicalOperator):
    pass

class NotOperator(LogicalOperator):
    pass


