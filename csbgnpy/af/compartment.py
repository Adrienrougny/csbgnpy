class Compartment(object):
    def __init__(self, label = None, id = None):
        self.label = label
        self.id = id

    def __eq__(self, other):
        return isinstance(other, Compartment) and self.label == other.label

    def __repr__(self):
        return "Compartment[%s (%s)]" % (self.label, self.id)

    def __hash__(self):
        return hash(self.label)