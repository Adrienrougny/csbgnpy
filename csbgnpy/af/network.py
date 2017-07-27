from csbgnpy.af.lo import LogicalOperator

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
        if mod not is self.modulations:
            self.modulations.append(mod)

    def add_compartment(self, comp):
        if comp not in self.compartments:
            self.compartments.append(comp)

    def add_lo(self, op):
        if lo not in self.los:
            self.los.append(op)

    def remove_activity(self, act):
        for modulation in self.modulations:
            if modulation.target == act or modulation.source == act:
                self.remove_modulation(act)
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
        for child in self.children:
            if isinstance(child, LogicalOperator):
                self.remove_lo(child)
        for modulation in self.modulations:
            if modulation.source == op:
                self.remove_modulation(modulation)
        self.los.remove(op)
