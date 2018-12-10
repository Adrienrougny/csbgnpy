from copy import deepcopy
from collections import defaultdict
import re

from csbgnpy.pd.lo import *
from csbgnpy.pd.entity import *
from csbgnpy.pd.modulation import *
from csbgnpy.pd.ui import *
from csbgnpy.utils import get_object
from csbgnpy.pd.io.sbgntxt import Parser

class Network(object):
    """The class to model SBGN PD maps"""
    def __init__(self, entities = None, processes = None, modulations = None, compartments = None, los = None):
        self.entities = entities if entities is not None else []
        self.processes = processes if processes is not None else []
        self.modulations = modulations if modulations is not None else []
        self.compartments = compartments if compartments is not None else []
        self.los = los if los is not None else []

    @property
    def macromolecules(self):
        return [e for e in self.entities if isinstance(e, Macromolecule)]

    @property
    def associations(self):
        return [p for p in self.processes if insinstance(p, Association)]

    @property
    def transcriptions(self):
        transcriptions = []
        for p in self.processes:
            if isinstance(p.reactants[0], EmptySet) and isinstance(p.products[0], NucleicAcidFeature) and UnitOfInformation("ct", "mRNA") in p.products[0].uis:
                for m in self.modulations:
                    if m.target == p and isinstance(m, NecessaryStimulation) and isinstance(m.source, NucleicAcidFeature) and UnitOfInformation("ct", "gene") in m.source.uis:
                        transcriptions.append(p)
        return transcriptions

    @property
    def translations(self):
        translations = []
        for p in self.processes:
            if isinstance(p.reactants[0], EmptySet) and isinstance(p.products[0], Macromolecule):
                for m in self.modulations:
                    if m.target == p and isinstance(m, NecessaryStimulation) and isinstance(m.source, NucleicAcidFeature) and UnitOfInformation("ct", "mRNA") in m.source.uis:
                        translations.append(p)
        return translations

    def add_process(self, proc):
        """Adds a process to the map

        Also recursively adds the reactants and the products if they do not already belong to the map.

        :param proc: the process to be added (object or sbgntxt string)
        """
        if isinstance(proc, str):
            parser = Parser()
            proc =  parser.process.parseString(proc)[0]
        if proc not in self.processes:
            if hasattr(proc, "reactants"):
                reactants = []
                for reactant in proc.reactants:
                    existent_reactant = self.get_entity(reactant, by_entity = True)
                    if existent_reactant:
                        reactants.append(existent_reactant)
                    else:
                        self.add_entity(reactant)
                        reactants.append(reactant)
                proc.reactants = reactants

            if hasattr(proc, "products"):
                products = []
                for product in proc.products:
                    existent_product = self.get_entity(product, by_entity = True)
                    if existent_product:
                        products.append(existent_product)
                    else:
                        products.append(product)
                        self.add_entity(product)
                proc.products = products
            self.processes.append(proc)

    def add_entity(self, entity):
        """Adds an entity pool to the map

        Also recursively adds the compartment if it does not already belong to the map.

        :param entity: the entity to be added (object or sbgntxt string)
        """
        if isinstance(entity, str):
            parser = Parser()
            entity =  parser.entity.parseString(entity)[0]
        if entity not in self.entities:
            self.entities.append(entity)
            if hasattr(entity, "compartment") and entity.compartment:
                existent_compartment = self.get_compartment(entity.compartment, by_compartment  = True)
                if existent_compartment:
                    entity.compartment = existent_compartment
                else:
                    self.add_compartment(entity.compartment)

    def add_modulation(self, mod):
        """Adds an modulation to the map

        Also recursively adds the source and the target if they do not already belong to the map.

        :param mod: the modulation to be added (object or sbgntxt string)
        """
        if isinstance(mod, str):
            parser = Parser()
            mod =  parser.modulation.parseString(mod)[0]
        if mod not in self.modulations:
            source = mod.source
            target = mod.target
            if isinstance(source, Entity):
                existent_source = self.get_entity(source, by_entity = True)
                if existent_source:
                    mod.source = existent_source
                else:
                    self.add_entity(source)
            elif isinstance(source, LogicalOperator):
                existent_source = self.get_lo(source, by_lo = True)
                if existent_source:
                    mod.source = existent_source
                else:
                    self.add_lo(source)
            existent_target = self.get_process(target, by_process = True)
            if existent_target:
                mod.target = existent_target
            else:
                self.add_process(target)
            self.modulations.append(mod)

    def add_compartment(self, comp):
        """Adds a compartment to the map

        :param comp: the compartment to be added (object or sbgntxt string)
        """
        if isinstance(comp, str):
            parser = Parser()
            comp =  parser.compartment.parseString(comp)[0]
        if comp not in self.compartments:
            self.compartments.append(comp)

    def add_lo(self, op):
        """Adds a logical operator to the map

        Also recursively adds the children if they do not already belong to the map.

        :param op: the logical operator to be added (object or sbgntxt string)
        """
        if isinstance(op, str):
            parser = Parser()
            op =  parser.lo.parseString(op)[0]
        if op not in self.los:
            for child in op.children:
                if isinstance(child, Entity):
                    existent_child = self.get_entity(child, by_entity = True)
                    if existent_child:
                        op.children[op.children.index(child)] = existent_child
                    else:
                        self.add_entity(child)
                elif isinstance(child, LogicalOperator):
                    existent_child = self.get_lo(child, by_lo = True)
                    if existent_child:
                        op.children[op.children.index(child)] = existent_child
                    else:
                        self.add_lo(child)
            self.los.append(op)

    def remove_process(self, process):
        """Removes a process from the map

        Also removes the modulations targetting this process.

        :param process: the process to be removed
        """
        if isinstance(process, str):
            parser = Parser()
            process =  parser.process.parseString(process)[0]
        for modulation in self.modulations:
            if modulation.target == process:
                self.remove_modulation(modulation)
        self.processes.remove(process)

    def remove_entity(self, entity):
        """Removes an entity pool from the map

        Also removes the processes consuming or producing this entity pool, an the modulations departing from it.

        :param entity: the entity pool to be removed
        """
        if isinstance(entity, str):
            parser = Parser()
            entity =  parser.entity.parseString(entity)[0]
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
        """Removes a compartment from the map

        Also sets the compartment attribute of the entity pools belonging to this compartment to None.

        :param compartment: the compartment to be removed
        """
        if isinstance(compartment, str):
            parser = Parser()
            compartment =  parser.compartment.parseString(compartment)[0]
        self.compartments.remove(compartment)
        for entity in self.entities:
            if hasattr(entity, "compartment") and entity.compartment == compartment:
                entity.compartment = None

    def remove_lo(self, op):
        """Removes a logical operator from the map

        Also removes all children of the logical operators that are themselves logical operators, if those are not the children of other operators or the source of a modualtion.

        :param op: the logical operator to be removed
        """
        if isinstance(op, str):
            parser = Parser()
            op =  parser.lo.parseString(op)[0]
        self.los.remove(op)
        toremove = set()
        for child in op.children:
            if isinstance(child, LogicalOperator):
                remove_child = True
                # we don't remove the child if it belongs to another logical function
                for lo in self.los:
                    for ch in lo.children:
                        if ch == child:
                            remove_child = False
                            break
                if remove_child:
                    # we don't remove the child if it is the source of a modulation
                    for mod in self.modulations:
                        if mod.source == child:
                            remove_child = False
                if remove_child:
                    toremove.add(child)
        for child in toremove:
            self.remove_lo(child)
        self.modulations = [mod for mod in self.modulations if mod.source != op]

    def remove_modulation(self, modulation):
        """Removes a modulation from the map

        Also removes its source if it is a logical operator that is not the child of another operator or the source of another modualtion.

        :param modulation: the modulation to be removed
        """
        if isinstance(modulation, str):
            parser = Parser()
            modulation =  parser.modulation.parseString(modulation)
        self.modulations.remove(modulation)
        # no orphan logical operator
        if isinstance(modulation.source, LogicalOperator):
            # we don't remove the lo if it is the source of another modulation
            for mod in self.modulations:
                if mod.source == modulation.source:
                    return
            # we don't remove the lo if it belongs to another logical function
            for lo in self.los:
                if modulation.source in lo.children:
                    return
            self.remove_lo(modulation.source)

    def get_compartment(self, val, by_compartment = False, by_id = False, by_label = False, by_hash = False, by_string = False):
        """Retrieves a compartment from the map

        Possible ways of searching for the compartment: by object, id, hash or sbgntxt string.
        Only the first matching compartment is retrieved.
        Returns None if no matching compartment is found.

        :param val: the value to be searched
        :param by_ui: if True, search by object
        :param by_id: if True, search by id
        :param by_hash: if True, search by hash
        :param by_string: if True, search by sbgntxt string
        :return: the unit of information or None
        """
        if by_string:
            parser = Parser()
            val = parser.compartment.parseString(val)[0]
        for c in self.compartments:
            if by_compartment or by_string:
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

    def get_lo(self, val, by_lo = False, by_id = False, by_hash = False, by_string = False):
        """Retrieves a logical operator from the map

        Possible ways of searching for the logical operator: by object, id, hash or sbgntxt string.
        Only the first matching logical operator is retrieved.
        Returns None if no matching logical operator is found.

        :param val: the value to be searched
        :param by_ui: if True, search by object
        :param by_id: if True, search by id
        :param by_hash: if True, search by hash
        :param by_string: if True, search by sbgntxt string
        :return: the unit of information or None
        """
        if by_string:
            parser = Parser()
            val = parser.lo.parseString(val)[0]
        for o in self.los:
            if by_lo or by_string:
                if o == val:
                    return o
            if by_id:
                if o.id == val:
                    return o
            if by_hash:
                if hash(o) == val:
                    return o
        return None

    def get_modulation(self, val, by_modulation = False, by_id = False, by_hash = False, by_string = False):
        """Retrieves a modulation from the map

        Possible ways of searching for the modulation: by object, id, hash or sbgntxt string.
        Only the first matching modulation is retrieved.
        Returns None if no matching modulation is found.

        :param val: the value to be searched
        :param by_ui: if True, search by object
        :param by_id: if True, search by id
        :param by_hash: if True, search by hash
        :param by_string: if True, search by sbgntxt string
        :return: the unit of information or None
        """
        if by_string:
            parser = Parser()
            val = parser.modulation.parseString(val)[0]
        for m in self.modulations:
            if by_modulation or by_string:
                if m == val:
                    return m
            if by_id:
                if m.id == val:
                    return m
            if by_hash:
                if hash(m) == val:
                    return m
        return None

    def get_process(self, val, by_process = False, by_id = False, by_label = False, by_hash = False, by_string = False):
        """Retrieves a process from the map

        Possible ways of searching for the process: by object, id, hash or sbgntxt string.
        Only the first matching process is retrieved.
        Returns None if no matching process is found.

        :param val: the value to be searched
        :param by_ui: if True, search by object
        :param by_id: if True, search by id
        :param by_hash: if True, search by hash
        :param by_string: if True, search by sbgntxt string
        :return: the unit of information or None
        """
        if by_string:
            parser = Parser()
            val = parser.process.parseString(val)[0]
        for p in self.processes:
            if by_process or by_string:
                if p == val:
                    return p
            if by_id:
                if p.id == val:
                    return p
            if by_label:
                if hasattr(p, "label"):
                    if p.label == val:
                        return p
            if by_hash:
                if hash(p) == val:
                    return p
        return None

    def get_entity(self, val, by_entity = True, by_id = False, by_label = False, by_hash = False, by_string = False):
        """Retrieves a entity pool from the map

        Possible ways of searching for the entity pool: by object, id, hash or sbgntxt string.
        Only the first matching entity pool is retrieved.
        Returns None if no matching entity pool is found.

        :param val: the value to be searched
        :param by_ui: if True, search by object
        :param by_id: if True, search by id
        :param by_hash: if True, search by hash
        :param by_string: if True, search by sbgntxt string
        :return: the unit of information or None
        """
        if by_string:
            parser = Parser()
            val = parser.entity.parseString(val)[0]
        for e in self.entities:
            if by_entity or by_string:
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

    def replace_entity(self, e1, e2):
        """Replaces an entity pool by another in the map

        :param e1: the entity pool to be replaced
        :param e2: the replacing entity pool
        :return: None
        """
        if isinstance(e1, str):
            parser = Parser()
            e1 =  parser.entity.parseString(e1)
        if isinstance(e2, str):
            parser = Parser()
            e2 =  parser.entity.parseString(e2)
        existent_entity = self.get_entity(e2, by_entity = True)
        if existent_entity:
            e2 = existent_entity
        self.add_entity(e2)
        for modulation in self.modulations:
            if modulation.source == e1:
                modulation.source = e2
        for process in self.processes:
            for reac in process.reactants:
                if reac == e1:
                    process.reactants[process.reactants.index(e1)] = e2
            for prod in process.products:
                if prod == e1:
                    process.products[process.products.index(e1)] = e2
        for lo in self.los:
            for child in lo.children:
                if child == e1:
                    lo.children[lo.children.index(e1)] = e2

    def replace_lo(self, lo1, lo2):
        """Replaces an logical operator by another in the map

        :param lo1: the logical operator to be replaced
        :param lo2: the replacing logical operator
        :return: None
        """
        if isinstance(lo1, str):
            parser = Parser()
            lo1 =  parser.lo.parseString(lo1)
        if isinstance(lo2, str):
            parser = Parser()
            lo2 =  parser.modulation.parseString(lo2)
        existent_lo = self.get_entity(lo2, by_lo = True)
        if existent_lo:
            lo2 = existent_lo
        self.add_lo(lo2)
        for modulation in self.modulations:
            if modulation.source == lo1:
                modulation.source = lo2
        for op in self.los:
            for child in op.children:
                if child == lo1:
                    op.children[op.children.index(lo1)] = lo2

    def replace_modulation(self, m1, m2):
        """Replaces an modulation by another in the map

        :param m1: the modulation to be replaced
        :param m2: the replacing modulation
        :return: None
        """
        if isinstance(m1, str):
            parser = Parser()
            m1 =  parser.modulation.parseString(m1)
        if isinstance(m2, str):
            parser = Parser()
            m2 =  parser.modulation.parseString(m2)
        self.add_modulation(m2)
        self.remove_modulation(m1)

    def replace_compartment(self, c1, c2):
        """Replaces a compartment by another in the map

        :param c1: the compartment to be replaced
        :param c2: the replacing compartment
        :return: None
        """
        if isinstance(c1, str):
            parser = Parser()
            c1 =  parser.compartment.parseString(c1)
        if isinstance(c2, str):
            parser = Parser()
            c2 =  parser.compartment.parseString(c2)
        self.add_compartment(c2)
        for entity in self.entities:
            if entity.compartment == c1:
                entity.compartment = c2
        self.remove_compartment(c1)

    def replace_process(self, p1, p2):
        """Replaces an process by another in the map

        :param p1: the process to be replaced
        :param p2: the replacing process
        :return: None
        """
        if isinstance(p1, str):
            parser = Parser()
            p1 =  parser.process.parseString(p1)
        if isinstance(p2, str):
            parser = Parser()
            p2 =  parser.process.parseString(p2)
        self.add_process(p2)
        for modulation in self.modulations:
            if modulation.target == p1:
                modulation.target = p2
        self.remove_process(p1)

    def query_entities(self, regexp):
        """Retrieves entities of the map whose sbgntxt representation match an input regular expression

        :param regexp: the regular expression to match
        :return: all entities matching the regular expression
        """
        res = []
        r = re.compile(regexp)
        for e in self.entities:
            if r.match(str(e)):
                res.append(e)
        return res

    def query_processes(self, regexp):
        """Retrieves processes of the map whose sbgntxt representation match an input regular expression

        :param regexp: the regular expression to match
        :return: all processes matching the regular expression
        """
        res = []
        r = re.compile(regexp)
        for e in self.processes:
            if r.match(str(e)):
                res.append(e)
        return res

    def query_los(self, regexp):
        """Retrieves logical operators of the map whose sbgntxt representation match an input regular expression

        :param regexp: the regular expression to match
        :return: all processes matching the regular expression
        """
        res = []
        r = re.compile(regexp)
        for e in self.los:
            if r.match(str(e)):
                res.append(e)
        return res

    def query_modulations(self, regexp):
        """Retrieves modulations of the map whose sbgntxt representation match an input regular expression

        :param regexp: the regular expression to match
        :return: all processes matching the regular expression
        """
        res = []
        r = re.compile(regexp)
        for e in self.modulations:
            if r.match(str(e)):
                res.append(e)
        return res

    def query_compartments(self, regexp):
        """Retrieves compartments of the map whose sbgntxt representation match an input regular expression

        :param regexp: the regular expression to match
        :return: all processes matching the regular expression
        """
        res = []
        r = re.compile(regexp)
        for e in self.compartments:
            if r.match(str(e)):
                res.append(e)
        return res

    def union(self, other):
        """Returns the union of the map with another map

        :param other: the other map
        :return: a new map that is the union of the map and the other map
        """
        new = Network()
        for e in self.entities:
            new.add_entity(deepcopy(e))
        for p in self.processes:
            new.add_process(deepcopy(p))
        for m in self.modulations:
            new.add_modulation(deepcopy(m))
        for c in self.compartments:
            new.add_compartment(deepcopy(c))
        for o in self.los:
            new.add_lo(deepcopy(o))
        for e in other.entities:
            new.add_entity(deepcopy(e))
        for p in other.processes:
            new.add_process(deepcopy(p))
        for m in other.modulations:
            new.add_modulation(deepcopy(m))
        for c in other.compartments:
            new.add_compartment(deepcopy(c))
        for o in other.los:
            new.add_lo(deepcopy(o))
        # new.entities = list(set(self.entities).union(set(other.entities)))
        # new.processes = list(set(self.processes).union(set(other.processes)))
        # new.modulations = list(set(self.modulations).union(set(other.modulations)))
        # new.los = list(set(self.los).union(set(other.los)))
        # new.compartments = list(set(self.compartments).union(set(other.compartments)))
        return new

    def intersection(self, other):
        """Returns the intersection of the map with another map

        :param other: the other map
        :return: a new map that is the intersection of the map and the other map
        """
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
        for c in self.compartments:
            if c in other.compartments:
                new.add_compartment(deepcopy(c))
        for o in self.los:
            if o in other.los:
                new.add_compartment(deepcopy(o))
        return new
        # new.entities = list(set(self.entities).intersection(set(other.entities)))
        # new.processes = list(set(self.processes).intersection(set(other.processes)))
        # new.modulations = list(set(self.modulations).intersection(set(other.modulations)))
        # new.los = list(set(self.los).intersection(set(other.los)))
        # new.compartments = list(set(self.compartments).intersection(set(other.compartments)))

    def difference(self, other):
        """Returns the difference of the map with another map

        :param other: the other map
        :return: a new map that is the difference of the map and the other map
        """
        new = Network()
        for m in self.modulations:
            if m not in other.modulations:
                new.add_modulation(deepcopy(m))
        for p in self.processes:
            if p not in other.processes:
                new.add_process(deepcopy(p))
        for e in self.entities:
            if e not in other.entities:
                new.add_entity(deepcopy(e))
        for c in self.compartments:
            if c not in other.compartments:
                new.add_compartment(deepcopy(c))
        for o in self.los:
            if o not in other.los:
                new.add_lo(deepcopy(o))
        # new.entities = list(set(self.entities).difference(set(other.entities)))
        # new.processes = list(set(self.processes).difference(set(other.processes)))
        # new.modulations = list(set(self.modulations).difference(set(other.modulations)))
        # new.los = list(set(self.los).difference(set(other.los)))
        # new.compartments = list(set(self.compartments).difference(set(other.compartments)))
        return new

    def simplify_gene_expressions(self):
        """Simplifies transcription and translation processes into generic processes a la CellDesigner

        :return: None
        """
        mods = defaultdict(list)
        for t in self.transcriptions:
            for m in self.modulations:
                if m.target == t:
                    if isinstance(m.source, NucleicAcidFeature) and UnitOfInformation("ct", "gene") in m.source.uis and m.source.label == t.products[0].label:
                        t.reactants.append(m.source)
                        t.reactants.remove(EmptySet())
                        self.remove_modulation(m)
                        break
        for t in self.translations:
            for m in self.modulations:
                if m.target == t:
                    if isinstance(m.source, NucleicAcidFeature) and UnitOfInformation("ct", "mRNA") in m.source.uis and m.source.label == t.products[0].label:
                        t.reactants.append(m.source)
                        t.reactants.remove(EmptySet())
                        self.remove_modulation(m)
                        break

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
