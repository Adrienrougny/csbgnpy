from csbgnpy.utils import escape_string

class Process(object):
    """The class to model processes"""
    def __init__(self, id = None):
        self.id = id

    def __eq__(self, other):
        return self.__class__ == other.__class__

    def __hash__(self):
        return hash((self.__class__))

    def __str__(self):
        s = self.__class__.__name__ + "("
        if hasattr(self, "reactants"):
            reacs = []
            for reac in self.reactants:
                if reac not in reacs:
                    reacs.append(reac)
            s += "[" + "|".join(["{}:{}".format(stoech, entity) for (stoech, entity) in sorted([(self.reactants.count(i), i) for i in reacs], key = lambda tup: str(tup[1]))]) + "]"
        if hasattr(self, "products"):
            prods = []
            for prod in self.products:
                if prod not in prods:
                    prods.append(prod)
            s += "[" + "|".join(["{}:{}".format(stoech, entity) for (stoech, entity) in sorted([(self.products.count(i), i) for i in prods], key = lambda tup: str(tup[1]))]) + "]"
        if hasattr(self, "label"):
            s += escape_string(self.label)
        s += ")"
        return s

    def __lt__(self, other):
        return str(self) < str(other)

    def __gt__(self, other):
        return str(self) > str(other)

class NonStoichiometricProcess(Process):
    """The class to model non stoichiometric processes"""
    def __init__(self, label = None, id = None):
        super().__init__(id)
        self.label = label

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
                self.label == other.label

class Phenotype(NonStoichiometricProcess):
    """The class to model phenotypes"""
    pass

class StoichiometricProcess(Process):
    """The class to model stoichiometric processes"""
    def __init__(self, reactants = None, products = None, id = None):
        super().__init__(id)
        self.reactants = reactants if reactants is not None else []
        self.products = products if products is not None else []

    def add_reactant(self, reactant, stoichiometry = 1):
        """Adds a reactant to the process

        :param reactant: the reactant to be added
        :param stoichiometry: the number of times the reactant should be added, i.e. the stoichiometry of the reactant in the process
        :return: None
        """
        for i in range(stoichiometry):
            self.reactants.append(reactant)

    def add_product(self, product, stoichiometry = 1):
        """Adds a product to the process

        :param product: the product to be added
        :param stoichiometry: the number of times the product should be added, i.e. the stoichiometry of the product in the process
        :return: None
        """
        for i in range(stoichiometry):
            self.products.append(product)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
                sorted(self.reactants) == sorted(other.reactants) and \
                sorted(self.products) == sorted(other.products)

class GenericProcess(StoichiometricProcess):
    """The class to model generic processes"""
    pass

class OmittedProcess(StoichiometricProcess):
    """The class to model omitted processes"""
    pass

class UncertainProcess(StoichiometricProcess):
    """The class to model unertain processes"""
    pass

class Association(StoichiometricProcess):
    """The class to model associations"""
    pass

class Dissociation(StoichiometricProcess):
    """The class to model dissociations"""
    pass
