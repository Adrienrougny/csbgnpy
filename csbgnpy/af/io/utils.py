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
    DELAY = DelayOperator

class ModulationEnum(Enum):
    INFLUENCE  = Modulation
    POSITIVE_INFLUENCE  = Stimulation
    NEGATIVE_INFLUENCE  = Inhibition
    UNKNOWN_INFLUENCE  = Modulation
    NECESSARY_STIMULATION  = NecessaryStimulation
