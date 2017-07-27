from csbgnpy.pd.lo import LogicalOperator

class Network(object):
    def __init__(self, entities = None, processes = None, modulations = None, compartments = None, los = None):
        self.entities = entities if entities is not None else []
        self.processes = processes if processes is not None else []
        self.modulations = modulations if modulations is not None else []
        self.compartments = compartments if compartments is not None else []
        self.los = los if los is not None else []

    def add_process(self, proc):
        if proc not in self.processes:
            self.processes.append(proc)

    def add_entity(self, entity):
        if entity not in self.entities:
            self.entities.append(entity)

    def add_modulation(self, mod):
        if mod not in self.modulations:
            self.modulations.append(mod)

    def add_compartment(self, comp):
        if comp not in self.compartments:
            self.compartments.append(comp)

    def add_lo(self, op):
        if op not in self.los:
            self.los.append(op)

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
        for entity in self.entities:
            if hasattr(entity, "compartment") and entity.compartment == compartment:
                entity.compartment = None

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

    def get_entity(self, val, by_object = False, by_id = False, by_label = False, by_hash = False):
        for e in self.entities:
            if by_object:
                if e == val:
                    return e
            if by_id:
                if e.id == val:
                    return e
            if by_label:
                if hasattr(e, "label"):
                    if e.label == val:
                        return e
            if by_hash:
                if hash(e) == val:
                    return e
        return None

    def union(self, other):
        new = Network()
        new.entities = list(set(self.entities).union(set(other.entities)))
        new.processes = list(set(self.processes).union(set(other.processes)))
        new.modulations = list(set(self.modulations).union(set(other.modulations)))
        new.los = list(set(self.los).union(set(other.los)))
        new.compartments = list(set(self.compartments).union(set(other.compartments)))
        return new

    def intersection(self, other):
        new = Network()
        new.entities = list(set(self.entities).intersection(set(other.entities)))
        new.processes = list(set(self.processes).intersection(set(other.processes)))
        new.modulations = list(set(self.modulations).intersection(set(other.modulations)))
        new.los = list(set(self.los).intersection(set(other.los)))
        new.compartments = list(set(self.compartments).intersection(set(other.compartments)))
        return new

    def __eq__(self, other):
        return isinstance(other, Network) and \
                set(self.entities) == set(other.entities) and \
                set(self.processes) == set(other.processes) and \
                set(self.compartments) == set(other.compartments) and \
                set(self.los) == set(other.los) and \
                set(self.modulations) == set(other.modulations)

