from enum import Enum

class EntityClazz(Enum):
    UNSPECIFIED_ENTITY = "unspecified entity"
    SIMPLE_CHEMICAL = "simple chemical"
    MACROMOLECULE = "macromolecule"
    NUCLEIC_ACID_FEATURE = "nucleic acid feature"
    SIMPLE_CHEMICAL_MULTIMER = "simple chemical multimer"
    MACROMOLECULE_MULTIMER = "macromolecule multimer"
    NUCLEIC_ACID_FEATURE_MULTIMER = "nucleic acid feature multimer"
    COMPLEX = "complex"
    COMPLEX_MULTIMER = "complex multimer"
    SOURCE_AND_SINK = "source and sink"
    PERTURBING_AGENT = "perturbation"
