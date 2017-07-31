from enum import Enum

class UnitOfInformationActivityType(Enum):
    MACROMOLECULE = "macromolecule"
    NUCLEIC_ACID_FEATURE = "nucleic acid feature"
    SIMPLE_CHEMICAL = "simple chemical"
    UNSPECIFIED_ENTITY = "unspecified entity"
    COMPLEX = "complex"
    PERTURBATION = "perturbation"

class UnitOfInformation(object):
    def __init__(self, id = None):
        self.id = id

class UnitOfInformationActivity(UnitOfInformation):
    def __init__(self, label = None, type = None, id = None):
        super().__init__(id)
        self.label = label
        self.type = type

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
                self.label == other.label and \
                self.type == other.type

    def __hash__(self):
        return hash((self.__class__, self.label, self.type))

    def __repr__(self):
        return "{}[{}:{}]".format(self.__class__.__name__, self.type.name, self.label)

class UnitOfInformationCompartment(UnitOfInformation):
    def __init__(self, prefix = None, label = None, id = None):
        super().__init__(id)
        self.prefix = prefix
        self.label = label

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
                self.prefix == other.prefix and \
                self.label == other.label

    def __hash__(self):
        return hash((self.__class__, self.prefix, self.label))
