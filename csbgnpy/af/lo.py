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

class AndOperator(LogicalOperator):
    pass

class OrOperator(LogicalOperator):
    pass

class NotOperator(LogicalOperator):
    pass


