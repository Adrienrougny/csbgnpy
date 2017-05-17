# from LogicalOperatorClazz import *

class LogicalOperatorNode:
    def __init__(self, clazz = None, children = None):
        self.clazz = clazz
        if children is None:
            self.children = set()
        else:
            self.children = children

    def add_child(self, child):
        self.children.add(child)

    def __hash__(self):
        hashcode = hash(self.clazz)
        for child in self.children:
            hashcode += hash(child)
        return hashcode

    def __eq__(self, other):
        return self.clazz == other.clazz and self.children == other.children
