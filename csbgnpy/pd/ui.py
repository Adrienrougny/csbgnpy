class UnitOfInformation:

    def __init__(self, id = None, prefix = None, label = None):
        self.id = id
        self.prefix = prefix
        self.label = label

    def __eq__(self, other):
        return isinstance(other, UnitOfInformation) and \
                self.prefix == other.prefix and \
                self.label == other.label

    def __hash__(self):
        return hash((self.prefix, self.label))
