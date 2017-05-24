from enum import Enum

class ProcessClazz(Enum):
    PROCESS = "process"
    OMITTED_PROCESS = "omitted process"
    UNCERTAIN_PROCESS  = "uncertain process"
    ASSOCIATION = "association"
    DISSOCIATION  = "dissociation"
    PHENOTYPE = "phenotype"
