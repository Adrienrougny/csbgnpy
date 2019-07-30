from math import atan2
from itertools import count

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

class FunctionalTerm(object):
    def __init__(self, name = None, arguments = None):
        self.name = name
        if arguments is None:
            self.arguments = []
        else:
            self.arguments = arguments

    def __str__(self):
        return self.name + "(" + ",".join([str(arg) for arg in self.arguments]) + ")"

    def __hash__(self):
        return hash((self.name, tuple(self.arguments)))

class Const(object):
    def __init__(self, name = None, to_string = False):
        if to_string:
            self.name = '"{}"'.format(name)
        else:
            self.name = name

    def __lt__(self, other):
        return str(self) < str(other)

    def __str__(self):
        if isinstance(self.name, int):
            return str(self.name)
        else:
            return self.name

    def __eq__(self, other):
        return self.__class__ == other.__class__ and str(self) == str(other)

    def __hash__(self):
        return hash((self.__class__, self.name))

class Var(object):
    def __init__(self, name = None):
        self.name = name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.__class__ == other.__class__ and str(self) == str(other)

    def __hash__(self):
        return hash((self.__class__, self.name))

class Atom(object):
    def __init__(self, name = None, arguments = None):
        self.name = name
        if not arguments:
            self.arguments = []
        else:
            self.arguments = arguments

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.name == other.name and self.arguments == other.arguments

    def __str__(self):
        return "{0}({1})".format(self.name, ','.join([str(arg) for arg in self.arguments]))

    def __hash__(self):
        return hash((self.__class__, self.name, tuple(self.arguments)))

class TranslationEnum(Enum):
    AND = "and_pd"
    ASSOCIATION = "association_pd"
    CARDINALITY = "cardinality_pd"
    CATALYSIS  = "catalysis_pd"
    COMPARTMENT = "compartment_pd"
    COMPLEX = "complex_pd"
    COMPLEX_MULTIMER = "multimerOfComplexes_pd"
    COMPONENT = "component_pd"
    CONSUMPTION = "consumption_pd"
    DISSOCIATION  = "dissociation_pd"
    INHIBITION  = "inhibition_pd"
    ABSOLUTE_INHIBITION  = "absoluteInhibition_pd"
    INPUT = "input_pd"
    LABELED = "label_pd"
    # LABEL = "label_pd"
    LOCALIZED = "container_pd"
    MACROMOLECULE = "macromolecule_pd"
    MACROMOLECULE_MULTIMER = "multimerOfMacromolecules_pd"
    MODULATION  = "modulation_pd"
    NECESSARY_STIMULATION  = "necessaryStimulation_pd"
    NOT = "not_pd"
    NUCLEIC_ACID_FEATURE_MULTIMER = "multimerOfNucleicAcidFeatures_pd"
    NUCLEIC_ACID_FEATURE = "nucleicAcidFeature_pd"
    OMITTED_PROCESS = "omittedProcess_pd"
    OR = "or_pd"
    PERTURBING_AGENT = "perturbation_pd"
    PHENOTYPE = "phenotype_pd"
    PROCESS = "process_pd"
    PRODUCT = "production_pd"
    PRODUCTION = "production_pd"
    REACTANT = "consumption_pd"
    SIMPLE_CHEMICAL_MULTIMER = "multimerOfsimpleChemicals_pd"
    SIMPLE_CHEMICAL = "simpleChemical_pd"
    SOURCE = "source_pd"
    SOURCE_AND_SINK = "emptySet_pd"
    STATE_VARIABLE = "stateVariable_pd"
    STIMULATION  = "stimulation_pd"
    TARGET = "target_pd"
    UNCERTAIN_PROCESS  = "uncertainProcess_pd"
    UNDEFINED = "undef"
    UNDEFINED_VAR = "undefVar"
    UNIT_OF_INFORMATION = "unitOfInformation_pd"
    UNKNOWN_INFLUENCE  = "modulation_pd"
    UNSET = "unset"
    UNSPECIFIED_ENTITY = "unspecifiedEntity_pd"
    STOICHIOMETRY = "stoichiometry_pd"
    SUB_UNSPECIFIED_ENTITY = "unspecifiedEntitySubunit_pd"
    SUB_SIMPLE_CHEMICAL = "simpleChemicalSubunit_pd"
    SUB_MACROMOLECULE = "macromoleculeSubunit_pd"
    SUB_NUCLEIC_ACID_FEATURE = "nucleicAcidFeatureSubunit_pd"
    SUB_SIMPLE_CHEMICAL_MULTIMER = "multimerOfSimpleChemicalsSubunit_pd"
    SUB_MACROMOLECULE_MULTIMER = "multimerOfMacromoleculesSubunit_pd"
    SUB_NUCLEIC_ACID_FEATURE_MULTIMER = "multimerOfNucleicAcidFeaturesSubunit_pd"
    SUB_COMPLEX = "complexSubunit_pd"
    SUB_COMPLEX_MULTIMER = "multimerOfComplexSubunit_pd"

def _new_entity_const(dcounter):
    dcounter["entity"] += 1
    return Const("e{}".format(dcounter["entity"]))

def _new_subentity_const(dcounter):
    dcounter["subentity"] += 1
    return Const("s{}".format(dcounter["subentity"]))

def _new_process_const(dcounter):
    dcounter["process"] += 1
    return Const("p{}".format(dcounter["process"]))

def _new_modulation_const(dcounter):
    dcounter["modulation"] += 1
    return Const("m{}".format(dcounter["modulation"]))

def _new_compartment_const(dcounter):
    dcounter["compartment"] += 1
    return Const("c{}".format(dcounter["compartment"]))

def _new_lo_const(dcounter):
    dcounter["lo"] += 1
    return Const("o{}".format(dcounter["lo"]))

def _new_flux_const(dcounter):
    dcounter["flux"] += 1
    return Const("f{}".format(dcounter["flux"]))

def write(net, filename, use_ids = False, suffix = "", endstr = "."):
    sbgnlog = network_to_atoms(net, use_ids, suffix)
    f = open(filename, 'w')
    f.write("\n".join(sorted(["{}{}".format(str(atom), endstr) for atom in sbgnlog])))
    f.close()

def network_to_atoms(net, use_ids = False, suffix = ''):
    s = set()
    dconst = {}
    dcounter = {"entity": 0, "subentity": 0, "process": 0, "modulation": 0, "lo": 0, "flux": 0, "compartment": 0}
    for entity in net.entities:
        s |= _entity_to_atoms(entity, dconst, dcounter, use_ids, suffix)
    for comp in net.compartments:
        s |= _compartment_to_atoms(comp, dconst, dcounter, use_ids, suffix)
    for op in net.los:
        s |= _lo_to_atoms(op, dconst, dcounter, use_ids, suffix)
    for mod in net.modulations:
        s |= _modulation_to_atoms(mod, dconst, dcounter, use_ids, suffix)
    for proc in net.processes:
        s |= _process_to_atoms(proc, dconst, dcounter, use_ids, suffix)
    return s

def _entity_to_atoms(entity, dconst, dcounter, use_ids = False, suffix = ""):
    s = set()
    entity_name = TranslationEnum[EntityEnum(entity.__class__).name].value + suffix
    if entity in dconst:
        entity_const = dconst[entity]
    else:
        if use_ids:
            entity_const = Const(entity.id, to_string = True)
        else:
            entity_const = _new_entity_const(dcounter)
    entity_atom = Atom(entity_name, [entity_const])
    s.add(entity_atom)
    dconst[entity] = entity_const
    if hasattr(entity, "uis"):
        for ui in entity.uis:
            if ui.prefix and ui.prefix == "N":
                ui_name = TranslationEnum["CARDINALITY"].value + suffix
                ui_const = Const(ui.label)
                ui_atom = Atom(ui_name, [ui_const])
            else:
                ui_name = TranslationEnum["UNIT_OF_INFORMATION"].value + suffix
                if ui.prefix is None:
                    ui_pre_const = Const(TranslationEnum["UNDEFINED"].value)
                else:
                    ui_pre_const = Const(quote_string(ui.prefix))
                ui_label_const = Const(quote_string(ui.label))
                ui_atom = Atom(ui_name, [entity_const, ui_pre_const, ui_label_const])
            s.add(ui_atom)
    if hasattr(entity, "svs"):
        for sv in entity.svs:
            sv_name = TranslationEnum["STATE_VARIABLE"].value + suffix
            if sv.val is None:
                sv_value_const = Const(TranslationEnum["UNSET"].value)
            else:
                sv_value_const = Const(quote_string(sv.val))
            if isinstance(sv.var, UndefinedVar):
                sv_variable_const = FunctionalTerm(TranslationEnum["UNDEFINED_VAR"].value, [entity_const, Const(sv.var.num)])
            else:
                sv_variable_const = Const(quote_string(sv.var))
            sv_atom = Atom(sv_name, [entity_const, sv_value_const, sv_variable_const])
            s.add(sv_atom)
    if hasattr(entity, "components"):
        for component in entity.components:
            component_name = TranslationEnum["COMPONENT"].value + suffix
            if use_ids:
                component_const = Const(component.id, to_string = True)
            else:
                component_const = _new_subentity_const(dcounter)
            component_atom = Atom(component_name, [entity_const, component_const])
            s.add(component_atom)
            ss = _subentity_to_atoms(component, dconst, dcounter, use_ids, component_const, suffix)
            s |= ss
    if hasattr(entity, "label"):
        labeled_name = TranslationEnum["LABELED"].value + suffix
        label_const = Const(quote_string(escape_string(entity.label)))
        labeled_atom = Atom(labeled_name, [entity_const, label_const])
        s.add(labeled_atom)
    if hasattr(entity, "compartment"):
        if entity.compartment:
            localized_name = TranslationEnum["LOCALIZED"].value + suffix
            if entity.compartment in dconst:
                compartment_const = dconst[entity.compartment]
            else:
                if use_ids:
                    compartment_const = Const(entity.compartment.id, to_string = True)
                else:
                    compartment_const = _new_compartment_const(dcounter)
                dconst[entity.compartment] = compartment_const
            localized_atom = Atom(localized_name, [entity_const, compartment_const])
            s.add(localized_atom)
    return s

def _subentity_to_atoms(subentity, dconst, dcounter, use_ids = False, const = None, suffix = ""):
    s = set()
    subentity_name = TranslationEnum[SubEntityEnum(subentity.__class__).name].value + suffix
    if const:
        subentity_const = const
    else:
        if use_ids:
            subentity_const = Const(subentity.id, to_string = True)
        else:
            subentity_const = _new_subentity_const(dcounter)
    subentity_atom = Atom(subentity_name, [subentity_const])
    s.add(subentity_atom)
    if hasattr(subentity, "uis"):
        for ui in subentity.uis:
            if ui.prefix and ui.prefix == "N":
                ui_name = TranslationEnum["CARDINALITY"].value + suffix
                ui_const = Const(ui.label)
                ui_atom = Atom(ui_name, [ui_const])
            else:
                ui_name = TranslationEnum["UNIT_OF_INFORMATION"].value + suffix
                if ui.prefix is None:
                    ui_pre_const = Const(TranslationEnum["UNDEFINED"].value)
                else:
                    ui_pre_const = Const(quote_string(ui.prefix))
                ui_label_const = Const(quote_string(ui.label))
                ui_atom = Atom(ui_name, [subentity_const, ui_pre_const, ui_label_const])
            s.add(ui_atom)
    if hasattr(subentity, "svs"):
        for sv in subentity.svs:
            sv_name = TranslationEnum["STATE_VARIABLE"].value + suffix
            if sv.val is None:
                sv_value_const = Const(TranslationEnum["UNSET"].value)
            else:
                sv_value_const = Const(quote_string(sv.val))
            if isinstance(sv.var, UndefinedVar):
                sv_variable_const = FunctionalTerm(TranslationEnum["UNDEFINED_VAR"].value, [subentity_const, Const(sv.var.num)])
            else:
                sv_variable_const = Const(quote_string(sv.var))
            sv_atom = Atom(sv_name, [subentity_const, sv_value_const, sv_variable_const])
            s.add(sv_atom)
    if hasattr(subentity, "components"):
        for component in subentity.components:
            component_name = TranslationEnum["COMPONENT"].value + suffix
            if use_ids:
                component_const = Const(component.id, to_string = True)
            else:
                component_const = _new_subsubentity_const(dcounter)
            component_atom = Atom(component_name, [subentity_const, component_const])
            s.add(component_atom)
            ss = _subsubentity_to_atoms(component, use_ids, component_const, suffix)
            s |= ss
    if hasattr(subentity, "label"):
        labeled_name = TranslationEnum["LABELED"].value + suffix
        label_const = Const(quote_string(escape_string(subentity.label)))
        labeled_atom = Atom(labeled_name, [subentity_const, label_const])
        s.add(labeled_atom)
    return s

def _compartment_to_atoms(comp, dconst, dcounter, use_ids = False, suffix = ""):
    s = set()
    comp_name = TranslationEnum["COMPARTMENT"].value + suffix
    if comp in dconst:
        comp_const = dconst[comp]
    else:
        if use_ids:
            comp_const = Const(comp.id, to_string = True)
        else:
            comp_const = _new_compartment_const(dcounter)
    comp_atom = Atom(comp_name, [comp_const])
    s.add(comp_atom)
    if hasattr(comp, "uis"):
        ui_name = TranslationEnum["UNIT_OF_INFORMATION"].value + suffix
        for ui in comp.uis:
            if ui.prefix is None:
                ui_pre_const = Const(TranslationEnum["UNDEFINED"].value)
            else:
                ui_pre_const = Const(quote_string(ui.prefix))
            ui_label_const = Const(quote_string(ui.label))
            ui_atom = Atom(ui_name, [comp_const, ui_pre_const, ui_label_const])
            s.add(ui_atom)
    if hasattr(comp, "label"):
        labeled_name = TranslationEnum["LABELED"].value + suffix
        label_const = Const(quote_string(escape_string(comp.label)))
        labeled_atom = Atom(labeled_name, [comp_const, label_const])
        s.add(labeled_atom)
    return s

def _lo_to_atoms(op, dconst, dcounter, use_ids = False, suffix = ""):
    s = set()
    op_name = TranslationEnum[LogicalOperatorEnum(op.__class__).name].value + suffix
    if op in dconst:
        op_const = dconst[op]
    else:
        if use_ids:
            op_const = Const(op.id, to_string = True)
        else:
            op_const = _new_lo_const(dcounter)
    op_atom = Atom(op_name, [op_const])
    s.add(op_atom)
    for child in op.children:
        if child in dconst:
            child_const = dconst[child]
        else:
            if use_ids:
                child_const = Const(child.id, to_string = True)
            else:
                if isinstance(child, LogicalOperator):
                    child_const = _new_lo_const(dcounter)
                else:
                    child_const = _new_entity_const(dcounter)
            dconst[child] = child_const
        input_name = TranslationEnum["INPUT"].value + suffix
        input_atom = Atom(input_name, [child_const, op_const])
        s.add(input_atom)
    return s

def _modulation_to_atoms(mod, dconst, dcounter, use_ids = False, suffix = ""):
    s = set()
    mod_name = TranslationEnum[ModulationEnum(mod.__class__).name].value + suffix
    if mod in dconst:
        mod_const = dconst[mod]
    else:
        if use_ids:
            mod_const = Const(mod.id, to_string = True)
        else:
            mod_const = _new_modulation_const(dcounter)
        dconst[mod] = mod_const
    mod_atom = Atom(mod_name, [mod_const])
    s.add(mod_atom)
    source_name = TranslationEnum["SOURCE"].value + suffix
    if mod.source in dconst:
        source_const = dconst[mod.source]
    else:
        if use_ids:
            source_const = Const(mod.source.id, to_string = True)
        else:
            if isinstance(mod.source, LogicalOperator):
                source_const = _new_lo_const(dcounter)
            else:
                source_const = _new_entity_const(dcounter)
        dconst[mod.source] = source_const
    source_atom = Atom(source_name, [mod_const, source_const])
    s.add(source_atom)
    target_name = TranslationEnum["TARGET"].value + suffix
    if mod.target in dconst:
        target_const = dconst[mod.target]
    else:
        if use_ids:
            target_const = Const(mod.target.id, to_string = True)
        else:
            target_const = _new_process_const(dcounter)
        dconst[mod.target] = target_const
    target_atom = Atom(target_name, [mod_const, target_const])
    s.add(target_atom)
    return s

def _process_to_atoms(proc, dconst, dcounter, use_ids = False, suffix = ""):
    s = set()
    proc_name = TranslationEnum[ProcessEnum(proc.__class__).name].value + suffix
    if proc in dconst:
        proc_const = dconst[proc]
    else:
        if use_ids:
            proc_const = Const(proc.id, to_string = True)
        else:
            proc_const = _new_process_const(dcounter)
        dconst[proc] = proc_const
    proc_atom = Atom(proc_name, [proc_const])
    s.add(proc_atom)
    card_name = TranslationEnum["STOICHIOMETRY"].value + suffix
    cons_name = TranslationEnum["CONSUMPTION"].value + suffix
    prod_name = TranslationEnum["PRODUCTION"].value + suffix
    source_name = TranslationEnum["SOURCE"].value + suffix
    target_name = TranslationEnum["TARGET"].value + suffix
    if hasattr(proc, "reactants"):
        for reac in set(proc.reactants):
            if use_ids:
                cons_const = Const("cons_{}_{}".format(proc.id, reac.id), to_string = True)
            else:
                cons_const = _new_flux_const(dcounter)
            cons_atom = Atom(cons_name, [cons_const])
            s.add(cons_atom)
            card_const = Const(proc.reactants.count(reac))
            card_atom = Atom(card_name, [cons_const, card_const])
            s.add(card_atom)
            if reac in dconst:
                source_const = dconst[reac]
            else:
                if use_ids:
                    source_const = Const(reac.id, to_string = True)
                else:
                    source_const = _new_entity_const(dcounter)
                dconst[reac] = source_const
            source_atom = Atom(source_name, [cons_const, source_const])
            s.add(source_atom)
            target_atom = Atom(target_name, [cons_const, proc_const])
            s.add(target_atom)
    if hasattr(proc, "products"):
        for prod in set(proc.products):
            if use_ids:
                prod_const = Const("prod_{}_{}".format(proc.id, prod.id), to_string = True)
            else:
                prod_const = _new_flux_const(dcounter)
            prod_atom = Atom(prod_name, [prod_const])
            s.add(prod_atom)
            card_const = Const(proc.products.count(prod))
            card_atom = Atom(card_name, [prod_const, card_const])
            s.add(card_atom)
            if prod in dconst:
                target_const = dconst[prod]
            else:
                if use_ids:
                    target_const = Const(prod.id, to_string = True)
                else:
                    target_const = _new_entity_const(dcounter)
                dconst[prod] = target_const
            target_atom = Atom(target_name, [prod_const, target_const])
            s.add(target_atom)
            source_atom = Atom(source_name, [prod_const, proc_const])
            s.add(source_atom)
    if hasattr(proc, "label"):
        labeled_name = TranslationEnum["LABELED"].value + suffix
        label_const = Const(quote_string(escape_string(proc.label)))
        labeled_atom = Atom(labeled_name, [proc_const, label_const])
        s.add(labeled_atom)
    return s

# def read(*filenames, suffix = ""):
#     net = Network()
#     atoms = set()
#     for filename in filenames:
#         f = open(filename)
#         for line in f:
#             if line[-1] == "\n":
#                 line = line[:-1]
#             atom = logicpy.parse.parse_atom(line)
#             atoms.add(atom)
#     net = atoms_to_network(atoms, suffix)
#     return net
#
# def atoms_to_network(atoms, suffix = ""):
#     net = Network()
#     for atom in atoms:
#         atom_name = rem_suffix(atom.name, suffix)
#         if atom_name == TranslationEnum["COMPARTMENT"].value:
#             comp_atoms = _get_compartment_atoms_by_const(atom.arguments[0], atoms, suffix)
#             comp = _atoms_to_compartment(comp_atoms, suffix)
#             net.add_compartment(comp)
#         elif atom_name in [TranslationEnum[c.name].value for c in EntityEnum]:
#             entity_atoms = _get_entity_atoms_by_const(atom.arguments[0], atoms, suffix)
#             entity = _atoms_to_entity(entity_atoms, atoms, suffix)
#             net.add_entity(entity)
#         elif atom_name in [TranslationEnum[c.name].value for c in LogicalOperatorEnum]:
#             lo_atoms = _get_lo_atoms_by_const(atom.arguments[0], atoms, suffix)
#             op = _atoms_to_lo(lo_atoms, atoms, suffix)
#             net.add_lo(op)
#         elif atom_name in [TranslationEnum[c.name].value for c in ProcessEnum]:
#             proc_atoms = _get_process_atoms_by_const(atom.arguments[0], atoms, suffix)
#             proc = _atoms_to_process(proc_atoms, atoms, suffix)
#             net.add_process(proc)
#         elif atom_name in [TranslationEnum[c.name].value for c in ModulationEnum]:
#             mod = _atom_to_modulation(atom, atoms, suffix)
#             net.add_modulation(mod)
#     return net
#
# def _get_entity_atoms_by_const(const, atoms, suffix = ""):
#     selatoms = set()
#     for atom in atoms:
#         atom_name = rem_suffix(atom.name, suffix)
#         if atom.arguments[0] == const and (atom_name in [TranslationEnum[c.name].value for c in EntityEnum] or atom_name == TranslationEnum["LABELED"].value or atom_name == TranslationEnum["LOCALIZED"].value or atom_name == TranslationEnum["UNIT_OF_INFORMATION"].value or atom_name == TranslationEnum["STATE_VARIABLE"].value or atom_name == TranslationEnum["COMPONENT"].value):
#             selatoms.add(atom)
#     return selatoms
#
# def _get_subentity_atoms_by_const(const, atoms, suffix = ""):
#     selatoms = set()
#     for atom in atoms:
#         atom_name = rem_suffix(atom.name, suffix)
#         if atom.arguments[0] == const and (atom_name in [TranslationEnum[c.name].value for c in SubEntityEnum] or atom_name == TranslationEnum["LABELED"].value or atom_name == TranslationEnum["UNIT_OF_INFORMATION"].value or atom_name == TranslationEnum["STATE_VARIABLE"].value or atom_name == TranslationEnum["COMPONENT"].value):
#             selatoms.add(atom)
#     return selatoms
#
# def _get_compartment_atoms_by_const(const, atoms, suffix = ""):
#     selatoms = set()
#     for atom in atoms:
#         atom_name = rem_suffix(atom.name, suffix)
#         if const in atom.arguments and (atom_name == TranslationEnum["COMPARTMENT"].value or atom_name == TranslationEnum["LABELED"].value or atom_name == TranslationEnum["UNIT_OF_INFORMATION"].value):
#             selatoms.add(atom)
#     return selatoms
#
# def _get_lo_atoms_by_const(const, atoms, suffix = ""):
#     selatoms = set()
#     for atom in atoms:
#         atom_name = rem_suffix(atom.name, suffix)
#         if atom_name in [TranslationEnum[c.name].value for c in LogicalOperatorEnum] and atom.arguments[0] == const or atom_name == TranslationEnum["INPUT"].value and atom.arguments[1] == const:
#             selatoms.add(atom)
#     return selatoms
#
# def _get_process_atoms_by_const(const, atoms, suffix = ""):
#     selatoms = set()
#     for atom in atoms:
#         atom_name = rem_suffix(atom.name, suffix)
#         if const in atom.arguments and (atom_name in [TranslationEnum[c.name].value for c in ProcessEnum] or atom_name == TranslationEnum["REACTANT"].value or atom_name == TranslationEnum["PRODUCT"].value or atom_name == TranslationEnum["LABELED"].value):
#             selatoms.add(atom)
#     return selatoms
#
# def _atoms_to_compartment(comp_atoms, suffix = ""):
#     c = Compartment()
#     for atom in comp_atoms:
#         atom_name = rem_suffix(atom.name, suffix)
#         if atom_name == TranslationEnum["LABELED"].value:
#             c.label = deescape_string(str(atom.arguments[1]))
#     return c
#
# def _atoms_to_entity(entity_atoms, atoms, suffix = ""):
#     for atom in entity_atoms:
#         atom_name = rem_suffix(atom.name, suffix)
#         if atom_name in [TranslationEnum[c.name].value for c in EntityEnum]:
#             e = EntityEnum[TranslationEnum(atom_name).name].value()
#             break
#     for atom in entity_atoms:
#         atom_name = rem_suffix(atom.name, suffix)
#         if atom_name == TranslationEnum["LABELED"].value:
#             if len(str(atom.arguments[1])) != 0:
#                 e.label = deescape_string(str(atom.arguments[1]))
#         elif atom_name == TranslationEnum["UNIT_OF_INFORMATION"].value:
#             ui = _atom_to_ui(atom)
#             e.uis.append(ui)
#         elif atom_name == TranslationEnum["STATE_VARIABLE"].value:
#             sv = _atom_to_sv(atom)
#             e.svs.append(sv)
#         elif atom_name == TranslationEnum["LOCALIZED"].value:
#             comp_atoms = _get_compartment_atoms_by_const(atom.arguments[1], atoms, suffix)
#             comp = _atoms_to_compartment(comp_atoms, suffix)
#             e.compartment = comp
#         elif atom_name == TranslationEnum["COMPONENT"].value:
#             subentity_atoms = _get_subentity_atoms_by_const(atom.arguments[1], atoms, suffix)
#             subentity = _atoms_to_subentity(subentity_atoms, atoms, suffix)
#             e.components.append(subentity)
#     return e
#
# def _atoms_to_subentity(subentity_atoms, atoms, suffix = ""):
#     for atom in subentity_atoms:
#         atom_name = rem_suffix(atom.name, suffix)
#         if atom_name in [TranslationEnum[c.name].value for c in SubEntityEnum]:
#             e = SubEntityEnum[TranslationEnum(atom_name).name].value()
#             break
#     for atom in subentity_atoms:
#         atom_name = rem_suffix(atom.name, suffix)
#         if atom_name == TranslationEnum["LABELED"].value:
#             if len(str(atom.arguments[1])) != 0:
#                 e.label = deescape_string(str(atom.arguments[1]))
#         elif atom_name == TranslationEnum["UNIT_OF_INFORMATION"].value:
#             ui = _atom_to_ui(atom)
#             e.uis.append(ui)
#         elif atom_name == TranslationEnum["STATE_VARIABLE"].value:
#             sv = _atom_to_sv(atom)
#             e.svs.append(sv)
#         elif atom_name == TranslationEnum["COMPONENT"].value:
#             subsubentity_atoms = _get_subentity_atoms_by_const(atom.arguments[1], atoms, suffix)
#             subsubentity = _atoms_to_subentity(subentity_atoms, atoms, suffix)
#             e.components.append(subsubentity)
#     return e
#
# def _atoms_to_lo(lo_atoms, atoms, suffix = ""):
#     for atom in lo_atoms:
#         atom_name = rem_suffix(atom.name, suffix)
#         if atom_name in [TranslationEnum[c.name].value for c in LogicalOperatorEnum]:
#             op = LogicalOperatorEnum[TranslationEnum(atom_name).name].value()
#             break
#     for atom in lo_atoms:
#         atom_name = rem_suffix(atom.name, suffix)
#         if atom_name == TranslationEnum["INPUT"].value:
#             child_const = atom.arguments[0]
#             child = None
#             for atom2 in atoms:
#                 atom2_name = rem_suffix(atom2.name, suffix)
#                 if atom2_name in [TranslationEnum[c.name].value for c in EntityEnum] and atom2.arguments[0] == child_const:
#                     child_atoms = _get_entity_atoms_by_const(child_const, atoms, suffix)
#                     child = _atoms_to_entity(child_atoms, atoms, suffix)
#                     break
#             if not child:
#                 child_atoms = _get_lo_atoms_by_const(child_const, atoms, suffix)
#                 child = _atoms_to_lo(child_atoms, atoms, suffix)
#             op.add_child(child)
#     return op
#
# def _atoms_to_process(proc_atoms, atoms, suffix = ""):
#     for atom in proc_atoms:
#         atom_name = rem_suffix(atom.name, suffix)
#         if atom_name in [TranslationEnum[c.name].value for c in ProcessEnum]:
#             proc = ProcessEnum[TranslationEnum(atom_name).name].value()
#             break
#     for atom in proc_atoms:
#         atom_name = rem_suffix(atom.name, suffix)
#         if atom_name == TranslationEnum["REACTANT"].value:
#             reactant_const = atom.arguments[1]
#             card_const = atom.arguments[2]
#             reactant_atoms = _get_entity_atoms_by_const(reactant_const, atoms, suffix)
#             reactant = _atoms_to_entity(reactant_atoms, atoms, suffix)
#             for i in range(int(str(card_const))):
#                 proc.add_reactant(reactant)
#         elif atom_name == TranslationEnum["PRODUCT"].value:
#             product_const = atom.arguments[1]
#             card_const = atom.arguments[2]
#             product_atoms = _get_entity_atoms_by_const(product_const, atoms, suffix)
#             product = _atoms_to_entity(product_atoms, atoms, suffix)
#             for i in range(int(str(card_const))):
#                 proc.add_product(product)
#         elif atom_name == TranslationEnum["LABELED"].value:
#             proc.label = deescape(atom.arguments[1])
#     return proc
#
# def _atom_to_modulation(mod_atom, atoms, suffix = ""):
#     atom_name = rem_suffix(mod_atom.name, suffix)
#     mod = ModulationEnum[TranslationEnum(atom_name).name].value()
#     source_const = mod_atom.arguments[0]
#     source = None
#     for atom in atoms:
#         atom_name = rem_suffix(atom.name, suffix)
#         if atom_name in [TranslationEnum[c.name].value for c in EntityEnum] and atom.arguments[0] == source_const:
#             source_atoms = _get_entity_atoms_by_const(source_const, atoms, suffix)
#             source = _atoms_to_entity(source_atoms, atoms, suffix)
#             break
#     if not source:
#         source_atoms = _get_lo_atoms_by_const(source_const, atoms, suffix)
#         source = _atoms_to_lo(source_atoms, atoms, suffix)
#     mod.source = source
#     target_const = mod_atom.arguments[1]
#     target_atoms = _get_process_atoms_by_const(target_const, atoms, suffix)
#     target = _atoms_to_process(target_atoms, atoms, suffix)
#     mod.target = target
#     return mod
#
# def _atom_to_ui(ui_atom):
#     ui = UnitOfInformation()
#     if ui_atom.arguments[1] != TranslationEnum["VOID"].value:
#         ui.prefix = str(ui_atom.arguments[1])
#     ui.label = str(ui_atom.arguments[2])
#     return ui
#
# def _atom_to_sv(sv_atom):
#     sv = StateVariable()
#     if str(sv_atom.arguments[1]) != TranslationEnum["UNSET"].value:
#         sv.val = str(sv_atom.arguments[1])
#     if isinstance(sv_atom.arguments[2], FunctionalTerm) and sv_atom.arguments[2].name == TranslationEnum["UNDEFINED"].value:
#         sv.var = UndefinedVar(int(str(sv_atom.arguments[2].arguments[0])))
#     else:
#         sv.var = str(sv_atom.arguments[2])
#     return sv
