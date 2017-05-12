from enum import Enum

class SubEntityClazz(Enum):
    SUB_UNSPECIFIED_ENTITY = {"name": "unspecified entity", "h" : 40, "w" : 40}
    SUB_SIMPLE_CHEMICAL = {"name": "simple chemical", "h" : 40, "w" : 40}
    SUB_MACROMOLECULE = {"name": "macromolecule", "h" : 60, "w" : 108}
    SUB_NUCLEIC_ACID_FEATURE = {"name":  "nucleic acid feature", "h" : 40, "w" : 40}
    SUB_SIMPLE_CHEMICAL_MULTIMER = {"name": "simple chemical multimer", "h" : 40, "w" : 40}
    SUB_MACROMOLECULE_MULTIMER = {"name":  "macromolecule multimer", "h" : 40, "w" : 40}
    SUB_NUCLEIC_ACID_FEATURE_MULTIMER = {"name":  "nucleic acid feature multimer", "h" : 40, "w" : 40}
    SUB_COMPLEX = {"name": "complex", "h" : 40, "w" : 40}
    SUB_COMPLEX_MULTIMER = {"name": "complex multimer", "h" : 40, "w" : 40}

