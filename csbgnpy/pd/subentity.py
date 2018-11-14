from copy import deepcopy

from csbgnpy.pd.sv import UndefinedVar

class SubEntity(object):
    """The class to model subentities"""
    def __init__(self, id = None):
        self.id = id

    def __ne__(self, other):
        return not (self == other)

    def __eq__(self, other):
        return self.__class__ == other.__class__

    def __hash__(self):
        return hash((self.__class__))

    # def __deepcopy__(self, memo):
    #     cls = self.__class__
    #     result = cls.__new__(cls)
    #     memo[id(self)] = result
    #     for k, v in self.__dict__.items():
    #         setattr(result, k, deepcopy(v, memo))
    #     return result

    def __lt__(self, other):
        return str(self) < str(other)

    def __str__(self):
        s = self.__class__.__name__ + "("
        if hasattr(self, "components"):
            s += "[" + "|".join([str(subentity) for subentity in self.components]) + "]"
        if hasattr(self, "uis"):
            s += "[" + "|".join([str(ui) for ui in self.uis]) + "]"
        if hasattr(self, "svs"):
            s += "[" + "|".join([str(sv) for sv in self.svs]) + "]"
        if hasattr(self, "label"):
            s += self.label
        s += ")"
        return s

    def __lt__(self, other):
        return str(self) < str(other)

    def __gt__(self, other):
        return str(self) > str(other)

class StatefulSubEntity(SubEntity):
    """The class to model stateful subentities"""
    def __init__(self, label = None, svs = None, uis = None, id = None):
        super().__init__(id)
        self.label = label
        self.svs = svs if svs else []
        self.uis = uis if uis else []

    def add_sv(self, sv):
        """Adds a state variable to the subentity

        :param sv: the state variable to be added
        :return: None
        """
        if sv not in self.svs:
            if isinstance(sv.var, UndefinedVar) and not sv.var.num:
                max = 0
                for sv2 in self.svs:
                    if isinstance(sv2.var, UndefinedVar) and sv2.var.num > max:
                        max = sv2.var.num
                max += 1
                sv.var.num = max
            self.svs.append(sv)

    def add_ui(self, ui):
        """Adds a unit of information to the subentity

        :param ui: the unit of information to be added
        :return: None
        """
        if ui not in self.uis:
            self.uis.append(ui)

    def get_ui(self, val, by_ui = False, by_id = False, by_hash = False):
        """Retrieves a unit of information from the subentity

        Possible ways of searching for the unit of information are: by object, id, or hash.
        Only the first matching unit of information is retrieved.
        Returns None if no matching unit of information is found.

        :param val: the value to be searched
        :param by_ui: if True, search by object
        :param by_id: if True, search by id
        :param by_hash: if True, search by hash
        :return: the unit of information or None
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
        """Retrieves a state variable from the subentity

        Possible ways of searching for the state variable are: by object, id, or hash.
        Only the first matching state variable is retrieved.
        Returns None if no matching state variable is found.

        :param val: the value to be searched
        :param by_ui: if True, search by object
        :param by_id: if True, search by id
        :param by_hash: if True, search by hash
        :return: the state variable or None
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
            set(self.svs) == set(other.svs) and \
            set(self.uis) == set(other.uis)

    def __hash__(self):
        return hash((self.__class__, self.label, frozenset(self.svs), frozenset(self.uis)))

class StatelessSubEntity(SubEntity):
    """The class to model stateless subentities"""
    def __init__(self, label = None, id = None):
        super().__init__(id)
        self.label = label

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
            self.label == other.label

    def __hash__(self):
        return hash((self.__class__, self.label))

class SubUnspecifiedEntity(StatelessSubEntity):
    """The class to model unspecified subentities"""
    pass

class SubSimpleChemical(StatefulSubEntity):
    """The class to model simple chemical subentities"""
    pass

class SubMacromolecule(StatefulSubEntity):
    """The class to model macromolecule subentities"""
    pass

class SubNucleicAcidFeature(StatefulSubEntity):
    """The class to model nucleic acid feature subentities"""
    pass

class SubComplex(StatefulSubEntity):
    """The class to model complex subentities"""
    def __init__(self, label = None, svs = None, uis = None, components = None, id = None):
        super().__init__(label, svs, uis, id)
        self.components = components if components is not None else []

    def add_component(self, component):
        """Adds a subentity to the complex subentity

        :param component: the subentity to be added
        :return: None
        """
        if component not in self.components:
            self.components.append(component)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
            self.label == other.label and \
            set(self.svs) == set(other.svs) and \
            set(self.uis) == set(other.uis) and \
            set(self.components) == set(other.components)

    def __hash__(self):
        return hash((self.__class__, self.label, frozenset(self.svs), frozenset(self.uis), frozenset(self.components)))

class SubMultimer(StatefulSubEntity):
    """The class to model multimer subentities"""
    pass

class SubSimpleChemicalMultimer(SubMultimer):
    """The class to model simple chemical multimer subentities"""
    pass

class SubMacromoleculeMultimer(SubMultimer):
    """The class to model macromolecule multimer subentities"""
    pass

class SubNucleicAcidFeatureMultimer(SubMultimer):
    """The class to model nucleic acid feature multimer subentities"""
    pass

class SubComplexMultimer(SubComplex, SubMultimer):
    """The class to model nucleic complex multimer subentities"""
    def __init__(self, label = None, svs = None, uis = None, components = None, id = None):
        super().__init__(label, svs, uis, component, id)

    #maybe not useful:
    def __hash__(self):
        return super().__hash__()
