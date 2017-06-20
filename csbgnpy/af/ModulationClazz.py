from enum import Enum

class ModulationClazz(Enum):
    MODULATION  = "modulation"
    POSITIVE_INFLUENCE  = "stimulation"
    NEGATIVE_INFLUENCE  = "inhibition"
    UNKNOWN_INFLUENCE  = "unknown influence"
    NECESSARY_STIMULATION  = "necessary stimulation"
