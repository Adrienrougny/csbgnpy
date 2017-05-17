from csbgnpy import *
# from Process import *
# from Modulation import *
# from StateVariable import *
# from Compartment import *
# from LogicalFunction import *
# from LogicalOperator import *

class Network:

    def __init__(self, entities = None, processes = None, modulations = None, compartments = None, logical_operator_nodes = None):
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
        if logical_operator_nodes is not None:
            self.logical_operator_nodes = logical_operator_nodes
        else:
            self.logical_operator_nodes = set()

    def add_process(self, proc):
        self.processes.add(proc)

    def add_entity(self, entity):
        self.entities.add(entity)

    def add_modulation(self, mod):
        self.modulations.add(mod)

    def add_compartment(self, comp):
        self.compartments.add(comp)

    def add_logical_operator_node(self, op):
        self.logical_operator_nodes.add(op)

    # def getEntity(self, entity):
    #     if isinstance(entity, Entity):
    #         for entity2 in self.entities:
    #             if entity == entity2:
    #                 return entity2
    #         return None
    #     elif isinstance(entity, str):
    #         for entity2 in self.entities:
    #             if entity2.getId() == entity:
    #                 return entity2
    #         return None
    #
    # def getProcess(self, process):
    #     if isinstance(process, Process):
    #         for process2 in self.processes:
    #             if process == process2:
    #                 return process2
    #         return None
    #     elif isinstance(process, str):
    #         for process2 in self.processes:
    #             if process2.getId() == process:
    #                 return process
    #         return None
    #
    # def getModulation(self, modulation):
    #     for modulation2 in self.modulations:
    #         if modulation2 == modulation:
    #             return modulation2
    #     return None
    #
    # def getCompartment(self, compartment):
    #     for compartment2 in self.compartments:
    #         if compartment2 == compartment:
    #             return compartment2
    #     return None
    #
    # def getLogicalFunction(self, logicalFunction):
    #     for logicalFunction2 in self.logicalFunctions:
    #         if logicalFunction2 == logicalFunction:
    #             return logicalFunction2
    #     return None
    #
    # def getLogicalFunctionByRoot(self, logicalOperator):
    #     for logicalFunction in self.logicalFunctions:
    #         if logicalFunction.getRoot() == logicalOperator:
    #             return logicalFunction
    #     return None
    #

    # def isProduced(self, entity):
    #     for process in self.getProcesses():
    #         if entity in process.getProducts():
    #             return True
    #     return False
    #
    # def isConsumed(self, entity):
    #     for process in self.getProcesses():
    #         if entity in process.getReactants():
    #             return True
    #     return False
    #
    # def isModulator(self, entity):
    #     for modulation in self.getModulations():
    #         if entity == modulation.getSource():
    #             return True
    #     return False
    #
    # def isSource(self, entity):
    #     if entity.getClazz() == EntityClazz.SOURCE_AND_SINK and not self.isProduced(entity):
    #         return True
    #     else:
    #         return False
    #
    # def isSink(self, entity):
    #     if entity.getClazz() == EntityClazz.SOURCE_AND_SINK and not self.isConsumed(entity):
    #         return True
    #     else:
    #         return False
    #
    # def updateIds(self):
    #     iepn = 0
    #     isubepn = 0
    #     isv = 0
    #     icomp = 0
    #     iproc = 0
    #     for epn in self.getEntities():
    #         epn.setId("epn{0}".format(iepn))
    #         iepn += 1
    #         for subepn in epn.getComponents():
    #             subepn.setId("subepn{0}".format(isubepn))
    #             isubepn += 1
    #         for sv in epn.getStateVariables():
    #             sv.setId("sv{0}".format(isv))
    #             isv += 1
    #     for comp in self.getCompartments():
    #         comp.setId("comp{0}".format(icomp))
    #         icomp += 1
    #     for proc in self.getProcesses():
    #         proc.setId("proc{0}".format(iproc))
    #         iproc += 1

    # def removeSingleEntities(self):
    #     toRemove = set()
    #     for epn in self.getEntities():
    #         if not self.isProduced(epn) and not self.isConsumed(epn) and not self.isModulator(epn):
    #             toRemove.add(epn)
    #     for epn in toRemove:
    #         self.entities.remove(epn)
    #
    # def setNoneLabelsToEmptyStrings(self):
    #     for epn in self.entities:
    #         if epn.getLabel() is None:
    #             epn.setLabel("")
    #
    # def __str__(self):
    #     s = ""
    #     for epn in self.getEntities():
    #         s += "Epn: {0}\n".format(epn)
    #     for proc in self.getProcesses():
    #         s += "Process: {0}\n".format(proc)
    #
    #     return s
