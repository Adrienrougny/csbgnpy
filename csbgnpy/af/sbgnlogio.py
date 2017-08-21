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
    BIOLOGICAL_ACTIVITY = "biologicalActivity"
    PHENOTYPE = "phenotype"
    OR = "or"
    AND = "and"
    NOT = "not"
    DELAY = "delay"
    INFLUENCE = "modulates"
    POSITIVE_INFLUENCE = "stimulates"
    NEGATIVE_INFLUENCE = "inhibits"
    UNKNOWN_INFLUENCE = "modulates"
    NECESSARY_STIMULATION = "necessarilyStimulates"
    COMPARTMENT = "compartment"
    LABEL = "label"
    LABELED = "labeled"
    LOCALIZED = "localized"
    INPUT = "input"
    UNIT_OF_INFORMATION = "unitOfInformation"
    NULL_COMPARTMENT = "null_comp"
    UNDEFINED = "undefined"
    UNSET = "unset"
    VOID = "void"
    COMPLEX = "complex"
    UNSEPCIFIED_ENTITY = "unspecifiedentity"
    PERTURBATION = "perturbation"
    MACROMOLECULE = "macromolecule"
    NUCLEIC_ACID_FEATURE = "nucleicacidfeature"

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
    for activity in net.activities:
        s |= _translate_activity(activity)
    for comp in net.compartments:
        s |= _translate_compartment(comp)
    for op in net.los:
        s |= _translate_lo(op)
    for mod in net.modulations:
        s |= _translate_modulation(mod)
    return s

def _make_constant_from_ui(ui):
    const = TranslationEnum[ui.type.name].value
    const += '_'
    const += normalize_string(ui.label)
    return Constant(const)

def _make_constant_from_entity(activity):
    const = "a_{}".format(TranslationEnum[ActivityEnum(entity.__class__).name].value)
    if hasattr(activity, "uis") and len(activity.uis) > 0:
        const += '_'
        const += '_'.join([str(_make_constant_from_ui(ui)) for ui in acitivity.uis])
    const += "_{}".format(normalize_string(activity.label))
    if hasattr(activity, "compartment"):
        if activity.compartment:
            const += "_{0}".format(_make_constant_from_compartment(activity.compartment))
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
            const += "_{0}".format(_make_constant_from_activity(child))
    return Constant(const)

def _translate_activity(activity):
    s = set()
    activity_name = TranslationEnum[ActivityEnum(activity.__class__).name].value
    activity_const = _make_constant_from_activity(activity)
    activity_atom = Atom(activity_name, [activity_const])
    s.add(activity_atom)
    if hasattr(activity, "uis"):
        for ui in activity.uis:
            ui_name = TranslationEnum["UNIT_OF_INFORMATION"].value
            ui_type_const = TranslationEnum[ui.type.name].value
            ui_label_const = quote_string(ui.label)
            ui_atom = Atom(ui_name, [activity_const, ui_type_const, ui_label_const])
            s.add(ui_atom)
    labeled_name = TranslationEnum["LABELED"].value
    label_const = _make_constant_from_label(activity.label)
    labeled_atom = Atom(labeled_name, [activity_const, label_const])
    s.add(labeled_atom)
    if hasattr(activity, "compartment"):
        if activity.compartment:
            localized_name = TranslationEnum["LOCALIZED"].value
            compartment_const = _make_constant_from_compartment(activity.compartment)
            localized_atom = Atom(localized_name, [activity_const, compartment_const])
            s.add(localized_atom)
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
            child_const = _make_constant_from_activity(child)
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
        source_const = _make_constant_from_activity(source)
    target_const = _make_constant_from_process(mod.target)
    mod_atom = Atom(mod_name, [source_const, target_const])
    s.add(mod_atom)
    return s
