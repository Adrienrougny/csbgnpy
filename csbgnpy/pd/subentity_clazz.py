from enum import Enum

class SubEntityClazz(Enum):
    SUB_UNSPECIFIED_ENTITY = "unspecified entity"
    SUB_SIMPLE_CHEMICAL = "simple chemical"
    SUB_MACROMOLECULE = "macromolecule"
    SUB_NUCLEIC_ACID_FEATURE = "nucleic acid feature"
    SUB_SIMPLE_CHEMICAL_MULTIMER = "simple chemical multimer"
    SUB_MACROMOLECULE_MULTIMER = "macromolecule multimer"
    SUB_NUCLEIC_ACID_FEATURE_MULTIMER = "nucleic acid feature multimer"
    SUB_COMPLEX = "complex"
    SUB_COMPLEX_MULTIMER = "complex multimer"

