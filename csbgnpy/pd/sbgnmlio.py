from enum import Enum
from math import atan2
from math import pi
import libsbgnpy.libsbgn as libsbgn
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

def atan2pi(y, x):
    a = atan2(y, x)
    if a < 0:
        a = a + 2 * pi
    return a

def read(*filenames):
    net = Network()
    compartments = set()
    entities = set()
    processes = set()
    modulations = set()
    los = set()
    for filename in filenames:
        sbgn = libsbgn.parse(filename, silence=True)
        sbgnmap = sbgn.get_map()
        for glyph in sbgnmap.get_glyph(): # making compartments
            if glyph.get_class().name == "COMPARTMENT":
                comp = _make_compartment_from_glyph(glyph)
                compartments.add(comp)
        for glyph in sbgnmap.get_glyph(): # making entities
            if glyph.get_class().name in [attribute.name for attribute in list(EntityEnum)]:
                entity = _make_entity_from_glyph(glyph, sbgnmap, compartments)
                entities.add(entity)
        for glyph in sbgnmap.get_glyph(): # making processes
            if glyph.get_class().name in [attribute.name for attribute in list(ProcessEnum)]:
                proc = _make_process_from_glyph(glyph, sbgnmap, entities, compartments)
                processes.add(proc)
        for glyph in sbgnmap.get_glyph(): # making logical operator nodes
            if glyph.get_class().name in [attribute.name for attribute in list(LogicalOperatorEnum)]:
                op  = _make_lo_from_glyph(glyph, sbgnmap, entities, compartments, los)
                los.add(op)
        for arc in sbgnmap.get_arc(): # making modulations
            if arc.get_class().name in [attribute.name for attribute in list(ModulationEnum)]:
                mod = _make_modulation_from_arc(arc, sbgnmap, entities, compartments, los, processes)
                modulations.add(mod)
    net.entities = list(entities)
    net.processes = list(processes)
    net.modulations = list(modulations)
    net.compartments = list(compartments)
    net.los = list(los)
    return net

def _make_ui_from_glyph(glyph):
    ui = UnitOfInformation()
    ui.id = glyph.get_id()
    if glyph.get_label() is not None:
        glabel = glyph.get_label().get_text()
        if ':' in glabel:
            ui.prefix = glabel.split(':')[0]
            ui.label = glabel.split(':')[1]
        else:
            ui.label = glabel
    return ui

def _make_sv_from_glyph(glyph, i):
    sv = StateVariable()
    sv.id = glyph.get_id()
    if glyph.get_state() is not None:
        sv.val = glyph.get_state().get_value()
        if glyph.get_state().get_variable() is None:
            sv.var = UndefinedVar(i)
        else:
            sv.var = glyph.get_state().get_variable()
    else:
        sv.var = UndefinedVar(i)
    return sv

def _make_compartment_from_glyph(glyph):
    comp = csbgnpy.pd.Compartment()
    comp.id = glyph.get_id()
    if glyph.get_label() is not None:
        comp.label = glyph.get_label().get_text()
    return comp

def _make_entity_from_glyph(glyph, sbgnmap, compartments):
    entity = EntityEnum[glyph.get_class().name].value()
    entity.id = glyph.get_id()
    lsvs = []
    if glyph.get_label() is not None:
        entity.label = glyph.get_label().get_text()
    comp_id = glyph.get_compartmentRef()
    if comp_id is not None:
        comp_glyph = get_glyph_by_id_or_port_id(sbgnmap, comp_id)
        comp = _make_compartment_from_glyph(comp_glyph)
        existent_comp = get_object(comp, compartments)
        entity.compartment = existent_comp
    for subglyph in glyph.get_glyph():
        if subglyph.get_class().name in [attribute.name for attribute in list(EntityEnum)]:
            subentity = _make_entity_from_glyph(subglyph, sbgnmap, compartments)
            entity.add_component(subentity)
        elif subglyph.get_class().name == "UNIT_OF_INFORMATION":
            ui = _make_ui_from_glyph(subglyph)
            entity.add_ui(ui)
        elif subglyph.get_class().name == "STATE_VARIABLE":
            lsvs.append(subglyph)
    if lsvs:
        i = 1
        center = (glyph.bbox.x + glyph.bbox.w / 2, glyph.bbox.y + glyph.bbox.h / 2)
        lsorted = sorted(lsvs, key = lambda g: atan2pi(-(g.bbox.y + g.bbox.h / 2 - center[1]), g.bbox.x + g.bbox.w / 2 - center[0]))
        # lsorted = sorted(lsvs, key = lambda g: atan2(g.bbox.y - center[1], g.bbox.x - center[0]))
        for subglyph in lsorted:
            sv = _make_sv_from_glyph(subglyph, i)
            if isinstance(sv.var, UndefinedVar):
                i += 1
            entity.add_sv(sv)
    return entity

def _make_lo_from_glyph(glyph, sbgnmap, entities, compartments, los):
    op = LogicalOperatorEnum[glyph.get_class().name].value()
    op.id = glyph.get_id()
    for arc in sbgnmap.get_arc():
        if arc.get_class().name == "LOGIC_ARC" and arc.get_target() in [port.get_id() for port in glyph.get_port()]:
            source_id = arc.get_source()
            source_glyph = get_glyph_by_id_or_port_id(sbgnmap, source_id)
            if source_glyph.get_class().name in [attribute.name for attribute in list(EntityEnum)]:
                source = _make_entity_from_glyph(source_glyph, sbgnmap, compartments)
                existent_source = get_object(source, entities)
                op.add_child(existent_source)
            elif source_glyph.get_class().name in [attribute.name for attribute in list(LogicalOperatorEnum)]:
                source = _make_lo_from_glyph(source_glyph, sbgnmap, entities, compartments, los)
                existent_source = get_object(source, los)
                if existent_source is not None:
                    op.add_child(existent_source)
                else:
                    op.add_child(source)
    return op

"""Still have to take into account stoech !"""
def _make_process_from_glyph(glyph, sbgnmap, entities, compartments):
    proc = ProcessEnum[glyph.get_class().name].value()
    proc.id = glyph.get_id()
    if glyph.get_label() is not None:
        proc.label = glyph.get_label().get_text()
    for arc in sbgnmap.get_arc():
        if arc.get_class().name == "CONSUMPTION" and get_glyph_by_id_or_port_id(sbgnmap, arc.get_target()) == glyph:
            source_id = arc.get_source()
            source_glyph = get_glyph_by_id_or_port_id(sbgnmap, source_id)
            source = _make_entity_from_glyph(source_glyph, sbgnmap, compartments)
            existent_source = get_object(source, entities)
            proc.add_reactant(existent_source)
        elif arc.get_class().name == "PRODUCTION" and get_glyph_by_id_or_port_id(sbgnmap, arc.get_source()) == glyph:
            target_id = arc.get_target()
            target_glyph = get_glyph_by_id_or_port_id(sbgnmap, target_id)
            target = _make_entity_from_glyph(target_glyph, sbgnmap, compartments)
            existent_target = get_object(target, entities)
            proc.add_product(existent_target)
    return proc

def _make_modulation_from_arc(arc, sbgnmap, entities, compartments, los, processes):
    modulation = ModulationEnum[arc.get_class().name].value()
    source_id = arc.get_source()
    source_glyph = get_glyph_by_id_or_port_id(sbgnmap, source_id)
    if source_glyph.get_class().name in [attribute.name for attribute in list(EntityEnum)]:
        source = _make_entity_from_glyph(source_glyph, sbgnmap, compartments)
        existent_source = get_object(source, entities)
    elif source_glyph.get_class().name in [attribute.name for attribute in list(LogicalOperatorEnum)]:
        source = _make_lo_from_glyph(source_glyph, sbgnmap, entities, compartments, los)
        existent_source = get_object(source, los)
    modulation.source = existent_source
    target_id = arc.get_target()
    target_glyph = get_glyph_by_id_or_port_id(sbgnmap, target_id)
    target = _make_process_from_glyph(target_glyph, sbgnmap, entities, compartments)
    existent_target = get_object(target, processes)
    modulation.target = existent_target
    return modulation

def _make_glyph_from_compartment(comp):
    g = libsbgn.glyph()
    g.set_class(libsbgn.GlyphClass.COMPARTMENT)
    g.set_id(comp.id)
    label = libsbgn.label()
    label.set_text(comp.label)
    g.set_label(label)
    bbox = libsbgn.bbox(0, 0, 0, 0)
    g.set_bbox(bbox)
    return g

def _make_glyph_from_entity(entity, dids):
    g = libsbgn.glyph()
    g.set_class(libsbgn.GlyphClass[EntityEnum(entity.__class__).name])
    g.set_id(entity.id)
    if hasattr(entity, "label"):
        label = libsbgn.label()
        label.set_text(entity.label)
    # else:
        # label.set_text("")
        g.set_label(label)
    if hasattr(entity, "compartment"):
        if entity.compartment is not None:
            g.set_compartmentRef(dids[entity.compartment])
    if hasattr(entity, "components"):
        for subentity in entity.components:
            gc = _make_glyph_from_entity(subentity, dids)
            g.add_glyph(gc)
    if hasattr(entity, "svs"):
        defsvs = [sv for sv in entity.svs if not isinstance(sv.var, UndefinedVar)]
        undefsvs = sorted([sv for sv in entity.svs if isinstance(sv.var, UndefinedVar)], key = lambda sv: sv.var.num)
        svs = defsvs + undefsvs
        for sv in svs:
            gsv = libsbgn.glyph()
            gsv.set_id(sv.id)
            gsv.set_class(libsbgn.GlyphClass["STATE_VARIABLE"])
            if isinstance(sv.var, UndefinedVar):
                var = None
                bbox = libsbgn.bbox((len(undefsvs) - sv.var.num) * 0.01, 0, 0, 0)
            else:
                var = sv.var
                bbox = libsbgn.bbox(0, 0, 0, 0)
            gsv.set_state(libsbgn.stateType(sv.val, var))
            gsv.set_bbox(bbox)
            g.add_glyph(gsv)
    if hasattr(entity, "uis"):
        for ui in entity.uis:
            gui = libsbgn.glyph()
            gui.set_id(ui.id)
            gui.set_class(libsbgn.GlyphClass["UNIT_OF_INFORMATION"])
            label = libsbgn.label()
            if ui.prefix is not None:
                label.set_text(ui.prefix + ':' + ui.label)
            else:
                label.set_text(ui.label)
            gui.set_label(label)
            bbox = libsbgn.bbox(0, 0, 0, 0)
            gui.set_bbox(bbox)
            g.add_glyph(gui)
    bbox = libsbgn.bbox(0, 0, 0, 0)
    g.set_bbox(bbox)
    return g

def _make_glyph_from_lo(op):
    g = libsbgn.glyph()
    g.set_class(libsbgn.GlyphClass[LogicalOperatorEnum(op.__class__).name])
    g.set_id(op.id)
    bbox = libsbgn.bbox(0, 0, 0, 0)
    g.set_bbox(bbox)
    return g

def _make_glyph_from_process(process):
    g = libsbgn.glyph()
    g.set_class(libsbgn.GlyphClass[ProcessEnum(process.__class__).name])
    g.set_id(process.id)
    label = libsbgn.label()
    if hasattr(process, "label"):
        label.set_text(process.label)
    else:
        label.set_text("")
    g.set_label(label)
    bbox = libsbgn.bbox(0, 0, 0, 0)
    g.set_bbox(bbox)
    # port1 = libsbgn.port()
    # port1.set_id("{0}.1".format(p.get_id()))
    # port1.set_y(bbox.get_y() + bbox.get_h() / 2)
    # port1.set_x(bbox.get_x())
    # port2 = libsbgn.port()
    # port2.set_id("{0}.2".format(p.get_id()))
    # port2.set_y(bbox.get_y() + bbox.get_h() / 2)
    # port2.set_x(bbox.get_x() + bbox.get_w())
    # p.add_port(port1)
    # p.add_port(port2)
    return g

def _make_arcs_from_process(process, dids):
    arcs = []
    if hasattr(process, "reactants"):
        for reactant in process.reactants:
            arc = libsbgn.arc()
            start = libsbgn.startType(0, 0)
            end = libsbgn.endType(0, 0)
            arc.set_source(dids[reactant])
            # arc.set_target("{0}.1".format(process.getId()))
            arc.set_target(dids[process])
            arc.set_id("cons_{0}_{1}".format(dids[reactant], dids[process]))
            arc.set_start(start)
            arc.set_end(end)
            arc.set_class(libsbgn.ArcClass.CONSUMPTION)
            arcs.append(arc)
    if hasattr(process, "products"):
        for product in process.products:
            arc = libsbgn.arc()
            start = libsbgn.startType(0, 0)
            end = libsbgn.endType(0, 0)
            # arc.set_source("{0}.2".format(process.getId()))
            arc.set_source(dids[process])
            arc.set_target(dids[product])
            arc.set_id("prod_{0}_{1}".format(dids[process], dids[product]))
            arc.set_start(start)
            arc.set_end(end)
            arc.set_class(libsbgn.ArcClass.PRODUCTION)
            arcs.append(arc)
    return arcs

def _make_arc_from_modulation(modulation, dids):
    arc = libsbgn.arc()
    start = libsbgn.startType(0, 0)
    end = libsbgn.endType(0, 0)
    arc.set_source(dids[modulation.source])
    arc.set_target(dids[modulation.target])
    arc.set_id("mod_{0}_{1}".format(dids[modulation.source], dids[modulation.target]))
    arc.set_start(start)
    arc.set_end(end)
    arc.set_class(libsbgn.ArcClass[ModulationEnum(modulation.__class__).name])
    return arc

def _make_arcs_from_lo(op, dids):
    arcs = set()
    for child in op.children:
        arc = libsbgn.arc()
        start = libsbgn.startType(0, 0)
        end = libsbgn.endType(0, 0)
        arc.set_source(dids[child])
        arc.set_target(dids[op])
        arc.set_id("log_{0}_{1}".format(dids[child], dids[op]))
        arc.set_start(start)
        arc.set_end(end)
        arc.set_class(libsbgn.ArcClass["LOGIC_ARC"])
        arcs.add(arc)
    return arcs

def _renew_id_of_entity(entity, i):
        entity.id = "epn_{0}".format(i)
        if hasattr(entity, "conmponents"):
            for j, subentity in enumerate(entity.components): # should be made recursive
                _renew_id_of_subentity(subentity, entity, j)
        if hasattr(entity, "svs"):
            for k, sv in enumerate(entity.svs):
                _renew_id_of_sv(sv, entity, k)
        if hasattr(entity, "uis"):
            for l, ui in enumerate(entity.uis):
                _renew_id_of_ui(ui, entity, l)

def _renew_id_of_subentity(subentity, entity, j):
    subentity.id = "{0}_sub_{1}".format(entity.id, j)
    for h, subsubentity in enumerate(subentity.components): # should be made recursive
        _renew_id_of_subentity(subsubentity, entity, h)
    for k, sv in enumerate(entity.svs):
        _renew_id_of_sv(sv, entity, k)
    for l, ui in enumerate(entity.uis):
        _renew_id_of_ui(ui, entity, l)

def _renew_id_of_sv(sv, entity, k):
    sv.id = "{0}_sv_{1}".format(entity.id, k)

def _renew_id_of_ui(ui, entity, l):
    ui.id = "{0}_ui_{1}".format(entity.id, l)


def _renew_id_of_compartment(compartment, i):
    compartment.id = "comp_{0}".format(i)

def _renew_id_of_process(process, i):
    process.id = "proc_{0}".format(i)

def _renew_id_of_lo(op, i):
    op.id = "op_{0}".format(i)

def _renew_ids(net):
    for i, entity in enumerate(net.entities):
        _renew_id_of_entity(entity, i)
    for i, compartment in enumerate(net.compartments):
        _renew_id_of_compartment(compartment, i)
    for i, process in enumerate(net.processes):
        _renew_id_of_process(process, i)
    for i, op in enumerate(net.los):
        _renew_id_of_lo(op, i)

def write(net, filename, renew_ids = True):
    sbgn = libsbgn.sbgn()
    sbgnmap = libsbgn.map()
    language = libsbgn.Language.PD
    sbgnmap.set_language(language)
    sbgn.set_map(sbgnmap)
    dids = {}
    if renew_ids:
        _renew_ids(net)
    for comp in net.compartments:
        g = _make_glyph_from_compartment(comp)
        sbgnmap.add_glyph(g)
        dids[comp] = g.get_id()
    for entity in net.entities:
        g = _make_glyph_from_entity(entity, dids)
        sbgnmap.add_glyph(g)
        dids[entity] = g.get_id()
    for op in net.los:
        g = _make_glyph_from_lo(op)
        sbgnmap.add_glyph(g)
        dids[op] = g.get_id()
        arcs = _make_arcs_from_lo(op, dids)
        for arc in arcs:
            sbgnmap.add_arc(arc)
    for process in net.processes:
        p = _make_glyph_from_process(process)
        sbgnmap.add_glyph(p)
        dids[process] = p.get_id()
        arcs = _make_arcs_from_process(process, dids)
        for arc in arcs:
            sbgnmap.add_arc(arc)
    for modulation in net.modulations:
        arc = _make_arc_from_modulation(modulation, dids)
        sbgnmap.add_arc(arc)
    sbgn.write_file(filename)
    ifile = open(filename)
    s = ifile.read()
    ifile.close()
    s = s.replace("sbgn:","")
    s = s.replace(' xmlns:sbgn="http://sbgn.org/libsbgn/0.2"', "")
    s = s.replace('."', '.0"')
    ofile = open(filename, "w")
    ofile.write(s)
    ofile.close()


