from csbgnpy.af.lo import LogicalOperator
from csbgnpy.af.errors import *

class Network(object):
    """The class to model the cSBGN AF maps"""
    def __init__(self, activities = None, modulations = None, compartments = None, los = None):
        self.activities = activities if activities is not None else []
        self.modulations = modulations if modulations is not None else []
        self.compartments = compartments if compartments is not None else []
        self.los = los if los is not None else []

    def add_activity(self, act):
        """Adds an activity to the map

        :param act: the activity to be added
        :return: None
        """
        if act not in self.activities:
            self.activities.append(act)

    def add_modulation(self, mod):
        """Adds a modulation to the map

        :param mod: the modulation to be added
        :return: None
        """
        if mod not in self.modulations:
            self.modulations.append(mod)

    def add_compartment(self, comp):
        """Adds a comparment to the map

        :param comp: the compartment to be added
        :return: None
        """
        if comp not in self.compartments:
            self.compartments.append(comp)

    def add_lo(self, op):
        """Adds a logical operator to the map

        :param op: the logical operator to be added
        :return: None
        """
        if op not in self.los:
            self.los.append(op)

    def remove_activity(self, act):
        """Removes an activity from the map

        Also removes any modulation whose source or taget is the activity

        :param act: the activity to be removed
        :return: None
        """
        toremove = set()
        for modulation in self.modulations:
            if modulation.target == act or modulation.source == act:
                toremove.add(modulation)
        for modulation in toremove:
            self.remove_modulation(modulation)
        self.activities.remove(act)

    def remove_modulation(self, modulation):
        """Removes a modulation from the map

        If the source of the modulation is a logical operators, also removes that logical operator

        :param modulation: the modulation to be removed
        :return: None
        """
        self.modulations.remove(modulation)
        if isinstance(modulation.source, LogicalOperator):
            self.remove_lo(modulation.source)

    def remove_compartment(self, compartment):
        """Removes a compartment from the map

        :param compartment: the compartment to be removed
        :return: None
        """
        self.compartments.remove(compartment)
        for act in self.activities:
            if hasattr(act, "compartment") and act.compartment == compartment:
                act.compartment = None

    def remove_lo(op):
        """Removes a logical operator from the map

        Also removes any of its child that is a logical operator, and any modulation whose source is the logical operator

        :param op: the logical operator to be removed
        :return: None
        """
        toremove = set()
        for child in self.children:
            if isinstance(child, LogicalOperator):
                toremove.add(child)
        for child in toremove:
            self.remove_lo(child)
        toremove = set()
        for modulation in self.modulations:
            if modulation.source == op:
                toremove.add(modulation)
        for modulation in toremove:
            self.remove_modulation(modulation)
        self.los.remove(op)

    def get_activity(self, val, by_object = False, by_id = False, by_label = False, by_hash = False):
        """Retrieves an activity from the map

        Possible ways of searching for the activity are: by object, id, label or hash.
        Only first the matching activity is retrieved.


        :param val: the value to be searched
        :param by_object: if True, search by object
        :param by_id: if True, search by id
        :param by_label: if True, search by label
        :param by_hash: if True, search by hash
        """
        for a in self.activities:
            if by_object:
                if a == val:
                    return a
            if by_id:
                if a.id == val:
                    return a
            if by_label:
                if a.label == val:
                    return a
            if by_hash:
                if hash(a) == val:
                    return a
        raise ActivityLookupError(a)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
                set(self.activities) == set(other.activities) and \
                set(self.compartments) == set(other.compartments) and \
                set(self.los) == set(other.los) and \
                set(self.modulations) == set(other.modulations)
