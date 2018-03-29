from enum import Enum
from csbgnpy.pd.entity import *
from csbgnpy.pd.subentity import *
from csbgnpy.pd.process import *
from csbgnpy.pd.modulation import *
from csbgnpy.pd.lo import *

class EntityEnum(Enum):
    """Enum for entity pools"""
    UNSPECIFIED_ENTITY = UnspecifiedEntity
    SIMPLE_CHEMICAL = SimpleChemical
    MACROMOLECULE = Macromolecule
    NUCLEIC_ACID_FEATURE = NucleicAcidFeature
    SIMPLE_CHEMICAL_MULTIMER = SimpleChemicalMultimer
    MACROMOLECULE_MULTIMER = MacromoleculeMultimer
    NUCLEIC_ACID_FEATURE_MULTIMER = NucleicAcidFeatureMultimer
    COMPLEX = Complex
    COMPLEX_MULTIMER = ComplexMultimer
    SOURCE_AND_SINK = EmptySet
    PERTURBING_AGENT = PerturbingAgent

class SubEntityEnum(Enum):
    """Enum for subentities"""
    SUB_UNSPECIFIED_ENTITY = SubUnspecifiedEntity
    SUB_SIMPLE_CHEMICAL = SubSimpleChemical
    SUB_MACROMOLECULE = SubMacromolecule
    SUB_NUCLEIC_ACID_FEATURE = SubNucleicAcidFeature
    SUB_SIMPLE_CHEMICAL_MULTIMER = SubSimpleChemicalMultimer
    SUB_MACROMOLECULE_MULTIMER = SubMacromoleculeMultimer
    SUB_NUCLEIC_ACID_FEATURE_MULTIMER = SubNucleicAcidFeatureMultimer
    SUB_COMPLEX = SubComplex
    SUB_COMPLEX_MULTIMER = SubComplexMultimer

class ProcessEnum(Enum):
    """Enum for processes"""
    PROCESS = GenericProcess
    OMITTED_PROCESS = OmittedProcess
    UNCERTAIN_PROCESS  = UncertainProcess
    ASSOCIATION = Association
    DISSOCIATION  = Dissociation
    PHENOTYPE = Phenotype

class LogicalOperatorEnum(Enum):
    """Enum for logical operators"""
    OR = OrOperator
    AND = AndOperator
    NOT = NotOperator

class ModulationEnum(Enum):
    """Enum for modulations"""
    CATALYSIS  = Catalysis
    MODULATION  = Modulation
    STIMULATION  = Stimulation
    INHIBITION  = Inhibition
    UNKNOWN_INFLUENCE  = Modulation
    NECESSARY_STIMULATION  = NecessaryStimulation
