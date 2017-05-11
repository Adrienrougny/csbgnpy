from csbgnpy import *

class Entity:
    def __init__(self, id = None, clazz = None, label = None, compartment = None, components = None, svs = None, uis = None):
        self.id = id
        self.clazz = clazz
        self.label = label
        self.compartment = compartment
        if components is not None:
            self.components = components
        else:
            self.components = set()
        if svs is not None:
            self.svs = svs
        else:
            self.svs = set()
        if uis is None:
            self.uis = set()
        else:
            self.uis = uis

    def add_component(self, component):
        self.components.add(component)

    def add_state_variable(self, sv):
        self.svs.add(sv)

    def add_unit_of_information(self, ui):
        self.uis.add(ui)

    def has_label(self):
        return self.label is not None

    def __eq__(self, other):
        if not isinstance(other, Entity):
            return False
        return self.label == other.label and \
            self.clazz == other.clazz and \
            self.compartment == other.compartment and \
            self.components == other.components and \
            self.svs == other.svs and \
            self.uis == other.uis

    def __hash__(self):
        return hash((self.clazz, self.label, self.compartment, frozenset(self.components), frozenset(self.svs), frozenset(self.uis)))
