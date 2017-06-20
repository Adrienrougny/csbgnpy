from csbgnpy import *
# from Process import *
# from Modulation import *
# from StateVariable import *
# from Compartment import *
# from LogicalFunction import *
# from LogicalOperator import *

class Network:

    def __init__(self, activities = None, modulations = None, compartments = None, logical_operator_nodes = None):
        if activities is not None:
            self.activities = activities
        else:
            self.activities = set()
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

    def add_activity(self, act):
        self.activities.add(act)

    def add_modulation(self, mod):
        self.modulations.add(mod)

    def add_compartment(self, comp):
        self.compartments.add(comp)

    def add_logical_operator_node(self, op):
        self.logical_operator_nodes.add(op)

    # def getActivity(self, activity):
    #     if isinstance(activity, Activity):
    #         for activity2 in self.activities:
    #             if activity == activity2:
    #                 return activity2
    #         return None
    #     elif isinstance(activity, str):
    #         for activity2 in self.activities:
    #             if activity2.getId() == activity:
    #                 return activity2
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
    # def getLogicalOperatorNode(self, logicalOperatorNode):
    #     for logicalOperatorNode2 in self.logicalOperatorNodes:
    #         if logicalOperatorNode2 == logicalOperatorNode:
    #             return logicalOperatorNode2
    #     return None
    #
    # def isModulator(self, activity):
    #     for modulation in self.getModulations():
    #         if activity == modulation.getSource():
    #             return True
    #     return False
    #
    # def removeSingleActivities(self):
    #     toRemove = set()
    #     for act in self.getActivities():
    #         if not self.isProduced(act) and not self.isConsumed(act) and not self.isModulator(act):
    #             toRemove.add(act)
    #     for act in toRemove:
    #         self.activities.remove(act)
    #
    # def setNoneLabelsToEmptyStrings(self):
    #     for act in self.activities:
    #         if act.getLabel() is None:
    #             act.setLabel("")
