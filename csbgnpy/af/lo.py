class LogicalOperator(object):
    """The abstract class to model logical operators"""
    def __init__(self, children = None, id = None):
        self.children = children if children else []
        self.id = id

    def add_child(self, child):
        """Add a child to the logical operator

        :param child: the child to be added
        :return: None
        """
        if child not in self.children:
            self.children.append(child)

    def __hash__(self):
        return hash((self.__class__, frozenset(self.children)))

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
        set(self.children) == set(other.children)

    def __repr__(self):
        return "{}".format(self.__class__.__name__)

class AndOperator(LogicalOperator):
    """The class to model AND operators"""
    pass

class OrOperator(LogicalOperator):
    """The class to model OR operators"""
    pass

class NotOperator(LogicalOperator):
    """The class to model NOT operators"""
    pass

class DelayOperator(LogicalOperator):
    """The class to model DELAY operators"""
    pass


