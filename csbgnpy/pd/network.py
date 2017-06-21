from csbgnpy.pd.lo import LogicalOperator

class Network(object):
    def __init__(self, entities = None, processes = None, modulations = None, compartments = None, los = None):
        if entities is not None:
            self.entities = entities
        else:
            self.entities = set()
        self.processes = processes if processes is not None else []
        self.modulations = modulations if modulations is not None else []
        if compartments is not None:
            self.compartments = compartments
        else:
            self.compartments = set()
        if los is not None:
            self.los = los
        else:
            self.los = set()

    def add_process(self, proc):
        self.processes.append(proc)

    def add_entity(self, entity):
        self.entities.add(entity)

    def add_modulation(self, mod):
        self.modulations.append(mod)

    def add_compartment(self, comp):
        self.compartments.add(comp)

    def add_lo(self, op):
        self.lo(op)

    def remove_process(self, process):
        for modulation in self.modulations:
            if modulation.target == process:
                self.remove_modulation(modulation)
        self.processes.remove(process)

    def remove_entity(self, entity):
        for process in self.processes:
            if entity in process.reactants or entity in process.products:
                self.remove_process(process)
        for modulation in self.modulations:
            if modulation.source == entity:
                self.remove_modulation(modulation)
        self.entities.remove(entity)

    def remove_compartment(self, compartment):
        self.compartments.remove(compartment)

    def remove_lo(self, op):
        for child in self.children:
            if isinstance(child, LogicalOperator):
                self.remove_lo(child)
        for modulation in self.modulations:
            if modulation.source == op:
                self.remove_modulation(modulation)
        self.los.remove(op)

    def remove_modulation(self, modulation):
        self.modulations.remove(modulation)
        if isinstance(modulation.source, LogicalOperator):
            self.remove_lo(modulation.source)

    def union(self, other):
        new = Network()
        new.entities = self.entities.union(other.entities)
        new.processes = list(set(self.processes).union(other.processes))
        new.modulations = list(set(self.modulations).union(other.modulations))
        new.los = self.los.union(other.los)
        new.compartments = self.compartments.union(other.compartments)
        return new

    def intersection(self, other):
        new = Network()
        new.entities = self.entities.intersection(other.entities)
        new.processes = list(set(self.processes).intersection(other.processes))
        new.modulations = list(set(self.modulations).intersection(other.modulations))
        new.los = self.los.intersection(other.los)
        new.compartments = self.compartments.intersection(other.compartments)
        return new

    def __eq__(self, other):
        return isinstance(other, Network) and \
                self.entities == other.entities and \
                frozenset(self.processes) == frozenset(other.processes) and \
                self.compartments == other.compartments and \
                self.los == other.los and \
                frozenset(self.modulations) == frozenset(other.modulations)

