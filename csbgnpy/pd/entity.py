class Entity(object):
    def __init__(self, id = None):
        self.id = id

    def __eq__(self, other):
        return self.__class__ == other.__class__

class EmptySet(Entity):
    pass

class StatefulEntity(Entity):
    def __init__(self, label = None, compartment = None, svs = None, uis = None, id = None):
        super().__init__(id)
        self.label = label
        self.compartment = compartment
        if svs is not None:
            self.svs = svs
        else:
            self.svs = set()
        if uis is None:
            self.uis = set()
        else:
            self.uis = uis

    def add_sv(self, sv):
        self.svs.add(sv)

    def add_ui(self, ui):
        self.uis.add(ui)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
            self.label == other.label and \
            self.compartment == other.compartment and \
            self.svs == other.svs and \
            self.uis == other.uis

    def __hash__(self):
        return hash((self.__class__, self.label, self.compartment, frozenset(self.svs), frozenset(self.uis)))

class StatelessEntity(Entity):
    def __init__(self, label = None, compartment = None, id = None):
        super().__init__(id)
        self.label = label
        self.compartment = compartment

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
            self.label == other.label and \
            self.compartment == other.compartment and \

class UnspecifiedEntity(StatelessEntity):
    pass

class PerturbingAgent(StatelessEntity):
    pass

class SimpleChemical(StatefulEntity):
    pass

class Macromolecule(StatefulEntity):
    pass

class NucleicAcidFeature(StatefulEntity):
    pass

class Complex(StatefulEntity):
    def __init__(self, label = None, compartment = None, svs = None, uis = None, components = None, id = None):
        super().__init__(self, label, compartment, svs, uis, id)
        if components is not None:
            self.components = components
        else:
            self.components = set()

    def add_component(self, component):
        self.components.add(component)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
            self.label == other.label and \
            self.compartment == other.compartment and \
            self.svs == other.svs and \
            self.uis == other.uis and \
            self.components == other.components

    def __hash__(self):
        return hash((self.__class__, self.label, self.compartment, frozenset(self.svs), frozenset(self.uis), frozenset(self.components)))

class Multimer(StatefulEntity):
    pass

class SimpleChemicalMultimer(Multimer):
    pass

class MacromoleculeMultimer(Multimer):
    pass

class NucleicAcidFeatureMultimer(Multimer):
    pass

class ComplexMultimer(Multimer):
    def __init__(self, label = None, compartment = None, svs = None, uis = None, components = None, id = None):
        super().__init__(self, label, compartment, svs, uis, id)
        if components is not None:
            self.components = components
        else:
            self.components = set()
    def add_component(self, component):
        self.components.add(component)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
            self.label == other.label and \
            self.compartment == other.compartment and \
            self.svs == other.svs and \
            self.uis == other.uis and \
            self.components == other.components

    def __hash__(self):
        return hash((self.__class__, self.label, self.compartment, frozenset(self.svs), frozenset(self.uis), frozenset(self.components)))
