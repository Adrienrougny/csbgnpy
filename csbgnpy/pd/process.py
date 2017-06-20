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
        self.reactants = reactants if reactants is not None else []
        self.products = products if products is not None else []

    def add_reactant(self, reactant):
        self.reactants.append(reactant)

    def add_product(self, product):
        self.products.append(product)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
                frozenset(self.reactants) == frozenset(other.reactants) and \
                frozenset(self.products) == frozenset(other.products)

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
