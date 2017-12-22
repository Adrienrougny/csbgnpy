from copy import deepcopy

"""Stoech !"""
class Process(object):

    def __init__(self, id = None):
        self.id = id

    def __repr__(self):
        return "{}({},{})".format(self.__class__.__name__, self.reactants, self.products)

    def __eq__(self, other):
        return self.__class__ == other.__class__

    def __hash__(self):
        return hash((self.__class__))

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result

    def __str__(self):
        s = self.__class__.__name__ + "("
        s += "[" + "|".join(["{}:{}".format(stoech, entity) for (stoech, entity) in [(self.reactants.count(i), i) for i in set(self.reactants)]]) + "]"
        s += "[" + "|".join(["{}:{}".format(stoech, entity) for (stoech, entity) in [(self.products.count(i), i) for i in set(self.products)]]) + "]"
        s += ")"
        return s

    def __repr__(self):
        return str(self)

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
        if reactant not in self.reactants:
            self.reactants.append(reactant)

    def add_product(self, product):
        if product not in self.products:
            self.products.append(product)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
                sorted(self.reactants) == sorted(other.reactants) and \
                sorted(self.products) == sorted(other.products)

    def __hash__(self):
        return hash((self.__class__, tuple(sorted(self.reactants)), tuple(sorted(self.products))))

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
