from enum import Enum

class ProcessClazz(Enum):
    PROCESS = {"name": "process", "h" : 24, "w" : 24}
    OMITTED_PROCESS = {"name": "omitted process", "h" : 24, "w" : 24}
    UNCERTAIN_PROCESS  = {"name": "uncertain process", "h" : 24, "w" : 24}
    ASSOCIATION = {"name": "association", "h" : 24, "w" : 24}
    DISSOCIATION  = {"name": "dissociation", "h" : 24, "w" : 24}
    PHENOTYPE = {"name": "phenotype", "h" : 24, "w" : 24}
