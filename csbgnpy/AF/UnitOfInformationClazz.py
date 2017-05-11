from enum import Enum

class UnitOfInformationClazz(Enum):
    MACROMOLECULE = {"name": "macromolecule", "h" : 40, "w" : 40}
    NUCLEIC_ACID_FEATURE = {"name": "nucleic acid feature", "h" : 40, "w" : 40}
    SIMPLE_CHEMICAL = {"name": "simple chemical", "h" : 40, "w" : 40}
    UNSPECIFIED_ENTITY = {"name": "unspecified entity", "h" : 40, "w" : 40}
    COMPLEX = {"name": "complex", "h" : 40, "w" : 40}
    PERTURBATION = {"name": "perturbation", "h" : 40, "w" : 40}
