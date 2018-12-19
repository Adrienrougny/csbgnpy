from csbgnpy.utils import escape_string

class UnitOfInformation(object):
    """The class to model units of information"""
    def __init__(self, prefix = None, label = None, id = None):
        self.prefix = prefix
        self.label = label
        self.id = id

    def __eq__(self, other):
        return isinstance(other, UnitOfInformation) and \
                self.prefix == other.prefix and \
                self.label == other.label

    def __hash__(self):
        return hash((self.prefix, self.label))

    def __str__(self):
        s = escape_string(self.label)
        if self.prefix:
            s = escape_string(self.prefix) + ":" + s
        return s

    def __lt__(self, other):
        return str(self) < str(other)

    def __gt__(self, other):
        return str(self) > str(other)


