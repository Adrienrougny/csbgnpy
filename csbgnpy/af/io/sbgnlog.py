from csbgnpy.utils import *
from csbgnpy.af.compartment import *
from csbgnpy.af.activity import *
from csbgnpy.af.modulation import *
from csbgnpy.af.lo import *
from csbgnpy.af.ui import *
from csbgnpy.af.network import *
from csbgnpy.af.io.utils import *

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
    UNDEFINED = "undefined"
    UNSET = "unset"
    VOID = "void"
    COMPLEX = "complex"
    UNSPECIFIED_ENTITY = "unspecifiedentity"
    PERTURBATION = "perturbation"
    MACROMOLECULE = "macromolecule"
    NUCLEIC_ACID_FEATURE = "nucleicacidfeature"
    SIMPLE_CHEMICAL = "simplechemical"

    """TO DO :
    - put a lexicographic order for logical operator nodes so that any logical function can be uniquely identified by its constant
    same for processes (sets of reactants and products)
    """

def write(net, filename):
    sbgnlog = network_to_atoms(net)
    f = open(filename, 'w')
    f.write('\n'.join(sorted([str(atom) for atom in sbgnlog])))
    f.close()

def network_to_atoms(net):
    s = set()
    for activity in net.activities:
        s |= _activity_to_atoms(activity)
    for comp in net.compartments:
        s |= _compartment_to_atoms(comp)
    for op in net.los:
        s |= _lo_to_atoms(op)
    for mod in net.modulations:
        s |= _modulation_to_atoms(mod)
    return s

def _ui_to_constant(ui):
    const = TranslationEnum[ui.type.name].value
    if ui.label:
        const += '_'
        const += normalize_string(ui.label)
    return Constant(const)

def _activity_to_constant(activity):
    const = "a_{}".format(TranslationEnum[ActivityEnum(activity.__class__).name].value)
    if hasattr(activity, "uis") and len(activity.uis) > 0:
        const += '_'
        const += '_'.join([str(_ui_to_constant(ui)) for ui in activity.uis])
    const += "_{}".format(normalize_string(activity.label))
    if hasattr(activity, "compartment"):
        if activity.compartment:
            const += "_{0}".format(_compartment_to_constant(activity.compartment))
    return Constant(const)

def _compartment_to_constant(compartment):
    const = "c_"
    const += comp.label
    return Constant(normalize_string(const))

def _label_to_constant(label):
    if label is None:
        label = ""
    return Constant(quote_string(label))

def _lo_to_constant(op):
    const = "lo_{}".format(TranslationEnum[LogicalOperatorEnum(op.__class__).name].value)
    for child in op.children:
        if isinstance(child, LogicalOperator):
            const += "_{0}".format(_lo_to_constant(child))
        else:
            const += "_{0}".format(_activity_to_constant(child))
    return Constant(const)

def _activity_to_atoms(activity):
    s = set()
    activity_name = TranslationEnum[ActivityEnum(activity.__class__).name].value
    activity_const = _activity_to_constant(activity)
    activity_atom = Atom(activity_name, [activity_const])
    s.add(activity_atom)
    if hasattr(activity, "uis"):
        for ui in activity.uis:
            ui_name = TranslationEnum["UNIT_OF_INFORMATION"].value
            ui_type_const = TranslationEnum[ui.type.name].value
            if ui.label:
                ui_label_const = quote_string(escape_string(ui.label))
            else:
                ui_label_const = TranslationEnum["VOID"].value
            ui_atom = Atom(ui_name, [activity_const, ui_type_const, ui_label_const])
            s.add(ui_atom)
    labeled_name = TranslationEnum["LABELED"].value
    label_const = _label_to_constant(escape_string(activity.label))
    labeled_atom = Atom(labeled_name, [activity_const, label_const])
    s.add(labeled_atom)
    if hasattr(activity, "compartment"):
        if activity.compartment:
            localized_name = TranslationEnum["LOCALIZED"].value
            compartment_const = _compartment_to_constant(activity.compartment)
            localized_atom = Atom(localized_name, [activity_const, compartment_const])
            s.add(localized_atom)
    return s

def _compartment_to_atoms(comp):
    s = set()
    comp_name = TranslationEnum["COMPARTMENT"].value
    comp_const = _compartment_to_constant(comp)
    comp_atom = Atom(comp_name, [comp_const])
    s.add(comp_atom)
    labeled_name = TranslationEnum["LABELED"].value
    label_const = _label_to_constant(escape_string(comp.label))
    labeled_atom = Atom(labeled_name, [comp_const, label_const])
    s.add(labeled_atom)
    return s

def _lo_to_atoms(op):
    s = set()
    op_name = TranslationEnum[LogicalOperatorEnum(op.__class__).name].value
    op_const = _lo_to_constant(op)
    op_atom = Atom(op_name, [op_const])
    s.add(op_atom)
    for child in op.children:
        if isinstance(child, LogicalOperator):
            child_const = _lo_to_constant(child)
        else:
            child_const = _activity_to_constant(child)
        input_name = TranslationEnum["INPUT"].value
        input_atom = Atom(input_name, [child_const, op_const])
        s.add(input_atom)
    return s

def _modulation_to_atoms(mod):
    s = set()
    source = mod.source
    mod_name = TranslationEnum[ModulationEnum(mod.__class__).name].value
    if isinstance(source, LogicalOperator):
        source_const = _lo_to_constant(source)
    else:
        source_const = _activity_to_constant(source)
    target_const = _activity_to_constant(mod.target)
    mod_atom = Atom(mod_name, [source_const, target_const])
    s.add(mod_atom)
    return s

def read(*filenames):
    net = Network()
    atoms = set()
    for filename in filenames:
        f = open(filename)
        for line in f:
            if line[-1] == "\n":
                line = line[:-1]
            atom = parse_atom(line)
            atoms.add(atom)
    net = atoms_to_network(atoms)
    return net

def atoms_to_network(atoms):
    net = Network()
    for atom in atoms:
        if atom.name == TranslationEnum["COMPARTMENT"].value:
            comp_atoms = _get_compartment_atoms_by_const(atom.arguments[0])
            comp = _atoms_to_compartment(comp_atoms, atoms)
            net.add_compartment(comp)
        elif atom.name in [TranslationEnum[c.name].value for c in ActivityEnum]:
            act_atoms = _get_activity_atoms_by_const(atom.arguments[0], atoms)
            a = _atoms_to_activity(act_atoms, atoms)
            net.add_activity(a)
        elif atom.name in [TranslationEnum[c.name].value for c in LogicalOperatorEnum]:
            lo_atoms = _get_lo_atoms_by_const(atom.arguments[0], atoms)
            op = _atoms_to_lo(lo_atoms, atoms)
            net.add_lo(op)
        elif atom.name in [TranslationEnum[c.name].value for c in ModulationEnum]:
            mod = _atom_to_modulation(atom, atoms)
            net.add_modulation(mod)
    return net

def _get_activity_atoms_by_const(const, atoms):
    selatoms = set()
    for atom in atoms:
        if const in atom.arguments and (atom.name in [TranslationEnum[c.name].value for c in ActivityEnum] or atom.name == TranslationEnum["LABELED"].value or atom.name == TranslationEnum["LOCALIZED"].value or atom.name == TranslationEnum["UNIT_OF_INFORMATION"].value):
            selatoms.add(atom)
    return selatoms

def _get_compartment_atoms_by_const(const, atoms):
    selatoms = set()
    for atom in atoms:
        if const in atom.arguments and (atom.name == TranslationEnum["COMPARTMENT"].value or atom.name == TranslationEnum["LABELED"].value or atom.name == TranslationEnum["UNIT_OF_INFORMATION"].value):
            selatoms.add(atom)
    return selatoms

def _get_lo_atoms_by_const(const, atoms):
    selatoms = set()
    for atom in atoms:
        if atom.name in [TranslationEnum[c.name].value for c in LogicalOperatorEnum] and atom.arguments[0] == const or atom.name == TranslationEnum["INPUT"].value and atom.arguments[1] == const:
            selatoms.add(atom)
    return selatoms

def _atoms_to_compartment(comp_atoms):
    c = Compartment()
    for atom in atoms:
        if atom.name == TranslationEnum["LABELED"].value:
            c.label = deescape_string(str(atom.arguments[1]))
    return c

def _atoms_to_activity(act_atoms, atoms):
    for atom in act_atoms:
        if atom.name in [TranslationEnum[c.name].value for c in ActivityEnum]:
            a = ActivityEnum[TranslationEnum(atom.name).name].value()
            break
    for atom in act_atoms:
        if atom.name == TranslationEnum["LABELED"].value:
            a.label = deescape_string(str(atom.arguments[1]))
        if atom.name == TranslationEnum["UNIT_OF_INFORMATION"].value:
            ui = _atom_to_ui(atom)
            a.uis.append(ui)
        if atom.name == TranslationEnum["LOCALIZED"].value:
            comp_atoms = _get_compartment_atoms_by_const(atom.arguments[1], atoms)
            comp = _atoms_to_compartments(comp_atoms)
            a.compartment = comp
    return a

def _atoms_to_lo(lo_atoms, atoms):
    for atom in lo_atoms:
        if atom.name in [TranslationEnum[c.name].value for c in LogicalOperatorEnum]:
            op = LogicalOperatorEnum[TranslationEnum(atom.name).name].value()
            break
    for atom in lo_atoms:
        if atom.name == TranslationEnum["INPUT"].value:
            child_const = atom.arguments[0]
            child = None
            for atom2 in atoms:
                if atom2.name in [TranslationEnum[c.name].value for c in ActivityEnum] and atom2.arguments[0] == child_const:
                    child_atoms = _get_activity_atoms_by_const(child_const, atoms)
                    child = _atoms_to_activity(child_atoms, atoms)
                    break
            if not child:
                child_atoms = _get_lo_atoms_by_const(child_const, atoms)
                child = _atoms_to_lo(child_atoms, atoms)
            op.add_child(child)
    return op

def _atom_to_modulation(mod_atom, atoms):
    mod = ModulationEnum[TranslationEnum(mod_atom.name).name].value()
    source_const = mod_atom.arguments[0]
    source = None
    for atom in atoms:
        if atom.name in [TranslationEnum[c.name].value for c in ActivityEnum] and atom.arguments[0] == source_const:
            source_atoms = _get_activity_atoms_by_const(source_const, atoms)
            source = _atoms_to_activity(source_atoms, atoms)
            break
    if not source:
        source_atoms = _get_lo_atoms_by_const(source_const, atoms)
        source = _atoms_to_lo(source_atoms, atoms)
    mod.source = source
    target_const = mod_atom.arguments[1]
    target_atoms = _get_activity_atoms_by_const(target_const, atoms)
    target = _atoms_to_activity(target_atoms, atoms)
    mod.target = target
    return mod

def _atom_to_ui(ui_atom):
    ui = UnitOfInformationActivity()
    ui.type = UnitOfInformationActivityType[TranslationEnum(str(ui_atom.arguments[1])).name]
    ui.label = deescape_string(str(ui_atom.arguments[2]))
    return ui
