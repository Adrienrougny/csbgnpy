from math import atan2

from csbgnpy.utils import *
from csbgnpy.pd.compartment import *
from csbgnpy.pd.entity import *
from csbgnpy.pd.process import *
from csbgnpy.pd.modulation import *
from csbgnpy.pd.lo import *
from csbgnpy.pd.sv import *
from csbgnpy.pd.ui import *
from csbgnpy.pd.network import *
from csbgnpy.pd.io_utils import *

class Atom(object):
    def __init__(self, name = None, args = None):
        self.name = name
        if args is None:
            self.args = []
        else:
            self.args = args

    def __str__(self):
        return "{0}({1})".format(self.name, ','.join([str(arg) for arg in self.args]))

class Constant(object):
    def __init__(self, value = None):
        self.value = value

    def __str__(self):
        return self.value

class TranslationEnum(Enum):
    MACROMOLECULE = "macromolecule"
    NUCLEIC_ACID_FEATURE = "nucleicAcidFeature"
    SIMPLE_CHEMICAL = "simpleChemical"
    UNSPECIFIED_ENTITY = "unspecifiedEntity"
    COMPLEX = "complex"
    LABEL = "label"
    LABELED = "labeled"
    LOCALIZED = "localized"
    INPUT = "input"
    UNIT_OF_INFORMATION = "unitOfInformation"
    NULL_COMPARTMENT = "null_comp"
    COMPARTMENT = "compartment"
    CATALYSIS  = "catalyzes"
    MODULATION  = "modulates"
    STIMULATION  = "stimulates"
    INHIBITION  = "inhibits"
    UNKNOWN_INFLUENCE  = "modulates"
    NECESSARY_STIMULATION  = "necessarilyStimulates"
    PROCESS = "process"
    OMITTED_PROCESS = "omittedProcess"
    UNCERTAIN_PROCESS  = "uncertainProcess"
    ASSOCIATION = "association"
    DISSOCIATION  = "dissociation"
    PHENOTYPE = "phenotype"
    SIMPLE_CHEMICAL_MULTIMER = "multimerOfsimpleChemicals"
    MACROMOLECULE_MULTIMER = "multimerOfMacromolecules"
    NUCLEIC_ACID_FEATURE_MULTIMER = "multimerOfNucleicAcidFeatures"
    COMPLEX_MULTIMER = "multimerOfComplexes"
    SOURCE_AND_SINK = "emptySet"
    PERTURBING_AGENT = "perturbation" # PERTURBATION ?
    OR = "or"
    AND = "and"
    NOT = "not"
    STATE_VARIABLE = "stateVariable"
    UNDEFINED = "undefined"
    UNSET = "unset"
    CARDINALITY = "cardinality"
    VOID = "void"
    REACTANT = "consumes"
    PRODUCT = "produces"

    """TO DO :
    - compartments with no label ? Is that possible ?
    - put a lexicographic order for logical operator nodes so that any logical function can be uniquely identified by its constant
    same for processes (sets of reactants and products)
    """

def write(net, filename):
    sbgnlog = _translate_network(net)
    f = open(filename, 'w')
    f.write('\n'.join(sorted([str(atom) for atom in sbgnlog])))
    f.close()

def _translate_network(net):
    s = set()
    for entity in net.entities:
        s |= _translate_entity(entity)
    for comp in net.compartments:
        s |= _translate_compartment(comp)
    for op in net.los:
        s |= _translate_lo(op)
    for mod in net.modulations:
        s |= _translate_modulation(mod)
    for proc in net.processes:
        s |= _translate_process(proc)
    return s

def _make_constant_from_ui(ui):
    if ui.pre is None:
        const = TranslationEnum["VOID"].value
    else:
        const = normalize_string(ui.pre)
    const += normalize_string(ui.label)
    return Constant(const)

def _make_constant_from_sv(sv):
    if sv.value is None:
        const = TranslationEnum["UNSET"].value
    else:
        const = normalize_string(sv.value)
    if isinstance(sv.variable, UndefinedVar):
        const += "_{0}({1})".format(TranslationEnum["UNDEFINED"].value, sv.variable.num)
    else:
        const += "_{0}".format(normalize_string(sv.variable))
    return Constant(const)

def _make_constant_from_entity(entity):
    const = "e_{}".format(TranslationEnum[EntityEnum(entity.__class__).name].value)
    if hasattr(entity, "uis") and len(entity.uis) > 0:
        const += '_'
        const += '_'.join([str(_make_constant_from_ui(ui)) for ui in entity.uis])
    if hasattr(entity, "svs") and len(entity.svs) > 0:
        const += '_'
        const += '_'.join([str(_make_constant_from_sv(sv)) for sv in entity.svs])
    if hasattr(entity, "components") and len(entity.components) > 0:
        const += '_'
        const += '_'.join([str(_make_constant_from_subentity(subentity)) for subentity in entity.components])
    const += "_{}".format(normalize_string(entity.label))
    if hasattr(entity, "compartment"):
        if entity.compartment:
            const += "_{0}".format(_make_constant_from_compartment(entity.compartment))
    return Constant(const)

def _make_constant_from_subentity(subentity):
    const = "sube_{}".format(TranslationEnum[subentityEnum(subentity.__class__).name].value)
    if hasattr(subentity, "uis") and len(subentity.uis) > 0:
        const += '_'
        const += '_'.join([str(_make_constant_from_ui(ui)) for ui in subentity.uis])
    if hasattr(subentity, "svs") and len(subentity.svs) > 0:
        const += '_'
        const += '_'.join([str(_make_constant_from_sv(sv)) for sv in subentity.svs])
    if hasattr(subentity, "components") and len(subentity.components) > 0:
        const += '_'
        const += '_'.join([str(_make_constant_from_subsubentity(subsubentity)) for subsubentity in subentity.components])
    const += "_{}".format(normalize_string(subentity.label))
    return Constant(const)

def _make_constant_from_compartment(compartment):
    const = "c_"
    if not comp.label:
        const += TranslationEnum["NULL_COMPARTMENT"].value
    else:
        const += comp.label
    return Constant(normalize_string(const))

def _make_constant_from_label(label):
    if label is None:
        label = ""
    return Constant(quote_string(label))

def _make_constant_from_lo(op):
    const = "lo_{}".format(TranslationEnum[LogicalOperatorEnum(op.__class__).name].value)
    for child in op.children:
        if isinstance(child, LogicalOperator):
            const += "_{0}".format(_make_constant_from_lo(child))
        else:
            const += "_{0}".format(_make_constant_from_entity(child))
    return Constant(const)

def _make_constant_from_empty_set(es):
    const = "e_{}".format(TranslationEnum["EMPTY_SET"].value)
    return Constant(const)

def _make_constant_from_process(proc):
    const = "p"
    const_reacs = []
    const_prods = []
    if hasattr(proc, "reactants"):
        const += "_"
        for reac in proc.reactants:
            if isinstance(reac, Entity):
                const_reac = _make_constant_from_entity(reac)
            else:
                const_reac = _make_constant_from_empty_set(reac)
            const_reacs.append(const_reac)
    if hasattr(proc, "products"):
        for prod in proc.products:
            if isinstance(prod, Entity):
                const_prod = _make_constant_from_entity(prod)
            else:
                const_prod = _make_constant_from_empty_set(prod)
            const_prods.append(const_prod)
        const += '_'.join([str(const) for const in const_reacs]) + '_' + '_'.join([str(const) for const in const_prods])
    return const

def _translate_entity(entity):
    s = set()
    entity_name = TranslationEnum[EntityEnum(entity.__class__).name].value
    entity_const = _make_constant_from_entity(entity)
    entity_atom = Atom(entity_name, [entity_const])
    s.add(entity_atom)
    if hasattr(entity, "uis"):
        for ui in entity.uis:
            ui_name = TranslationEnum["UNIT_OF_INFORMATION"].value
            if ui.pre is None:
                ui_pre_const = TranslationEnum["VOID"].value
            else:
                ui_pre_const = quote_string(ui.pre)
            ui_label_const = quote_string(ui.label)
            ui_atom = Atom(ui_name, [entity_const, ui_pre_const, ui_label_const])
            s.add(ui_atom)
    if hasattr(entity, "svs"):
        for sv in entity.svs:
            sv_name = TranslationEnum["STATE_VARIABLE"].value
            if sv.value is None:
                sv_value_const = TranslationEnum["UNSET"].value
            else:
                sv_value_const = quote_string(sv.value)
            if isinstance(sv.variable, UndefinedVar):
                sv_variable_const = "{0}({1})".format(TranslationEnum["UNDEFINED"].value, sv.variable.num)
            else:
                sv_variable_const = quote_string(sv.variable)
            sv_atom = Atom(sv_name, [entity_const, sv_value_const, sv_variable_const])
            s.add(sv_atom)
    if hasattr(entity, "components"):
        for component in entity.components:
            component_name = TranslationEnum["COMPONENT"].value
            component_const = _make_constant_from_subentity(component)
            component_atom = Atom(component_name, [entity_const, component_const])
            s.add(component_atom)
            ss = _translate_subentity(component)
            s |= ss
    labeled_name = TranslationEnum["LABELED"].value
    label_const = _make_constant_from_label(entity.label)
    labeled_atom = Atom(labeled_name, [entity_const, label_const])
    s.add(labeled_atom)
    if hasattr(entity, "compartment"):
        if entity.compartment:
            localized_name = TranslationEnum["LOCALIZED"].value
            compartment_const = _make_constant_from_compartment(entity.compartment)
            localized_atom = Atom(localized_name, [entity_const, compartment_const])
            s.add(localized_atom)
    return s

def _translate_subentity(subentity):
    s = set()
    subentity_name = TranslationEnum[subentityEnum(subentity.__class__)].name.value
    subentity_const = _make_constant_from_subentity(subentity)
    subentity_atom = Atom(subentity_name, [subentity_const])
    s.add(subentity_atom)
    if hasattr(subentity, "uis"):
        for ui in subentity.uis:
            ui_name = TranslationEnum["UNIT_OF_INFORMATION"].value
            if ui.pre is None:
                ui_pre_const = TranslationEnum["VOID"].value
            else:
                ui_pre_const = quote_string(ui.pre)
            ui_label_const = quote_string(ui.label)
            ui_atom = Atom(ui_name, [subentity_const, ui_pre_const, ui_label_const])
            s.add(ui_atom)
    if hasattr(subentity, "svs"):
        for sv in subentity.svs:
            sv_name = TranslationEnum["STATE_VARIABLE"].value
            if sv.value is None:
                sv_value_const = TranslationEnum["UNSET"].value
            else:
                sv_value_const = quote_string(sv.value)
            if isinstance(sv.variable, UndefinedVar):
                sv_variable_const = "{0}({1})".format(TranslationEnum["UNDEFINED"].value, sv.variable.num)
            else:
                sv_variable_const = quote_string(sv.variable)
            sv_atom = Atom(sv_name, [subentity_const, sv_value_const, sv_variable_const])
            s.add(sv_atom)
    if hasattr(subentity, "components"):
        for component in subentity.components:
            component_name = TranslationEnum["COMPONENT"].value
            component_const = _make_constant_from_subsubentity(component)
            component_atom = Atom(component_name, [subentity_const, component_const])
            s.add(component_atom)
            ss = _translate_subsubentity(component)
            s |= ss
    labeled_name = TranslationEnum["LABELED"].value
    label_const = _make_constant_from_label(subentity.label)
    labeled_atom = Atom(labeled_name, [subentity_const, label_const])
    s.add(labeled_atom)
    return s

def _translate_compartment(comp):
    s = set()
    comp_name = TranslationEnum["COMPARTMENT"].value
    comp_const = _make_constant_from_compartment(comp)
    comp_atom = Atom(comp_name, [comp_const])
    s.add(comp_atom)
    return s

def _translate_lo(op):
    s = set()
    op_name = TranslationEnum[LogicalOPeratorEnum(op.__class__).name].value
    op_const = _make_constant_from_lo(op)
    op_atom = Atom(op_name, [op_const])
    s.add(op_atom)
    for child in op.children:
        if isinstance(child, LogicalOperator):
            child_const = _make_constant_from_lo(child)
        else:
            child_const = _make_constant_from_entity(child)
        input_name = TranslationEnum["INPUT"].value
        input_atom = Atom(input_name, [child_const, op_const])
        s.add(input_atom)
    return s

def _translate_modulation(mod):
    s = set()
    source = mod.source
    mod_name = TranslationEnum[ModulationEnum(mod.__class__).name].value
    if isinstance(source, LogicalOperator):
        source_const = _make_constant_from_lo(source)
    else:
        source_const = _make_constant_from_entity(source)
    target_const = _make_constant_from_process(mod.target)
    mod_atom = Atom(mod_name, [source_const, target_const])
    s.add(mod_atom)
    return s

"""Still have to take into account the stoechiometry
"""
def _translate_process(proc):
    s = set()
    proc_name = TranslationEnum[ProcessEnum(proc.__class__).name].value
    proc_const = _make_constant_from_process(proc)
    proc_atom = Atom(proc_name, [proc_const])
    s.add(proc_atom)
    if hasattr(proc, "reactants"):
        reac_name = TranslationEnum["REACTANT"].value
        for reac in proc.reactants:
            if isinstance(reac, Entity):
                reac_const = _make_constant_from_entity(reac)
            else:
                reac_const = _make_constant_from_empty_set(reac)
            reac_atom = Atom(reac_name, [proc_const, reac_const])
            s.add(reac_atom)
    if hasattr(proc, "products"):
        prod_name = TranslationEnum["PRODUCT"].value
        for prod in proc.products:
            if isinstance(prod, Entity):
                prod_const = _make_constant_from_entity(prod)
            else:
                prod_const = _make_constant_from_empty_set(prod)
            prod_atom = Atom(prod_name, [proc_const, prod_const])
            s.add(prod_atom)
    return s
