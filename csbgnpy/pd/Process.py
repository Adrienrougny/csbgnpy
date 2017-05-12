from csbgnpy import *

"""Stoech !"""
class Process:

    def __init__(self, id = None, clazz = None, label = None, reactants = None, products = None):
        self.id = id
        self.clazz = clazz
        self.label = label
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
        return isinstance(other, Process) and \
                self.clazz == other.clazz and \
                self.label == other.label and \
                self.reactants == other.reactants and \
                self.products == other.products

    def __hash__(self):
        return hash((self.clazz, self.label, frozenset(self.reactants), frozenset(self.products)))
