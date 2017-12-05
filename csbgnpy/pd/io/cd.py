from lxml import etree

from csbgnpy.utils import *
from csbgnpy.pd.compartment import *
from csbgnpy.pd.entity import *
from csbgnpy.pd.subentity import *
from csbgnpy.pd.process import *
from csbgnpy.pd.modulation import *
from csbgnpy.pd.lo import *
from csbgnpy.pd.sv import *
from csbgnpy.pd.ui import *
from csbgnpy.pd.network import *

# ns = {"sbml":"http://www.sbml.org/sbml/level2/version4", "cd":"http://www.sbml.org/2001/ns/celldesigner"}

TranslationDic = {
    "PROTEIN": Macromolecule,
    "GENE": Macromolecule,
    "RNA": Macromolecule,
    "ANTISENSE_RNA": Macromolecule,
    "ION": SimpleChemical,
    "SIMPLE_MOLECULE": SimpleChemical,
    "DRUG": UnspecifiedEntity,
    "UNKNOWN": UnspecifiedEntity,
    "COMPLEX": Complex,
    "PROTEIN_HOMODIMER": MacromoleculeMultimer,
    "GENE_HOMODIMER": MacromoleculeMultimer,
    "RNA_HOMODIMER": MacromoleculeMultimer,
    "ANTISENSE_RNA_HOMODIMER": MacromoleculeMultimer,
    "ION_HOMODIMER": SimpleChemicalMultimer,
    "SIMPLE_MOLECULE_HOMODIMER": SimpleChemicalMultimer,
    "COMPLEX_HOMODIMER": ComplexMultimer,
    "SUB_PROTEIN": SubMacromolecule,
    "SUB_GENE": SubMacromolecule,
    "SUB_RNA": SubMacromolecule,
    "SUB_ANTISENSE_RNA": SubMacromolecule,
    "SUB_ION": SubSimpleChemical,
    "SUB_SIMPLE_MOLECULE": SubSimpleChemical,
    "SUB_DRUG": SubUnspecifiedEntity,
    "SUB_UNKNOWN": SubUnspecifiedEntity,
    "SUB_COMPLEX": SubComplex,
    "SUB_PROTEIN_HOMODIMER": SubMacromoleculeMultimer,
    "SUB_GENE_HOMODIMER": SubMacromoleculeMultimer,
    "SUB_RNA_HOMODIMER": SubMacromoleculeMultimer,
    "SUB_ANTISENSE_RNA_HOMODIMER": SubMacromoleculeMultimer,
    "SUB_ION_HOMODIMER": SubSimpleChemicalMultimer,
    "SUB_SIMPLE_MOLECULE_HOMODIMER": SubSimpleChemicalMultimer,
    "SUB_COMPLEX_HOMODIMER": SubComplexMultimer,
    "DEGRADED": EmptySet,
    "PHENOTYPE": Phenotype,
    "phosphorylated": "P",
    "acetylated": "Ac",
    "ubiquitinated": "Ub",
    "methylated": "Me",
    "hydroxylated": "OH",
    "glycosylated": "G",
    "myristoylated": "My",
    "palmytoylated": "Pa",
    "prenylated": "Pr",
    "protonated": "H",
    "sulfated": "S",
    "unknown": "",
    "don't care": "?",
    "empty": None,
    "STATE_TRANSITION": GenericProcess,
    "TRANSLATION": GenericProcess,
    "TRANSCRIPTION": GenericProcess,
    "KNOWN_TRANSITION_OMITTED": OmittedProcess,
    "UNKNOWN_TRANSITION": UncertainProcess,
    "TRANSPORT": GenericProcess,
    "HETERODIMER_ASSOCIATION": Association,
    "DISSOCIATION": Dissociation,
    "TRUNCATION": GenericProcess,
    "CATALYSIS": Catalysis,
    "UNKNOWN_CATALYSIS": Catalysis,
    "INHIBITION": Inhibition,
    "UNKNOWN_INHIBITION": Inhibition,
    "PHYSICAL_STIMULATION": Stimulation,
    "POSITIVE_INFLUENCE": Stimulation,
    "MODULATION": Modulation,
    "TRIGGER": NecessaryStimulation,
    "AND": AndOperator,
    "OR": OrOperator,
    "NOT": NotOperator,
}

def read(*filenames):
    net = Network()
    toskip = 0
    aliases = {}
    for filename in filenames:
        tree = etree.parse(filename)
        ns = tree.getroot().nsmap
        ns["sbml"] = ns[None]
        ns.pop(None)
        for cdcomp in tree.xpath("//sbml:compartment", namespaces = ns): # making compartment
            comp = _make_compartment_from_cd(cdcomp, ns)
            net.add_compartment(comp)
        for cdspecies in tree.xpath("//sbml:species", namespaces = ns): #making entities and phenotypes
            cd_class = cdspecies.xpath(".//celldesigner:class", namespaces = ns)[0].text
            if cd_class == "PHENOTYPE":
                process = _make_phenotype_from_cd(cdspecies, tree, ns)
                net.add_process(process)
            else:
                entity = _make_entity_from_cd(cdspecies, tree, ns)
                net.add_entity(entity)
        for cdproc in tree.xpath("//sbml:reaction", namespaces = ns): # making additional emtyset
            cd_class = cdproc.xpath(".//celldesigner:reactionType", namespaces = ns)[0].text
            if cd_class == "TRANSCRIPTION" or cd_class == "TRANSLATION":
                es = EmptySet("emptyset")
                net.add_entity(es)
                break
        for cdproc in tree.xpath("//sbml:reaction", namespaces = ns): #making processes
            process = _make_process_from_cd(cdproc, tree, ns)
            net.add_process(process)
        for cdproc in tree.xpath("//sbml:reaction", namespaces = ns): # making los
            for cdmod in cdproc.xpath(".//celldesigner:modification", namespaces = ns):
                mtype = cdmod.get("type")
                if mtype.startswith("BOOLEAN"):
                    lo = _make_lo_from_cd(cdmod, tree, ns)
                    net.add_lo(lo)
        for cdproc in tree.xpath("//sbml:reaction", namespaces = ns): # making modulations
            cd_class = cdproc.xpath(".//celldesigner:reactionType", namespaces = ns)[0].text
            if cd_class == "TRANSCRIPTION" or cd_class == "TRANSLATION": # making special modulation in case of translation or transcription
                modulation = NecessaryStimulation()
                sourceid = cdproc.xpath("./sbml:listOfReactants", namespaces = ns)[0].xpath("./sbml:speciesReference", namespaces = ns)[0].get("species")
                cdsource = _get_cdentity_by_id(tree, ns, sourceid)
                source = _make_entity_from_cd(cdsource, tree, ns)
                modulation.source = source
                target = _make_process_from_cd(cdproc, tree, ns)
                modulation.target = target
                net.add_modulation(modulation)
            for cdmod in cdproc.xpath(".//celldesigner:modification", namespaces = ns):
                if not toskip: # when boolean, two next modulations should be skipped
                    modulation = _make_modulation_from_cd(cdmod, tree, ns)
                    net.add_modulation(modulation)
                    mtype = cdmod.get("type")
                    if mtype.startswith("BOOLEAN"):
                        chids = cdmod.get("modifiers").split(',')
                        if isinstance(modulation, Catalysis): #when CATALYSIS, the modulations are repeated after the AND node
                            toskip = len(chids)
                else:
                    toskip -= 1
        # TODO: should be forwarded to Entities objects instead (aliases
        # attribute)
        for node in tree.xpath("//celldesigner:speciesAlias", namespaces=ns):
            aliases[node.get("id")] = node.get("species")
        for node in tree.xpath("//celldesigner:complexSpeciesAlias", namespaces=ns):
            aliases[node.get("id")] = node.get("species")
    net.aliases = aliases
    return net

def _get_cdentity_by_id(tree, ns, id):
    l = tree.xpath("//sbml:species[@id='{0}']".format(id), namespaces = ns)
    if l:
        return l[0]
    raise IdLookupError(id)

def _get_cdcompartment_by_id(tree, ns, id):
    l = tree.xpath("//sbml:compartment[@id='{0}']".format(id), namespaces = ns)
    if l:
        return l[0]
    raise IdLookupError(id)

def _get_cdprocess_by_id(tree, ns, id):
    l = tree.xpath("//sbml:reaction[@id='{0}']".format(id), namespaces = ns)
    if l:
        return l[0]
    raise IdLookupError(id)

def _make_compartment_from_cd(cdcomp, ns):
    comp = Compartment()
    comp.id = cdcomp.get("id")
    comp_label = cdcomp.get("name")
    if comp_label:
        comp.label = comp_label
    return comp

def _make_phenotype_from_cd(cdspecies, tree, ns):
    process = Phenotype()
    process.id = cdspecies.get("id")
    process.label = cdspecies.get("name")
    return process

def _make_entity_from_cd(cdspecies, tree, ns):
    cd_class = cdspecies.xpath(".//celldesigner:class", namespaces = ns)[0].text
    homodimer = len(cdspecies.xpath(".//celldesigner:homodimer", namespaces = ns)) > 0
    if homodimer:
        cd_class = cd_class + "_HOMODIMER"
    if cd_class != "PHENOTYPE":
        entity = TranslationDic[cd_class]()
        entity.id = cdspecies.get("id")
        if hasattr(entity, "label"):
            entity.label = cdspecies.get("name")
        if cd_class == "GENE":
            ui = UnitOfInformation()
            ui.prefix = "ct"
            ui.label = "gene"
            ui.id = entity.id + "_" + "ui"
            entity.add_ui(ui)
        elif cd_class == "RNA" or cd_class == "ANTISENSE_RNA":
            ui = UnitOfInformation()
            ui.prefix = "mt"
            ui.label = "rna"
            ui.id = entity.id + "_" + "ui"
            entity.add_ui(ui)
        if hasattr(entity, "compartment"):
            cid = cdspecies.get("compartment")
            if cid:
                cdcompartment = _get_cdcompartment_by_id(tree, ns, cid)
                compartment = _make_compartment_from_cd(cdcompartment, ns)
                entity.compartment = compartment
        # making svs
        if cd_class == "PROTEIN":
            prid = cdspecies.xpath(".//celldesigner:proteinReference", namespaces = ns)[0].text
            cdprot = tree.xpath("//celldesigner:protein[@id='{0}']".format(prid), namespaces = ns)[0]
            svars = [(mod.get("id"), mod.get("angle"), mod.get("name")) for mod in cdprot.xpath(".//celldesigner:modificationResidue", namespaces = ns)]
            svarssorted = sorted(svars, key = lambda var: var[1])
            i = 1
            for svar in svarssorted:
                sv = StateVariable()
                lval = cdspecies.xpath(".//celldesigner:modification[@residue='{0}']".format(svar[0]), namespaces = ns)
                if lval:
                    sv.val = TranslationDic[lval[0].get("state")]
                else:
                    sv.val = None
                if svar[2]:
                    sv.var = svar[2]
                else:
                    sv.var = UndefinedVar(i)
                    i += 1
                sv.id = entity.id + "_" + svar[0]
                entity.add_sv(sv)
        for cdsubspecies in [cd.getparent().getparent() for cd in tree.xpath(".//celldesigner:complexSpecies[text()='{0}']".format(cdspecies.get("id")), namespaces = ns)]:
            subentity = _make_subentity_from_cd(cdsubspecies, tree, ns)
            entity.add_component(subentity)
        return entity

def _make_subentity_from_cd(cdspecies, tree, ns):
    cd_class = cdspecies.xpath(".//celldesigner:class", namespaces = ns)[0].text
    homodimer = len(cdspecies.xpath(".//celldesigner:homodimer", namespaces = ns)) > 0
    if homodimer:
        cd_class = cd_class + "_HOMODIMER"
    if cd_class != "PHENOTYPE":
        entity = TranslationDic["SUB_" + cd_class]()
        entity.id = cdspecies.get("id")
        if hasattr(entity, "label"):
            entity.label = cdspecies.get("name")
        if cd_class == "GENE":
            ui = UnitOfInformation()
            ui.prefix = "ct"
            ui.label = "gene"
            ui.id = entity.id + "_" + "ui"
            entity.add_ui(ui)
        elif cd_class == "RNA" or cd_class == "ANTISENSE_RNA":
            ui = UnitOfInformation()
            ui.prefix = "mt"
            ui.label = "rna"
            ui.id = entity.id + "_" + "ui"
            entity.add_ui(ui)
        if hasattr(entity, "compartment"):
            cid = cdspecies.get("compartment")
            if cid:
                cdcompartment = _get_cdcompartment_by_id(tree, ns, cid)
                compartment = _make_compartment_from_cd(cdcompartment, ns)
                entity.compartment = compartment
        # making svs
        if cd_class == "PROTEIN":
            prid = cdspecies.xpath(".//celldesigner:proteinReference", namespaces = ns)[0].text
            cdprot = tree.xpath("//celldesigner:protein[@id='{0}']".format(prid), namespaces = ns)[0]
            svars = [(mod.get("id"), mod.get("angle"), mod.get("name")) for mod in cdprot.xpath(".//celldesigner:modificationResidue", namespaces = ns)]
            svarssorted = sorted(svars, key = lambda var: var[1])
            i = 1
            for svar in svarssorted:
                sv = StateVariable()
                lval = cdspecies.xpath(".//celldesigner:modification[@residue='{0}']".format(svar[0]), namespaces = ns)
                if lval:
                    sv.val = TranslationDic[lval[0].get("state")]
                else:
                    sv.val = None
                if svar[2]:
                    sv.var = svar[2]
                else:
                    sv.var = UndefinedVar(i)
                    i += 1
                sv.id = entity.id + "_" + svar[0]
                entity.add_sv(sv)
        for cdsubspecies in [cd.getparent().getparent() for cd in tree.xpath(".//celldesigner:complexSpecies[text()='{0}']".format(cdspecies.get("id")), namespaces = ns)]:
            subentity = _make_entity_from_cd(cdsubspecies, tree, ns)
            entity.add_component(subentity)
        return entity


def _make_process_from_cd(cdproc, tree, ns):
    cd_class = cdproc.xpath(".//celldesigner:reactionType", namespaces = ns)[0].text
    process = TranslationDic[cd_class]()
    process.id = cdproc.get("id")
    if cd_class == "TRANSCRIPTION" or cd_class == "TRANSLATION":
        es = EmptySet()
        process.add_reactant(es)
    else:
        for cdreac in cdproc.xpath("./sbml:listOfReactants", namespaces = ns)[0].xpath("./sbml:speciesReference", namespaces = ns):
            reacid = cdreac.get("species")
            cdreac = _get_cdentity_by_id(tree, ns, reacid)
            reactant = _make_entity_from_cd(cdreac, tree, ns)
            process.add_reactant(reactant)
    for cdprod in cdproc.xpath("./sbml:listOfProducts", namespaces = ns)[0].xpath("./sbml:speciesReference", namespaces = ns):
        prodid = cdprod.get("species")
        cdprod = _get_cdentity_by_id(tree, ns, prodid)
        product = _make_entity_from_cd(cdprod, tree, ns)
        process.add_product(product)
    return process

def _make_lo_from_cd(cdmod, tree, ns):
    lo = TranslationDic[cdmod.get("type").split('_')[-1]]()
    chids = cdmod.get("modifiers").split(',')
    lo.id = '_'.join(chids)
    for chid in chids:
        cdentity = _get_cdentity_by_id(tree, ns, chid)
        entity = _make_entity_from_cd(cdentity, tree, ns)
        lo.add_child(entity)
    return lo

def _make_modulation_from_cd(cdmod, tree, ns):
    mtype = cdmod.get("type")
    if mtype.startswith("BOOLEAN"):
        modulation = TranslationDic[cdmod.get("modificationType")]()
        op = _make_lo_from_cd(cdmod, tree, ns)
        modulation.source = op
    else:
        modulation = TranslationDic[cdmod.get("type")]()
        eid = cdmod.get("modifiers")
        cdentity = _get_cdentity_by_id(tree, ns, eid)
        entity = _make_entity_from_cd(cdentity, tree, ns)
        modulation.source = entity
    cdprocess = cdmod.getparent().getparent().getparent().getparent()
    process = _make_process_from_cd(cdprocess, tree, ns)
    modulation.target = process
    return modulation
