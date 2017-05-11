from enum import Enum

class EntityClazz(Enum):
    UNSPECIFIED_ENTITY = {"name": "unspecified entity", "h" : 40, "w" : 40}
    SIMPLE_CHEMICAL = {"name": "simple chemical", "h" : 40, "w" : 40}
    MACROMOLECULE = {"name": "macromolecule", "h" : 60, "w" : 108}
    NUCLEIC_ACID_FEATURE = {"name":  "nucleic acid feature", "h" : 40, "w" : 40}
    SIMPLE_CHEMICAL_MULTIMER = {"name": "simple chemical multimer", "h" : 40, "w" : 40}
    MACROMOLECULE_MULTIMER = {"name":  "macromolecule multimer", "h" : 40, "w" : 40}
    NUCLEIC_ACID_FEATURE_MULTIMER = {"name":  "nucleic acid feature multimer", "h" : 40, "w" : 40}
    COMPLEX = {"name": "complex", "h" : 40, "w" : 40}
    COMPLEX_MULTIMER = {"name": "complex multimer", "h" : 40, "w" : 40}
    SOURCE_AND_SINK = {"name": "source and sink", "h" : 40, "w" : 40}
    PERTURBING_AGENT = {"name":  "perturbation", "h" : 40, "w" : 40}
