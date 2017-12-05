from math import atan2

from logicpy import parse

from csbgnpy.utils import *
from csbgnpy.pd.compartment import *
from csbgnpy.pd.entity import *
from csbgnpy.pd.process import *
from csbgnpy.pd.modulation import *
from csbgnpy.pd.lo import *
from csbgnpy.pd.sv import *
from csbgnpy.pd.ui import *
from csbgnpy.pd.network import *
from csbgnpy.pd.io.utils import *

import logicpy.parse
from logicpy.term import *
from logicpy.atom import *

class TranslationEnum(Enum):
    AND = "and_pd"
    ASSOCIATION = "association_pd"
    CARDINALITY = "cardinality_pd"
    CATALYSIS  = "catalyzes_pd"
    COMPARTMENT = "compartment_pd"
    COMPLEX = "complex_pd"
    COMPLEX_MULTIMER = "multimerOfComplexes_pd"
    COMPONENT = "component_pd"
    DISSOCIATION  = "dissociation_pd"
    INHIBITION  = "inhibits_pd"
    INPUT = "input_pd"
    LABELED = "labeled_pd"
    LABEL = "label_pd"
    LOCALIZED = "localized_pd"
    MACROMOLECULE = "macromolecule_pd"
    MACROMOLECULE_MULTIMER = "multimerOfMacromolecules_pd"
    MODULATION  = "modulates_pd"
    NECESSARY_STIMULATION  = "necessarilyStimulates_pd"
    NOT = "not_pd"
    NUCLEIC_ACID_FEATURE_MULTIMER = "multimerOfNucleicAcidFeatures_pd"
    NUCLEIC_ACID_FEATURE = "nucleicAcidFeature_pd"
    OMITTED_PROCESS = "omittedProcess_pd"
    OR = "or_pd"
    PERTURBING_AGENT = "perturbation_pd"
    PHENOTYPE = "phenotype_pd"
    PROCESS = "process_pd"
    PRODUCT = "produces_pd"
    REACTANT = "consumes_pd"
    SIMPLE_CHEMICAL_MULTIMER = "multimerOfsimpleChemicals_pd"
    SIMPLE_CHEMICAL = "simpleChemical_pd"
    SOURCE_AND_SINK = "emptySet_pd"
    STATE_VARIABLE = "stateVariable_pd"
    STIMULATION  = "stimulates_pd"
    UNCERTAIN_PROCESS  = "uncertainProcess_pd"
    UNDEFINED = "undefined_pd"
    UNIT_OF_INFORMATION = "unitOfInformation_pd"
    UNKNOWN_INFLUENCE  = "modulates_pd"
    UNSET = "unset_pd"
    UNSPECIFIED_ENTITY = "unspecifiedEntity_pd"
    VOID = "void_pd"
    SUB_UNSPECIFIED_ENTITY = "subUnspecifiedEntity_pd"
    SUB_SIMPLE_CHEMICAL = "subSimpleChemical_pd"
    SUB_MACROMOLECULE = "subMacromolecule_pd"
    SUB_NUCLEIC_ACID_FEATURE = "subNucleicAcidFeature_pd"
    SUB_SIMPLE_CHEMICAL_MULTIMER = "subSimpleChemicalMultimer_pd"
    SUB_MACROMOLECULE_MULTIMER = "subMacromoleculeMultimer_pd"
    SUB_NUCLEIC_ACID_FEATURE_MULTIMER = "subNucleicAcidFeatureMultimer_pd"
    SUB_COMPLEX = "subComplex_pd"
    SUB_COMPLEX_MULTIMER = "subComplexMultimer_pd"

    """TO DO :
    - put a lexicographic order for logical operator nodes so that any logical function can be uniquely identified by its constant
    same for processes (sets of reactants and products)
    """

def write(net, filename, use_ids = False, suffix = ""):
    sbgnlog = network_to_atoms(net, use_ids, suffix)
    f = open(filename, 'w')
    f.write('\n'.join(sorted([str(atom) for atom in sbgnlog])))
    f.close()

def network_to_atoms(net, use_ids = False, suffix = ''):
    s = set()
    for entity in net.entities:
        s |= _entity_to_atoms(entity, use_ids, suffix)
    for comp in net.compartments:
        s |= _compartment_to_atoms(comp, use_ids, suffix)
    for op in net.los:
        s |= _lo_to_atoms(op, use_ids, suffix)
    for mod in net.modulations:
        s |= _modulation_to_atoms(mod, use_ids, suffix)
    for proc in net.processes:
        s |= _process_to_atoms(proc, use_ids, suffix)
    return s

def _ui_to_constant(ui):
    if ui.prefix is None:
        const = TranslationEnum["VOID"].value
    else:
        const = normalize_string(ui.prefix)
    const += normalize_string(ui.label)
    return Constant(const)

def _sv_to_constant(sv):
    if sv.val is None:
        const = TranslationEnum["UNSET"].value
    else:
        const = normalize_string(sv.val)
    if isinstance(sv.var, UndefinedVar):
        const += "_{0}_{1}".format(TranslationEnum["UNDEFINED"].value, sv.var.num)
    else:
        const += "_{0}".format(normalize_string(sv.var))
    return Constant(const)

def _entity_to_constant(entity):
    const = "e_{}".format(TranslationEnum[EntityEnum(entity.__class__).name].value)
    if hasattr(entity, "uis") and len(entity.uis) > 0:
        const += '_'
        const += '_'.join([str(_ui_to_constant(ui)) for ui in entity.uis])
    if hasattr(entity, "svs") and len(entity.svs) > 0:
        const += '_'
        const += '_'.join([str(_sv_to_constant(sv)) for sv in entity.svs])
    if hasattr(entity, "components") and len(entity.components) > 0:
        const += '_'
        const += '_'.join([str(_subentity_to_constant(subentity)) for subentity in entity.components])
    if hasattr(entity, "label"):
        const += "_{}".format(normalize_string(entity.label) if entity.label else entity.label)
    if hasattr(entity, "compartment"):
        if entity.compartment:
            const += "_{0}".format(_compartment_to_constant(entity.compartment))
    return Constant(const)

def _subentity_to_constant(subentity):
    const = "sube_{}".format(TranslationEnum[SubEntityEnum(subentity.__class__).name].value)
    if hasattr(subentity, "uis") and len(subentity.uis) > 0:
        const += '_'
        const += '_'.join([str(_ui_to_constant(ui)) for ui in subentity.uis])
    if hasattr(subentity, "svs") and len(subentity.svs) > 0:
        const += '_'
        const += '_'.join([str(_sv_to_constant(sv)) for sv in subentity.svs])
    if hasattr(subentity, "components") and len(subentity.components) > 0:
        const += '_'
        const += '_'.join([str(_subentity_to_constant(subsubentity)) for subsubentity in subentity.components])
    const += "_{}".format(normalize_string(subentity.label))
    return Constant(const)

def _compartment_to_constant(comp):
    const = "c_"
    const += comp.label
    return Constant(normalize_string(const))

def _lo_to_constant(op):
    const = "lo_{}".format(TranslationEnum[LogicalOperatorEnum(op.__class__).name].value)
    for child in op.children:
        if isinstance(child, LogicalOperator):
            const += "_{0}".format(_lo_to_constant(child))
        else:
            const += "_{0}".format(_entity_to_constant(child))
    return Constant(const)

def _process_to_constant(proc):
    const = "p"
    const_reacs = []
    const_prods = []
    if hasattr(proc, "label"):
        const += "_{}".format(normalize_string(proc.label))
    if hasattr(proc, "reactants"):
        const += "_"
        for reac in set(proc.reactants):
            if isinstance(reac, EmptySet):
                card_const = 1
            else:
                card_const = proc.reactants.count(reac)
            const_reac = "{}_{}".format(card_const, _entity_to_constant(reac))
            const_reacs.append(const_reac)
    if hasattr(proc, "products"):
        for prod in proc.products:
            if isinstance(prod, EmptySet):
                card_const = 1
            else:
                card_const = proc.products.count(prod)
            const_prod = "{}_{}".format(card_const, _entity_to_constant(prod))
            const_prods.append(const_prod)
        const += '_'.join([str(const) for const in const_reacs]) + '_' + '_'.join([str(const) for const in const_prods])
    return const

def _entity_to_atoms(entity, use_ids = False, suffix = ""):
    s = set()
    entity_name = TranslationEnum[EntityEnum(entity.__class__).name].value + suffix
    if use_ids:
        entity_const = entity.id
    else:
        entity_const = _entity_to_constant(entity)
    entity_atom = Atom(entity_name, [entity_const])
    s.add(entity_atom)
    if hasattr(entity, "uis"):
        for ui in entity.uis:
            ui_name = TranslationEnum["UNIT_OF_INFORMATION"].value + suffix
            if ui.prefix is None:
                ui_pre_const = TranslationEnum["VOID"].value
            else:
                ui_pre_const = quote_string(ui.prefix)
            ui_label_const = quote_string(ui.label)
            ui_atom = Atom(ui_name, [entity_const, ui_pre_const, ui_label_const])
            s.add(ui_atom)
    if hasattr(entity, "svs"):
        for sv in entity.svs:
            sv_name = TranslationEnum["STATE_VARIABLE"].value + suffix
            if sv.val is None:
                sv_value_const = TranslationEnum["UNSET"].value
            else:
                sv_value_const = quote_string(sv.val)
            if isinstance(sv.var, UndefinedVar):
                sv_variable_const = "{0}({1})".format(TranslationEnum["UNDEFINED"].value, sv.var.num)
            else:
                sv_variable_const = quote_string(sv.var)
            sv_atom = Atom(sv_name, [entity_const, sv_value_const, sv_variable_const])
            s.add(sv_atom)
    if hasattr(entity, "components"):
        for component in entity.components:
            component_name = TranslationEnum["COMPONENT"].value + suffix
            if use_ids:
                component_const = component.id
            else:
                component_const = _subentity_to_constant(component)
            component_atom = Atom(component_name, [entity_const, component_const])
            s.add(component_atom)
            ss = _subentity_to_atoms(component, use_ids, suffix)
            s |= ss
    if hasattr(entity, "label"):
        labeled_name = TranslationEnum["LABELED"].value + suffix
        label_const = quote_string(escape_string(entity.label))
        labeled_atom = Atom(labeled_name, [entity_const, label_const])
        s.add(labeled_atom)
    if hasattr(entity, "compartment"):
        if entity.compartment:
            localized_name = TranslationEnum["LOCALIZED"].value + suffix
            compartment_const = _compartment_to_constant(entity.compartment)
            localized_atom = Atom(localized_name, [entity_const, compartment_const])
            s.add(localized_atom)
    return s

def _subentity_to_atoms(subentity, use_ids = False,suffix = ""):
    s = set()
    subentity_name = TranslationEnum[SubEntityEnum(subentity.__class__).name].value + suffix
    if use_ids:
        subentity_const = subentity.id
    else:
        subentity_const = _subentity_to_constant(subentity)
    subentity_atom = Atom(subentity_name, [subentity_const])
    s.add(subentity_atom)
    if hasattr(subentity, "uis"):
        for ui in subentity.uis:
            ui_name = TranslationEnum["UNIT_OF_INFORMATION"].value + suffix
            if ui.prefix is None:
                ui_pre_const = TranslationEnum["VOID"].value
            else:
                ui_pre_const = quote_string(ui.prefix)
            ui_label_const = quote_string(ui.label)
            ui_atom = Atom(ui_name, [subentity_const, ui_pre_const, ui_label_const])
            s.add(ui_atom)
    if hasattr(subentity, "svs"):
        for sv in subentity.svs:
            sv_name = TranslationEnum["STATE_VARIABLE"].value + suffix
            if sv.val is None:
                sv_value_const = TranslationEnum["UNSET"].value
            else:
                sv_value_const = quote_string(sv.val)
            if isinstance(sv.var, UndefinedVar):
                sv_variable_const = "{0}({1})".format(TranslationEnum["UNDEFINED"].value, sv.var.num)
            else:
                sv_variable_const = quote_string(sv.var)
            sv_atom = Atom(sv_name, [subentity_const, sv_value_const, sv_variable_const])
            s.add(sv_atom)
    if hasattr(subentity, "components"):
        for component in subentity.components:
            component_name = TranslationEnum["COMPONENT"].value + suffix
            if use_ids:
                component_const = component.id
            else:
                component_const = _subentity_to_constant(component)
            component_atom = Atom(component_name, [subentity_const, component_const])
            s.add(component_atom)
            ss = _subentity_to_atoms(component, use_ids, suffix)
            s |= ss
    labeled_name = TranslationEnum["LABELED"].value + suffix
    label_const = quote_string(escape_string(subentity.label))
    labeled_atom = Atom(labeled_name, [subentity_const, label_const])
    s.add(labeled_atom)
    return s

def _compartment_to_atoms(comp, use_ids = False, suffix = ""):
    s = set()
    comp_name = TranslationEnum["COMPARTMENT"].value + suffix
    if use_ids:
        comp_const = comp.id
    else:
        comp_const = _compartment_to_constant(comp)
    comp_atom = Atom(comp_name, [comp_const])
    s.add(comp_atom)
    labeled_name = TranslationEnum["LABELED"].value + suffix
    label_const = quote_string(escape_string(comp.label))
    labeled_atom = Atom(labeled_name, [comp_const, label_const])
    s.add(labeled_atom)
    return s

def _lo_to_atoms(op, use_ids = False, suffix = ""):
    s = set()
    op_name = TranslationEnum[LogicalOperatorEnum(op.__class__).name].value + suffix
    if use_ids:
        op_const = op.id
    else:
        op_const = _lo_to_constant(op)
    op_atom = Atom(op_name, [op_const])
    s.add(op_atom)
    for child in op.children:
        if use_ids:
            child_const = child.id
        else:
            if isinstance(child, LogicalOperator):
                child_const = _lo_to_constant(child)
            else:
                child_const = _entity_to_constant(child)
        input_name = TranslationEnum["INPUT"].value + suffix
        input_atom = Atom(input_name, [child_const, op_const])
        s.add(input_atom)
    return s

def _modulation_to_atoms(mod, use_ids = False, suffix = ""):
    s = set()
    source = mod.source
    mod_name = TranslationEnum[ModulationEnum(mod.__class__).name].value + suffix
    if use_ids:
        source_const =source.id
        target_const = mod.target.id
    else:
        if isinstance(source, LogicalOperator):
            source_const = _lo_to_constant(source)
        else:
            source_const = _entity_to_constant(source)
        target_const = _process_to_constant(mod.target)
    mod_atom = Atom(mod_name, [source_const, target_const])
    s.add(mod_atom)
    return s

def _process_to_atoms(proc, use_ids = False, suffix = ""):
    s = set()
    proc_name = TranslationEnum[ProcessEnum(proc.__class__).name].value + suffix
    if use_ids:
        proc_const = proc.id
    else:
        proc_const = _process_to_constant(proc)
    proc_atom = Atom(proc_name, [proc_const])
    s.add(proc_atom)
    if hasattr(proc, "reactants"):
        reac_name = TranslationEnum["REACTANT"].value + suffix
        for reac in set(proc.reactants):
            if isinstance(reac, EmptySet):
                card_const = 1
            else:
                card_const = proc.reactants.count(reac)
            if use_ids:
                reac_const = reac.id
            else:
                reac_const = _entity_to_constant(reac)
            reac_atom = Atom(reac_name, [proc_const, reac_const, card_const])
            s.add(reac_atom)
    if hasattr(proc, "products"):
        prod_name = TranslationEnum["PRODUCT"].value + suffix
        for prod in proc.products:
            if isinstance(prod, EmptySet):
                card_const = 1
            else:
                card_const = proc.products.count(prod)
            if use_ids:
                prod_const = prod.id
            else:
                prod_const = _entity_to_constant(prod)
            prod_atom = Atom(prod_name, [proc_const, prod_const, card_const])
            s.add(prod_atom)
    if hasattr(proc, "label"):
        labeled_name = TranslationEnum["LABELED"].value + suffix
        label_const = quote_string(escape_string(proc.label))
        labeled_atom = Atom(labeled_name, [proc_const, label_const])
        s.add(labeled_atom)
    return s

def read(*filenames, suffix = ""):
    net = Network()
    atoms = set()
    for filename in filenames:
        f = open(filename)
        for line in f:
            if line[-1] == "\n":
                line = line[:-1]
            atom = logicpy.parse.parse_atom(line)
            atoms.add(atom)
    net = atoms_to_network(atoms, suffix)
    return net

def atoms_to_network(atoms, suffix = ""):
    net = Network()
    for atom in atoms:
        atom_name = rem_suffix(atom.name, suffix)
        if atom_name == TranslationEnum["COMPARTMENT"].value:
            comp_atoms = _get_compartment_atoms_by_const(atom.arguments[0], atoms, suffix)
            comp = _atoms_to_compartment(comp_atoms, suffix)
            net.add_compartment(comp)
        elif atom_name in [TranslationEnum[c.name].value for c in EntityEnum]:
            entity_atoms = _get_entity_atoms_by_const(atom.arguments[0], atoms, suffix)
            entity = _atoms_to_entity(entity_atoms, atoms, suffix)
            net.add_entity(entity)
        elif atom_name in [TranslationEnum[c.name].value for c in LogicalOperatorEnum]:
            lo_atoms = _get_lo_atoms_by_const(atom.arguments[0], atoms, suffix)
            op = _atoms_to_lo(lo_atoms, atoms, suffix)
            net.add_lo(op)
        elif atom_name in [TranslationEnum[c.name].value for c in ProcessEnum]:
            proc_atoms = _get_process_atoms_by_const(atom.arguments[0], atoms, suffix)
            proc = _atoms_to_process(proc_atoms, atoms, suffix)
            net.add_process(proc)
        elif atom_name in [TranslationEnum[c.name].value for c in ModulationEnum]:
            mod = _atom_to_modulation(atom, atoms, suffix)
            net.add_modulation(mod)
    return net

def _get_entity_atoms_by_const(const, atoms, suffix = ""):
    selatoms = set()
    for atom in atoms:
        atom_name = rem_suffix(atom.name, suffix)
        if atom.arguments[0] == const and (atom_name in [TranslationEnum[c.name].value for c in EntityEnum] or atom_name == TranslationEnum["LABELED"].value or atom_name == TranslationEnum["LOCALIZED"].value or atom_name == TranslationEnum["UNIT_OF_INFORMATION"].value or atom_name == TranslationEnum["STATE_VARIABLE"].value or atom_name == TranslationEnum["COMPONENT"].value):
            selatoms.add(atom)
    return selatoms

def _get_subentity_atoms_by_const(const, atoms, suffix = ""):
    selatoms = set()
    for atom in atoms:
        atom_name = rem_suffix(atom.name, suffix)
        if atom.arguments[0] == const and (atom_name in [TranslationEnum[c.name].value for c in SubEntityEnum] or atom_name == TranslationEnum["LABELED"].value or atom_name == TranslationEnum["UNIT_OF_INFORMATION"].value or atom_name == TranslationEnum["STATE_VARIABLE"].value or atom_name == TranslationEnum["COMPONENT"].value):
            selatoms.add(atom)
    return selatoms

def _get_compartment_atoms_by_const(const, atoms, suffix = ""):
    selatoms = set()
    for atom in atoms:
        atom_name = rem_suffix(atom.name, suffix)
        if const in atom.arguments and (atom_name == TranslationEnum["COMPARTMENT"].value or atom_name == TranslationEnum["LABELED"].value or atom_name == TranslationEnum["UNIT_OF_INFORMATION"].value):
            selatoms.add(atom)
    return selatoms

def _get_lo_atoms_by_const(const, atoms, suffix = ""):
    selatoms = set()
    for atom in atoms:
        atom_name = rem_suffix(atom.name, suffix)
        if atom_name in [TranslationEnum[c.name].value for c in LogicalOperatorEnum] and atom.arguments[0] == const or atom_name == TranslationEnum["INPUT"].value and atom.arguments[1] == const:
            selatoms.add(atom)
    return selatoms

def _get_process_atoms_by_const(const, atoms, suffix = ""):
    selatoms = set()
    for atom in atoms:
        atom_name = rem_suffix(atom.name, suffix)
        if const in atom.arguments and (atom_name in [TranslationEnum[c.name].value for c in ProcessEnum] or atom_name == TranslationEnum["REACTANT"].value or atom_name == TranslationEnum["PRODUCT"].value or atom_name == TranslationEnum["LABELED"].value):
            selatoms.add(atom)
    return selatoms

def _atoms_to_compartment(comp_atoms, suffix = ""):
    c = Compartment()
    for atom in comp_atoms:
        atom_name = rem_suffix(atom.name, suffix)
        if atom_name == TranslationEnum["LABELED"].value:
            c.label = deescape_string(str(atom.arguments[1]))
    return c

def _atoms_to_entity(entity_atoms, atoms, suffix = ""):
    for atom in entity_atoms:
        atom_name = rem_suffix(atom.name, suffix)
        if atom_name in [TranslationEnum[c.name].value for c in EntityEnum]:
            e = EntityEnum[TranslationEnum(atom_name).name].value()
            break
    for atom in entity_atoms:
        atom_name = rem_suffix(atom.name, suffix)
        if atom_name == TranslationEnum["LABELED"].value:
            if len(str(atom.arguments[1])) != 0:
                e.label = deescape_string(str(atom.arguments[1]))
        elif atom_name == TranslationEnum["UNIT_OF_INFORMATION"].value:
            ui = _atom_to_ui(atom)
            e.uis.append(ui)
        elif atom_name == TranslationEnum["STATE_VARIABLE"].value:
            sv = _atom_to_sv(atom)
            e.svs.append(sv)
        elif atom_name == TranslationEnum["LOCALIZED"].value:
            comp_atoms = _get_compartment_atoms_by_const(atom.arguments[1], atoms, suffix)
            comp = _atoms_to_compartment(comp_atoms, suffix)
            e.compartment = comp
        elif atom_name == TranslationEnum["COMPONENT"].value:
            subentity_atoms = _get_subentity_atoms_by_const(atom.arguments[1], atoms, suffix)
            subentity = _atoms_to_subentity(subentity_atoms, atoms, suffix)
            e.components.append(subentity)
    return e

def _atoms_to_subentity(subentity_atoms, atoms, suffix = ""):
    for atom in subentity_atoms:
        atom_name = rem_suffix(atom.name, suffix)
        if atom_name in [TranslationEnum[c.name].value for c in SubEntityEnum]:
            e = SubEntityEnum[TranslationEnum(atom_name).name].value()
            break
    for atom in subentity_atoms:
        atom_name = rem_suffix(atom.name, suffix)
        if atom_name == TranslationEnum["LABELED"].value:
            if len(str(atom.arguments[1])) != 0:
                e.label = deescape_string(str(atom.arguments[1]))
        elif atom_name == TranslationEnum["UNIT_OF_INFORMATION"].value:
            ui = _atom_to_ui(atom)
            e.uis.append(ui)
        elif atom_name == TranslationEnum["STATE_VARIABLE"].value:
            sv = _atom_to_sv(atom)
            e.svs.append(sv)
        elif atom_name == TranslationEnum["COMPONENT"].value:
            subsubentity_atoms = _get_subentity_atoms_by_const(atom.arguments[1], atoms, suffix)
            subsubentity = _atoms_to_subentity(subentity_atoms, atoms, suffix)
            e.components.append(subsubentity)
    return e

def _atoms_to_lo(lo_atoms, atoms, suffix = ""):
    for atom in lo_atoms:
        atom_name = rem_suffix(atom.name, suffix)
        if atom_name in [TranslationEnum[c.name].value for c in LogicalOperatorEnum]:
            op = LogicalOperatorEnum[TranslationEnum(atom_name).name].value()
            break
    for atom in lo_atoms:
        atom_name = rem_suffix(atom.name, suffix)
        if atom_name == TranslationEnum["INPUT"].value:
            child_const = atom.arguments[0]
            child = None
            for atom2 in atoms:
                atom2_name = rem_suffix(atom2.name, suffix)
                if atom2_name in [TranslationEnum[c.name].value for c in EntityEnum] and atom2.arguments[0] == child_const:
                    child_atoms = _get_entity_atoms_by_const(child_const, atoms, suffix)
                    child = _atoms_to_entity(child_atoms, atoms, suffix)
                    break
            if not child:
                child_atoms = _get_lo_atoms_by_const(child_const, atoms, suffix)
                child = _atoms_to_lo(child_atoms, atoms, suffix)
            op.add_child(child)
    return op

def _atoms_to_process(proc_atoms, atoms, suffix = ""):
    for atom in proc_atoms:
        atom_name = rem_suffix(atom.name, suffix)
        if atom_name in [TranslationEnum[c.name].value for c in ProcessEnum]:
            proc = ProcessEnum[TranslationEnum(atom_name).name].value()
            break
    for atom in proc_atoms:
        atom_name = rem_suffix(atom.name, suffix)
        if atom_name == TranslationEnum["REACTANT"].value:
            reactant_const = atom.arguments[1]
            card_const = atom.arguments[2]
            reactant_atoms = _get_entity_atoms_by_const(reactant_const, atoms, suffix)
            reactant = _atoms_to_entity(reactant_atoms, atoms, suffix)
            for i in range(int(str(card_const))):
                proc.add_reactant(reactant)
        elif atom_name == TranslationEnum["PRODUCT"].value:
            product_const = atom.arguments[1]
            card_const = atom.arguments[2]
            product_atoms = _get_entity_atoms_by_const(product_const, atoms, suffix)
            product = _atoms_to_entity(product_atoms, atoms, suffix)
            for i in range(int(str(card_const))):
                proc.add_product(product)
        elif atom_name == TranslationEnum["LABELED"].value:
            proc.label = deescape(atom.arguments[1])
    return proc

def _atom_to_modulation(mod_atom, atoms, suffix = ""):
    atom_name = rem_suffix(mod_atom.name, suffix)
    mod = ModulationEnum[TranslationEnum(atom_name).name].value()
    source_const = mod_atom.arguments[0]
    source = None
    for atom in atoms:
        atom_name = rem_suffix(atom.name, suffix)
        if atom_name in [TranslationEnum[c.name].value for c in EntityEnum] and atom.arguments[0] == source_const:
            source_atoms = _get_entity_atoms_by_const(source_const, atoms, suffix)
            source = _atoms_to_entity(source_atoms, atoms, suffix)
            break
    if not source:
        source_atoms = _get_lo_atoms_by_const(source_const, atoms, suffix)
        source = _atoms_to_lo(source_atoms, atoms, suffix)
    mod.source = source
    target_const = mod_atom.arguments[1]
    target_atoms = _get_process_atoms_by_const(target_const, atoms, suffix)
    target = _atoms_to_process(target_atoms, atoms, suffix)
    mod.target = target
    return mod

def _atom_to_ui(ui_atom):
    ui = UnitOfInformation()
    if ui_atom.arguments[1] != TranslationEnum["VOID"].value:
        ui.prefix = str(ui_atom.arguments[1])
    ui.label = str(ui_atom.arguments[2])
    return ui

def _atom_to_sv(sv_atom):
    sv = StateVariable()
    if str(sv_atom.arguments[1]) != TranslationEnum["UNSET"].value:
        sv.val = str(sv_atom.arguments[1])
    if isinstance(sv_atom.arguments[2], FunctionalTerm) and sv_atom.arguments[2].name == TranslationEnum["UNDEFINED"].value:
        sv.var = UndefinedVar(int(str(sv_atom.arguments[2].arguments[0])))
    else:
        sv.var = str(sv_atom.arguments[2])
    return sv
