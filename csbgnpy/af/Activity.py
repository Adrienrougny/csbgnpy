from csbgnpy import *

class Activity:
    def __init__(self, id = None, clazz = None, label = None, compartment = None, ui = None):
        self.id = id
        self.clazz = clazz
        self.label = label
        self.compartment = compartment
        self.ui = ui

    def has_label(self):
        return self.label is not None

    def __eq__(self, other):
        if not isinstance(other, Activity):
            return False
        return self.label == other.label and \
            self.clazz == other.clazz and \
            self.compartment == other.compartment and \
            self.ui == other.ui

    def __hash__(self):
        return hash((self.clazz, self.label, self.compartment, self.ui))
