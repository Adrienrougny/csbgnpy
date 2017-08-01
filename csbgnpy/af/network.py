from csbgnpy.af.lo import LogicalOperator
from csbgnpy.af.errors import *

class Network(object):
    def __init__(self, activities = None, modulations = None, compartments = None, los = None):
        self.activities = activities if activities is not None else []
        self.modulations = modulations if modulations is not None else []
        self.compartments = compartments if compartments is not None else []
        self.los = los if los is not None else []

    def add_activity(self, act):
        if act not in self.activities:
            self.activities.append(act)

    def add_modulation(self, mod):
        if mod not in self.modulations:
            self.modulations.append(mod)

    def add_compartment(self, comp):
        if comp not in self.compartments:
            self.compartments.append(comp)

    def add_lo(self, op):
        if lo not in self.los:
            self.los.append(op)

    def remove_activity(self, act):
        toremove = set()
        for modulation in self.modulations:
            if modulation.target == act or modulation.source == act:
                toremove.add(modulation)
        for modulation in toremove:
            self.remove_modulation(modulation)
        self.activities.remove(act)

    def remove_modulation(self, modulation):
        self.modulations.remove(modulation)
        if isinstance(modulation.source, LogicalOperator):
            self.remove_lo(modulation.source)

    def remove_compartment(self, compartment):
        self.compartments.remove(compartment)
        for act in self.activities:
            if hasattr(act, "compartment") and act.compartment == compartment:
                act.compartment = None

    def remove_lo(op):
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
