

class Compartment:
    def __init__(self, id = None, label = None):
        self.id = id
        self.label = label

    def __eq__(self, other):
        return isinstance(other, Compartment) and self.label == other.label

    def __hash__(self):
        return hash(self.label)
