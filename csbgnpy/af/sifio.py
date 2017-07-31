from enum import Enum
import libsbgnpy.libsbgn as libsbgn
from csbgnpy.utils import *
from csbgnpy.af.compartment import *
from csbgnpy.af.activity import *
from csbgnpy.af.modulation import *
from csbgnpy.af.lo import *
from csbgnpy.af.ui import *
from csbgnpy.af.network import *

class ActivityEnum(Enum):
    BIOLOGICAL_ACTIVITY = BiologicalActivity
    PHENOTYPE = Phenotype

class LogicalOperatorEnum(Enum):
    OR = OrOperator
    AND = AndOperator
    NOT = NotOperator

class ModulationEnum(Enum):
    INFLUENCE  = Modulation
    POSITIVE_INFLUENCE  = Stimulation
    NEGATIVE_INFLUENCE  = Inhibition
    UNKNOWN_INFLUENCE  = Modulation
    NECESSARY_STIMULATION  = NecessaryStimulation

def read(*filenames):
    net = Network()
    activities = set()
    modulations = set()
    for filename in filenames:
        f = open(filename)
        for line in filename:
            l = line[:-1].split("\t")
            source = BiologicalActivity()
            source.label = l[0]
            activities.add(source)
            target = BiologicalActivity()
            target.label = l[2]
            activities.add(target)
            if l[1] == "-1":
                mod = Inhibition()
            elif l[1] == "1":
                mod = Stimulation()
            mod.source = source
            mod.target = taget
            modulations.add(mod)
    net.activities = list(activities)
    net.modulations = list(modulations)
    return net
