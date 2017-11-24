from copy import deepcopy

class Entity(object):
    """The class to model entity pools"""
    def __init__(self, id = None):
        self.id = id

    def __ne__(self, other):
        return not (self == other)

    def __eq__(self, other):
        return self.__class__ == other.__class__

    def __repr__(self):
        return "%s[]" % self.__class__.__name__

    def __hash__(self):
        return hash((self.__class__))

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result

    def __lt__(self, other):
        return self.__repr__() < other.__repr__()

class EmptySet(Entity):
    """The class to model empty sets"""
    pass

class StatefulEntity(Entity):
    """The class to model entity pools"""
    def __init__(self, label = None, compartment = None, svs = None, uis = None, id = None):
        super().__init__(id)
        self.label = label if label else ""
        self.compartment = compartment
        self.svs = svs if svs else []
        self.uis = uis if uis else []

    def add_sv(self, sv):
        """Adds a state variable to the entity pool

        :param sv: the state variable to be added
        :return: None
        """
        if sv not in self.svs:
            self.svs.append(sv)

    def add_ui(self, ui):
        """Adds a unit of information to the entity pool

        :param ui: the unit of information to be added
        :return: None
        """
        if ui not in self.uis:
            self.uis.append(ui)

    def get_ui(self, val, by_ui = False, by_id = False, by_hash = False):
        """Retrieves a unit of information from the entity pool

        Possible ways of searching for the unit of information are: by object, id, or hash.
        Only the first matching unit of information is retrieved.

        :param val: the value to be searched
        :param by_ui: if True, search by object
        :param by_id: if True, search by id
        :param by_hash: if True, search by hash
        """
        for ui in self.uis:
            if by_ui:
                if ui == val:
                    return ui
            if by_id:
                if ui.id == val:
                    return ui
            if by_hash:
                if hash(ui) == val:
                    return ui
        return None

    def get_sv(self, val, by_sv = False, by_id = False, by_hash = False):
        """Retrieves a state variable from the entity pool

        Possible ways of searching for the state variable are: by object, id, or hash.
        Only the first matching state variable is retrieved.

        :param val: the value to be searched
        :param by_sv: if True, search by object
        :param by_id: if True, search by id
        :param by_hash: if True, search by hash
        """
        for sv in self.svs:
            if by_sv:
                if sv == val:
                    return sv
            if by_id:
                if sv.id == val:
                    return sv
            if by_hash:
                if hash(sv) == val:
                    return sv
        return None

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
            self.label == other.label and \
            self.compartment == other.compartment and \
            set(self.svs) == set(other.svs) and \
            set(self.uis) == set(other.uis)

    def __hash__(self):
        return hash((self.__class__, self.label, self.compartment, frozenset(self.svs), frozenset(self.uis)))

    def __repr__(self):
        return "%s[%s {%s,%s} @ %s]" % (self.__class__.__name__, self.label,
                    self.svs, self.uis,
                    self.compartment.label if self.compartment else "None")

class StatelessEntity(Entity):
    """The class to model stateless entity pools"""
    def __init__(self, label = None, compartment = None, id = None):
        super().__init__(id)
        self.label = label if label else ""
        self.compartment = compartment

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
            self.label == other.label and \
            self.compartment == other.compartment

    def __hash__(self):
        return hash((self.__class__, self.label, self.compartment))

    def __repr__(self):
        return "%s[%s @ %s]" % (self.__class__.__name__, self.label, 
                    self.compartment.label if self.compartment else "None")

class UnspecifiedEntity(StatelessEntity):
    """The class to model pools of unspecified entity pools"""
    pass

class PerturbingAgent(StatelessEntity):
    """The class to model stateless perturbing agent pools"""
    pass

class SimpleChemical(StatefulEntity):
    """The class to model stateless simple chemical pools"""
    pass

class Macromolecule(StatefulEntity):
    """The class to model stateless macromolecule pools"""
    pass

class NucleicAcidFeature(StatefulEntity):
    """The class to model stateless nucleic acid feature pools"""
    pass

class Complex(StatefulEntity):
    """The class to model complex pools"""
    def __init__(self, label = None, compartment = None, svs = None, uis = None, components = None, id = None):
        super().__init__(label, compartment, svs, uis, id)
        self.components = components if components is not None else []

    def add_component(self, component):
        """Adds a subentity to the complex

        :param component: the subentity to be added
        :return: None
        """
        if component not in self.components:
            self.components.append(component)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
            self.label == other.label and \
            self.compartment == other.compartment and \
            set(self.svs) == set(other.svs) and \
            set(self.uis) == set(other.uis) and \
            set(self.components) == set(other.components)

    def __hash__(self):
        return hash((self.__class__, self.label, self.compartment, frozenset(self.svs), frozenset(self.uis), frozenset(self.components)))

    def __repr__(self):
        return "%s[%s {%s,%s,%s} @ %s]" % (self.__class__.__name__, self.label,
                    self.svs, self.uis, self.components,
                    self.compartment.label if self.compartment else "None")

class Multimer(StatefulEntity):
    """The class to model multimer pools"""
    pass

class SimpleChemicalMultimer(Multimer):
    """The class to model simple chemical multimer pools"""
    pass

class MacromoleculeMultimer(Multimer):
    """The class to model macromolecule multimer pools"""
    pass

class NucleicAcidFeatureMultimer(Multimer):
    """The class to model nucleic acid feature pools"""
    pass

class ComplexMultimer(Complex, Multimer):
    """The class to model complex multimer pools"""
    def __init__(self, label = None, compartment = None, svs = None, uis = None, components = None, id = None):
        super().__init__(label, compartment, svs, uis, components, id)

    #maybe not useful:
    def __hash__(self):
        return super().__hash__()
