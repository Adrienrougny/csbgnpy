from csbgnpy.pd.lo import LogicalOperator

class Network(object):
    def __init__(self, entities = None, processes = None, modulations = None, compartments = None, los = None):
        if entities is not None:
            self.entities = entities
        else:
            self.entities = set()
        if processes is not None:
            self.processes = processes
        else:
            self.processes = set()
        if modulations is not None:
            self.modulations = modulations
        else:
            self.modulations = set()
        if compartments is not None:
            self.compartments = compartments
        else:
            self.compartments = set()
        if los is not None:
            self.los = los
        else:
            self.los = set()

    def add_process(self, proc):
        self.processes.add(proc)

    def add_entity(self, entity):
        self.entities.add(entity)

    def add_modulation(self, mod):
        self.modulations.add(mod)

    def add_compartment(self, comp):
        self.compartments.add(comp)

    def add_lo(self, op):
        self.lo(op)

    def remove_process(self, process):
        self.processes.remove(process)
        for modulation in self.modulations:
            if modulation.target == process:
                self.remove_modulation(modulation)

    def remove_entity(self, entity):
        self.entities.remove(entity)
        for process in self.processes:
            if entity in process.reactants or entity in process.products:
                self.remove_process(process)
        for modulation in self.modulations:
            if modulation.source == entity:
                self.remove_modulation(modulation)

    def remove_compartment(self, compartment):
        self.compartments.remove(compartment)

    def remove_lo(self, op):
        self.los.remove(op)
        for child in self.children:
            if isinstance(child, LogicalOperator):
                self.remove_lo(child)
        for modulation in self.modulations:
            if modulation.source == op:
                self.remove(modulation)

    def remove_modulation(self, modulation):
        self.modulations.remove(modulation)
        if isinstance(modulation.source, LogicalOperator):
            self.remove_lo(modulation.source)

    def union(self, other):
        new = Network()
        new.entities = self.entities.union(other.entities)
        new.processes = self.processes.union(other.processes)
        new.modulations = self.modulations.union(other.modulations)
        new.los = self.los.union(other.los)
        new.compartments = self.compartments.union(other.compartments)
        return new
