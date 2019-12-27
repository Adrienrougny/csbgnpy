from copy import deepcopy

class Compartment(object):
    """The class to model compartments"""
    def __init__(self, label = None, uis = None, id = None):
        if label:
            self.label = label
        else:
            self.label = "" #by default, label is empty string
        self.uis = uis if uis else []
        self.id = id

    def __eq__(self, other):
        return isinstance(other, Compartment) and \
                self.label == other.label and \
                sorted(self.uis) == sorted(other.uis)

    def __str__(self):
        return "Compartment([{}]{})".format("|".join(sorted([str(ui) for ui in self.uis])), self.label)

    def __lt__(self, other):
        return str(self) < str(other)

    def __gt__(self, other):
        return str(self) > str(other)
