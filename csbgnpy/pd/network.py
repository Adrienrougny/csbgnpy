from copy import deepcopy
from csbgnpy.pd.lo import LogicalOperator
from csbgnpy.pd.entity import Entity

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
            for reactant in proc.reactants:
                self.add_entity(reactant)
            for product in proc.products:
                self.add_entity(product)

    def add_entity(self, entity):
        if entity not in self.entities:
            self.entities.append(entity)
            if hasattr(entity, "compartment"):
                self.add_compartment(entity.compartment)

    def add_modulation(self, mod):
        if mod not in self.modulations:
            self.modulations.append(mod)
        source = mod.source
        target = mod.target
        if isinstance(source, Entity):
            self.add_entity(source)
        elif isinstance(source, LogicalOperator):
            self.add_lo(source)
        self.add_process(target)

    def add_compartment(self, comp):
        if comp not in self.compartments:
            self.compartments.append(comp)

    def add_lo(self, op):
        if op not in self.los:
            self.los.append(op)
            for child in op.children:
                if isinstance(child, Entity):
                    self.add_entity(child)
                elif isinstance(child, LogicalOperator):
                    self.add_lo(source)

    def remove_process(self, process):
        for modulation in self.modulations:
            if modulation.target == process:
                self.remove_modulation(modulation)
        self.processes.remove(process)

    def remove_entity(self, entity):
        toremove = set()
        for process in self.processes:
            if entity in process.reactants or entity in process.products:
                toremove.add(process)
        for process in toremove:
            self.remove_process(process)
        toremove = set()
        for modulation in self.modulations:
            if modulation.source == entity:
                toremove.add(modulation)
        for modulation in toremove:
            self.remove_modulation(modulation)
        self.entities.remove(entity)

    def remove_compartment(self, compartment):
        self.compartments.remove(compartment)
        for entity in self.entities:
            if hasattr(entity, "compartment") and entity.compartment == compartment:
                entity.compartment = None

    def remove_lo(self, op):
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

    def remove_modulation(self, modulation):
        self.modulations.remove(modulation)
        if isinstance(modulation.source, LogicalOperator):
            self.remove_lo(modulation.source)

    def get_compartment(self, val, by_compartment = False, by_id = False, by_label = False, by_hash = False):
        for c in self.compartments:
            if by_compartment:
                if c == val:
                    return c
            if by_id:
                if c.id == val:
                    return c
            if by_label:
                if hasattr(c, "label"):
                    if c.label == val:
                        return c
            if by_hash:
                if hash(c) == val:
                    return c
        return None


    def get_entity(self, val, by_entity = False, by_id = False, by_label = False, by_hash = False):
        for e in self.entities:
            if by_entity:
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
        for e in self.entities:
            new.add_entity(deepcopy(e))
        for p in self.processes:
            new.add_process(deepcopy(p))
        for m in self.modulations:
            new.add_modulation(deepcopy(m))
        for c in self.compartments:
            new.add_compartment(deepcopy(m))
        for o in self.los:
            new.add_lo(deepcopy(o))
        for e in other.entities:
            new.add_entity(deepcopy(e))
        for p in other.processes:
            new.add_process(deepcopy(p))
        for m in other.modulations:
            new.add_modulation(deepcopy(m))
        for c in other.compartments:
            new.add_compartment(deepcopy(m))
        for o in other.los:
            new.add_lo(deepcopy(o))
        # new.entities = list(set(self.entities).union(set(other.entities)))
        # new.processes = list(set(self.processes).union(set(other.processes)))
        # new.modulations = list(set(self.modulations).union(set(other.modulations)))
        # new.los = list(set(self.los).union(set(other.los)))
        # new.compartments = list(set(self.compartments).union(set(other.compartments)))
        return new

    def intersection(self, other):
        new = Network()
        for e in self.entities:
            if e in other.entities:
                new.add_entity(deepcopy(e))
        for p in self.processes:
            if p in other.processes:
                new.add_process(deepcopy(p))
        for m in self.modulations:
            if m in other.modulations:
                new.add_modulation(deepcopy(m))
        for c in self.compartment:
            if c in other.compartments:
                new.add_compartment(deepcopy(c))
        for o in self.los:
            if o in other.los:
                new.add_compartment(deepcopy(c))
        return new
        # new.entities = list(set(self.entities).intersection(set(other.entities)))
        # new.processes = list(set(self.processes).intersection(set(other.processes)))
        # new.modulations = list(set(self.modulations).intersection(set(other.modulations)))
        # new.los = list(set(self.los).intersection(set(other.los)))
        # new.compartments = list(set(self.compartments).intersection(set(other.compartments)))
        return new

    def difference(self, other):
        new = Network()
        for m in self.modulations:
            if m not in other.modulations:
                new.add_modulation(deepcopy(m))
        # new.entities = list(set(self.entities).difference(set(other.entities)))
        # new.processes = list(set(self.processes).difference(set(other.processes)))
        # new.modulations = list(set(self.modulations).difference(set(other.modulations)))
        # new.los = list(set(self.los).difference(set(other.los)))
        # new.compartments = list(set(self.compartments).difference(set(other.compartments)))
        return new

    def __eq__(self, other):
        return isinstance(other, Network) and \
                set(self.entities) == set(other.entities) and \
                set(self.processes) == set(other.processes) and \
                set(self.compartments) == set(other.compartments) and \
                set(self.los) == set(other.los) and \
                set(self.modulations) == set(other.modulations)

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result
