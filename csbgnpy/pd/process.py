"""Stoech !"""
class Process(object):

    def __init__(self, id = None):
        self.id = id

    def __eq__(self, other):
        return self.__class__ == other.__class__

    def __hash__(self):
        return hash((self.__class__))

class NonStoichiometricProcess(Process):
    def __init__(self, label = None, id = None):
        super().__init__(id)
        self.label = label

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
                self.label == other.label

    def __hash__(self):
        return hash((self.__class__, self.label))

class Phenotype(NonStoichiometricProcess):
    pass

class StoichiometricProcess(Process):
    def __init__(self, reactants = None, products = None, id = None):
        super().__init__(id)
        if reactants is not None:
            self.reactants = reactants
        else:
            self.reactants = set()
        if products is not None:
            self.products = products
        else:
            self.products = set()

    def add_reactant(self, reactant):
        self.reactants.add(reactant)

    def add_product(self, product):
        self.products.add(product)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
                self.reactants == other.reactants and \
                self.products == other.products

    def __hash__(self):
        return hash((self.__class__, frozenset(self.reactants), frozenset(self.products)))

class GenericProcess(StoichiometricProcess):
    pass

class OmittedProcess(StoichiometricProcess):
    pass

class UncertainProcess(StoichiometricProcess):
    pass

class Association(StoichiometricProcess):
    pass

class Dissociation(StoichiometricProcess):
    pass
