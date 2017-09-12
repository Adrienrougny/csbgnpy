from csbgnpy.utils import escape_string

class Activity(object):
    def __init__(self, label = None, compartment = None, id = None):
        self.label = label
        self.compartment = compartment
        self.id = id

    def __ne__(self, other):
        return not self == other

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
                self.label == other.label and \
                self.compartment == other.compartment

    def __hash__(self):
        return hash((self.__class__, self.label, self.compartment))

    def __repr__(self):
        return "{}[{} {{}} @ {}]".format(self.__class__.__name__, escape_string(self.label), self.compartment)

class BiologicalActivity(Activity):
    def __init__(self, label = None, compartment = None, uis = None, id = None):
        super().__init__(label, compartment, id)
        self.uis = uis if uis else []

    def add_ui(self, ui):
        if ui not in self.uis:
            self.uis.append(ui)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
                self.label == other.label and \
                self.compartment == other.compartment and \
                self.uis == other.uis

    def __hash__(self):
        return hash((self.__class__, self.label, self.compartment, frozenset(self.uis)))

    def __repr(self):
        return "{}[{} {{{}}} @ {}]".format(self.__class__.__name__, self.label, self.uis, self.compartment)

class Phenotype(Activity):
    pass
