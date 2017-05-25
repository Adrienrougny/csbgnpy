from lxml import etree

from csbgnpy.utils import *
from csbgnpy.pd.compartment import *
from csbgnpy.pd.entity import *
from csbgnpy.pd.process import *
from csbgnpy.pd.modulation import *
from csbgnpy.pd.lo import *
from csbgnpy.pd.sv import *
from csbgnpy.pd.ui import *
from csbgnpy.pd.network import *

ns = {"sbml":"http://www.sbml.org/sbml/level2/version4", "cd":"http://www.sbml.org/2001/ns/celldesigner"}

dic_cd2sbgnml = {
    "PROTEIN": Macromolecule,
    "GENE": Macromolecule,
    "RNA": Macromolecule,
    "ANTISENSE_RNA": Macromolecule,
    "ION": SimpleChemical,
    "SIMPLE_MOLECULE": SimpleChemical,
    "DRUG": UnspecifiedEntity,
    "UNKNOWN": UnspecifiedEntity,
    "COMPLEX": Complex,
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
    "NOT": NotOperator
}

def read_cd(*filenames):
    net = Network()
    compartments = set([])
    entities = set([])
    processes = set([])
    modulations = set([])
    los = set([])
    toskip = 0
    for filename in filenames:
        tree = etree.parse(filename)
        ns = tree.getroot().nsmap
        ns["sbml"] = ns[None]
        ns.pop(None)
        for cdcomp in tree.xpath("//sbml:compartment", namespaces = ns): # making compartment
            comp = _make_compartment_from_cd(cdcomp, ns)
            compartments.add(comp)
        for cdspecies in tree.xpath("//sbml:species", namespaces = ns): #making entities and phenotypes
            cd_class = cdspecies.xpath(".//celldesigner:class", namespaces = ns)[0].text
            if cd_class == "PHENOTYPE":
                process = _make_phenotype_from_cd(cdspecies, tree, ns, compartments)
                processes.add(process)
            else:
                entity = _make_entity_from_cd(cdspecies, tree, ns, compartments)
                entities.add(entity)
        for cdproc in tree.xpath("//sbml:reaction", namespaces = ns): # making additional emtyset
            cd_class = cdproc.xpath(".//celldesigner:reactionType", namespaces = ns)[0].text
            if cd_class == "TRANSCRIPTION" or cd_class == "TRANSLATION":
                es = EmptySet("emptyset")
                entities.add(es)
                break
        for cdproc in tree.xpath("//sbml:reaction", namespaces = ns): #making processes
            process = _make_process_from_cd(cdproc, tree, ns, entities, compartments)
            processes.add(process)
        for cdproc in tree.xpath("//sbml:reaction", namespaces = ns): # making los
            for cdmod in cdproc.xpath(".//celldesigner:modification", namespaces = ns):
                mtype = cdmod.get("type")
                if mtype.startswith("BOOLEAN"):
                    lo = _make_lo_from_cd(cdmod, tree, ns, entities, compartments)
                    los.add(lo)
        for cdproc in tree.xpath("//sbml:reaction", namespaces = ns): # making modulations
            cd_class = cdproc.xpath(".//celldesigner:reactionType", namespaces = ns)[0].text
            if cd_class == "TRANSCRIPTION" or cd_class == "TRANSLATION": # making special modulation in case of translation or transcription
                modulation = NecessaryStimulation()
                sourceid = cdproc.xpath("./sbml:listOfReactants", namespaces = ns)[0].xpath("./sbml:speciesReference", namespaces = ns)[0].get("species")
                cdsource = _get_cdentity_by_id(tree, ns, sourceid)
                source = _make_entity_from_cd(cdsource, tree, ns, compartments)
                existent_source = get_object(source, entities)
                modulation.source = existent_source
                target = _make_process_from_cd(cdproc, tree, ns, entities, compartments)
                existent_target = get_object(target, processes)
                modulation.target = existent_target
                modulations.add(modulation)
            for cdmod in cdproc.xpath(".//celldesigner:modification", namespaces = ns):
                if not toskip: # when boolean, two next modulations should be skipped
                    modulation = _make_modulation_from_cd(cdmod, tree, ns, entities, compartments, los, processes)
                    modulations.add(modulation)
                    mtype = cdmod.get("type")
                    if mtype.startswith("BOOLEAN"):
                        chids = cdmod.get("modifiers").split(',')
                        toskip = len(chids)
                else:
                    toskip -= 1
    net.compartments = compartments
    net.entities = entities
    net.processes = processes
    net.modulations = modulations
    net.los = los
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
    comp.label = cdcomp.get("name")
    return comp

def _make_phenotype_from_cd(cdspecies, tree, ns, compartments):
    process = Phenotype()
    process.id = cdspecies.get("id")
    process.label = cdspecies.get("name")
    return process

def _make_entity_from_cd(cdspecies, tree, ns, compartments):
    cd_class = cdspecies.xpath(".//celldesigner:class", namespaces = ns)[0].text
    if cd_class != "PHENOTYPE":
        entity = dic_cd2sbgnml[cd_class]()
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
                existent_compartment = get_object(compartment, compartments)
                entity.compartment = existent_compartment
        # making svs
        if cd_class == "PROTEIN":
            prid = cdspecies.xpath(".//celldesigner:proteinReference", namespaces = ns)[0].text
            cdprot = tree.xpath("//celldesigner:protein[@id='{0}']".format(prid), namespaces = ns)[0]
            svars = [(mod.get("id"), mod.get("angle")) for mod in cdprot.xpath(".//celldesigner:modificationResidue", namespaces = ns)]
            svarssorted = sorted(svars, key = lambda var: var[1])
            for i, svar in enumerate(svarssorted):
                sv = StateVariable()
                sv.id
                lval = cdspecies.xpath(".//celldesigner:modification[@residue='{0}']".format(svar[0]), namespaces = ns)
                if lval:
                    val = dic_cd2sbgnml[lval[0].get("state")]
                else:
                    val = None
                var = UndefinedVar(i)
                sv.val = val
                sv.var = var
                sv.id = entity.id + "_" + svar[0]
                entity.add_sv(sv)
        for cdsubspecies in [cd.getparent().getparent() for cd in tree.xpath(".//celldesigner:complexSpecies[text()='{0}']".format(cdspecies.get("id")), namespaces = ns)]:
            subentity = _make_entity_from_cd(cdsubspecies, tree, ns, compartments)
            entity.add_component(subentity)
        return entity

def _make_process_from_cd(cdproc, tree, ns, entities, compartments):
    cd_class = cdproc.xpath(".//celldesigner:reactionType", namespaces = ns)[0].text
    process = dic_cd2sbgnml[cd_class]()
    process.id = cdproc.get("id")
    if cd_class == "TRANSCRIPTION" or cd_class == "TRANSLATION":
        found = False
        for entity in entities:
            if isinstance(entity, EmptySet):
                found = True
                break
        if not found:
            raise Exception("EmptySet not found")
        es = entity
        process.add_reactant(es)
    else:
        for cdreac in cdproc.xpath("./sbml:listOfReactants", namespaces = ns)[0].xpath("./sbml:speciesReference", namespaces = ns):
            reacid = cdreac.get("species")
            cdreac = _get_cdentity_by_id(tree, ns, reacid)
            reactant = _make_entity_from_cd(cdreac, tree, ns, compartments)
            existent_reactant = get_object(reactant, entities)
            process.add_reactant(existent_reactant)
    for cdprod in cdproc.xpath("./sbml:listOfProducts", namespaces = ns)[0].xpath("./sbml:speciesReference", namespaces = ns):
        prodid = cdprod.get("species")
        cdprod = _get_cdentity_by_id(tree, ns, prodid)
        product = _make_entity_from_cd(cdprod, tree, ns, compartments)
        existent_product = get_object(product, entities)
        process.add_product(existent_product)
    return process

def _make_lo_from_cd(cdmod, tree, ns, entities, compartments):
    lo = dic_cd2sbgnml[cdmod.get("type").split('_')[-1]]()
    chids = cdmod.get("modifiers").split(',')
    lo.id = '_'.join(chids)
    for chid in chids:
        cdentity = _get_cdentity_by_id(tree, ns, chid)
        entity = _make_entity_from_cd(cdentity, tree, ns, compartments)
        existent_entity = get_object(entity, entities)
        lo.add_child(existent_entity)
    return lo

def _make_modulation_from_cd(cdmod, tree, ns, entities, compartments, los, processes):
    mtype = cdmod.get("type")
    if mtype.startswith("BOOLEAN"):
        modulation = dic_cd2sbgnml[cdmod.get("modificationType")]()
        op = _make_lo_from_cd(cdmod, tree, ns, entities, compartments)
        existent_op = get_object(op, los)
        modulation.source = op
    else:
        modulation = dic_cd2sbgnml[cdmod.get("type")]()
        eid = cdmod.get("modifiers")
        cdentity = _get_cdentity_by_id(tree, ns, eid)
        entity = _make_entity_from_cd(cdentity, tree, ns, compartments)
        existent_entity = get_object(entity, entities)
        modulation.source = existent_entity
    cdprocess = cdmod.getparent().getparent().getparent().getparent()
    process = _make_process_from_cd(cdprocess, tree, ns, entities, compartments)
    existent_process = get_object(process, processes)
    modulation.target = existent_process
    return modulation


