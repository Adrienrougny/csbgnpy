from enum import Enum
import libsbgnpy.libsbgn as libsbgn
from csbgnpy.utils import *
from csbgnpy.af.compartment import *
from csbgnpy.af.activity import *
from csbgnpy.af.modulation import *
from csbgnpy.af.lo import *
from csbgnpy.af.ui import *
from csbgnpy.af.network import *

class ActivityEnum(Enum):
    BIOLOGICAL_ACTIVITY = BiologicalActivity
    PHENOTYPE = Phenotype

class LogicalOperatorEnum(Enum):
    OR = OrOperator
    AND = AndOperator
    NOT = NotOperator

class ModulationEnum(Enum):
    INFLUENCE  = Modulation
    POSITIVE_INFLUENCE  = Stimulation
    NEGATIVE_INFLUENCE  = Inhibition
    UNKNOWN_INFLUENCE  = Modulation
    NECESSARY_STIMULATION  = NecessaryStimulation

def read(*filenames):
    net = Network()
    compartments = set()
    activities = set()
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
            if glyph.get_class().name in [attribute.name for attribute in list(ActivityEnum)]:
                activity = _make_activity_from_glyph(glyph, sbgnmap, compartments)
                activities.add(activity)
        for glyph in sbgnmap.get_glyph(): # making logical operator nodes
            if glyph.get_class().name in [attribute.name for attribute in list(LogicalOperatorEnum)]:
                op  = _make_lo_from_glyph(glyph, sbgnmap, activities, compartments, los)
                los.add(op)
        for arc in sbgnmap.get_arc(): # making modulations
            if arc.get_class().name in [attribute.name for attribute in list(ModulationEnum)]:
                mod = _make_modulation_from_arc(arc, sbgnmap, activities, compartments, los)
                modulations.add(mod)
    net.activities = list(activities)
    net.modulations = list(modulations)
    net.compartments = list(compartments)
    net.los = list(los)
    return net

def _make_activity_ui_from_glyph(glyph):
    ui = UnitOfInformationActivity()
    ui.id = glyph.get_id()
    name = glyph.get_entity().get_name()
    t = UnitOfInformationActivityType(name)
    label = glyph.get_label()
    if label:
        label = label.get_text()
    else:
        label = None
    ui.type = t
    ui.label = label
    return ui

def _make_compartment_from_glyph(glyph):
    comp = csbgnpy.pd.Compartment()
    comp.id = glyph.get_id()
    if glyph.get_label():
        comp.label = glyph.get_label().get_text()
    return comp

def _make_activity_from_glyph(glyph, sbgnmap, compartments):
    activity = ActivityEnum[glyph.get_class().name].value()
    activity.id = glyph.get_id()
    if glyph.get_label():
        activity.label = glyph.get_label().get_text()
    comp_id = glyph.get_compartmentRef()
    if comp_id is not None:
        comp_glyph = get_glyph_by_id_or_port_id(sbgnmap, comp_id)
        comp = _make_compartment_from_glyph(comp_glyph)
        existent_comp = get_object(comp, compartments)
        activity.compartment = existent_comp
    for ui_glyph in glyph.get_glyph():
        ui = _make_activity_ui_from_glyph(ui_glyph)
        activity.add_ui(ui)
    return activity

def _make_lo_from_glyph(glyph, sbgnmap, activities, compartments, los):
    op = LogicalOperatorEnum[glyph.get_class().name].value()
    op.id = glyph.get_id()
    for arc in sbgnmap.get_arc():
        if arc.get_class().name == "LOGIC_ARC" and arc.get_target() in [port.get_id() for port in glyph.get_port()]:
            source_id = arc.get_source()
            source_glyph = get_glyph_by_id_or_port_id(sbgnmap, source_id)
            if source_glyph.get_class().name in [attribute.name for attribute in list(ActivityEnum)]:
                source = _make_activity_from_glyph(source_glyph, sbgnmap, compartments)
                existent_source = get_object(source, activities)
                op.add_child(existent_source)
            elif source_glyph.get_class().name in [attribute.name for attribute in list(LogicalOperatorEnum)]:
                source = _make_lo_from_glyph(source_glyph, sbgnmap, activities, compartments, los)
                existent_source = get_object(source, los)
                if existent_source is not None:
                    op.add_child(existent_source)
                else:
                    op.add_child(source)
    return op

def _make_modulation_from_arc(arc, sbgnmap, activities, compartments, los):
    modulation = ModulationEnum[arc.get_class().name].value()
    source_id = arc.get_source()
    source_glyph = get_glyph_by_id_or_port_id(sbgnmap, source_id)
    if source_glyph.get_class().name in [attribute.name for attribute in list(ActivityEnum)]:
        source = _make_activity_from_glyph(source_glyph, sbgnmap, compartments)
        existent_source = get_object(source, activities)
    elif source_glyph.get_class().name in [attribute.name for attribute in list(LogicalOperatorEnum)]:
        source = _make_lo_from_glyph(source_glyph, sbgnmap, activities, compartments, los)
        existent_source = get_object(source, los)
    modulation.source = existent_source
    target_id = arc.get_target()
    target_glyph = get_glyph_by_id_or_port_id(sbgnmap, target_id)
    target = _make_activity_from_glyph(target_glyph, sbgnmap, compartments)
    existent_target = get_object(target, activities)
    modulation.target = existent_target
    return modulation

def write(net, filename, renew_ids = True, layout = None):
    sbgn = libsbgn.sbgn()
    sbgnmap = libsbgn.map()
    language = libsbgn.Language.AF
    sbgnmap.set_language(language)
    sbgn.set_map(sbgnmap)
    dids = {}
    dports = {}
    if renew_ids:
        _renew_ids(net)
    for comp in net.compartments:
        g = _make_glyph_from_compartment(comp)
        sbgnmap.add_glyph(g)
        dids[comp] = g.get_id()
    for activity in net.activities:
        g = _make_glyph_from_activity(activity, dids, layout)
        sbgnmap.add_glyph(g)
        dids[activity] = g.get_id()
    for op in net.los:
        g = _make_glyph_from_lo(op, layout)
        sbgnmap.add_glyph(g)
        dids[op] = g.get_id()
        arcs = _make_arcs_from_lo(op, dids, layout)
        for arc in arcs:
            sbgnmap.add_arc(arc)
    for modulation in net.modulations:
        arc = _make_arc_from_modulation(modulation, dids, layout)
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

def _make_glyph_from_compartment(comp, layout = None):
    g = libsbgn.glyph()
    g.set_class(libsbgn.GlyphClass.COMPARTMENT)
    g.set_id(comp.id)
    label = libsbgn.label()
    label.set_text(comp.label)
    g.set_label(label)
    if layout:
        bbox = libsbgn.bbox(layout[comp]['x'], layout[comp]['y'], layout[comp]['w'], layout[comp]['h'])
    else:
        bbox = libsbgn.bbox(0, 0, 0, 0)
    g.set_bbox(bbox)
    return g

def _make_glyph_from_activity(activity, dids, layout = None):
    g = libsbgn.glyph()
    g.set_class(libsbgn.GlyphClass[ActivityEnum(activity.__class__).name])
    g.set_id(activity.id)
    label = libsbgn.label()
    label.set_text(activity.label)
    g.set_label(label)
    if activity.compartment is not None:
        g.set_compartmentRef(dids[activity.compartment])
    if hasattr(activity, "uis"):
        for ui in activity.uis:
            gui = _make_glyph_from_unit_of_information_activity(ui, layout)
            g.add_glyph(gui)
    if layout:
        bbox = libsbgn.bbox(layout[activity]['x'], layout[activity]['y'], layout[activity]['w'], layout[activity]['h'])
    else:
        bbox = libsbgn.bbox(0, 0, 0, 0)
    g.set_bbox(bbox)
    return g

def _make_glyph_from_unit_of_information_activity(ui, layout = None):
    gui = libsbgn.glyph()
    gui.set_id(ui.id)
    gui.set_class(libsbgn.GlyphClass["UNIT_OF_INFORMATION"])
    label = libsbgn.label()
    if ui.label:
        label.set_text(ui.label)
    gui.set_label(label)
    entity = libsbgn.entityType()
    entity.set_name(ui.type.value)
    gui.set_entity(entity)
    if layout:
        bbox = libsbgn.bbox(layout[ui]['x'], layout[ui]['y'], layout[ui]['w'], layout[ui]['h'])
    else:
        bbox = libsbgn.bbox(0, 0, 0, 0)
    gui.set_bbox(bbox)
    return gui

def _make_glyph_from_lo(op, layout):
    g = libsbgn.glyph()
    g.set_class(libsbgn.GlyphClass[LogicalOperatorEnum(op.__class__).name])
    g.set_id(op.id)
    top_port = libsbgn.port()
    top_port.set_id("{}.top".format(g.get_id()))
    top_port.set_x(layout[op]['x'] + layout[op]['w'] / 2)
    top_port.set_y(layout[op]['y'])
    g.add_port(top_port)
    bot_port = libsbgn.port()
    bot_port.set_id("{}.bot".format(g.get_id()))
    bot_port.set_x(layout[op]['x'] + layout[op]['w'] / 2)
    bot_port.set_y(layout[op]['y'] - layout[op]['h'])
    g.add_port(bot_port)
    bbox = libsbgn.bbox(layout[op]['x'], layout[op]['y'], layout[op]['w'], layout[op]['h'])
    g.set_bbox(bbox)
    return g

def _make_arc_from_modulation(modulation, dids, layout):
    arc = libsbgn.arc()
    arc.set_id("mod_{0}_{1}".format(dids[modulation.source], dids[modulation.target]))
    arc.set_class(libsbgn.ArcClass[ModulationEnum(modulation.__class__).name])
    if isinstance(modulation.source, Activity):
        arc.set_source(dids[modulation.source])
    else:
        arc.set_source("{}.bot".format(dids[modulation.source]))
    arc.set_target(dids[modulation.target])
    if layout:
        if isinstance(modulation.source, Activity):
            start = libsbgn.startType(layout[modulation]["start"]['x'], layout[modulation]["start"]['y'])
        else:
            start = libsbgn.startType(layout[modulation.source]['x'] + layout[modulation.source]['w'] / 2, layout[modulation.source]['y'] - layout[modulation.source]['h'])
        end = libsbgn.endType(layout[modulation]["end"]['x'], layout[modulation]["end"]['y'])
    else:
        start = libsbgn.startType(0, 0)
        end = libsbgn.endType(0, 0)
    arc.set_start(start)
    arc.set_end(end)
    return arc

def _make_arcs_from_lo(op, dids, layout):
    arcs = set()
    for child in op.children:
        arc = libsbgn.arc()
        arc.set_id("log_{0}_{1}".format(dids[child], dids[op]))
        arc.set_class(libsbgn.ArcClass["LOGIC_ARC"])
        if isinstance(child, Activity):
            arc.set_source(dids[child])
        else:
            arc.set_source("{}.bot".format(dids[child]))
        arc.set_target("{}.top".format(dids[op]))
        if layout:
            if isinstance(child, Activity):
                start = libsbgn.startType(layout[(child, op)]["start"]['x'], layout[(child, op)]["start"]['y'])
            else:
                start = libsbgn.startType(layout[child]['x'] + layout[child]['w'] / 2, layout[child]['y'] - layout[child]['h'])
            end = libsbgn.startType(layout[op]['x'] + layout[op]['w'] / 2, layout[op]['y'])
        else:
            start = libsbgn.startType(0, 0)
            end = libsbgn.endType(0, 0)
        arc.set_start(start)
        arc.set_end(end)
        arcs.add(arc)
    return arcs

def _renew_id_of_activity(activity, i):
        activity.id = "act_{0}".format(i)
        if hasattr(activity, "uis"):
            for l, ui in enumerate(activity.uis):
                _renew_id_of_ui(ui, activity, l)

def _renew_id_of_ui(ui, activity, l):
    ui.id = "{0}_ui_{1}".format(activity.id, l)

def _renew_id_of_compartment(compartment, i):
    compartment.id = "comp_{0}".format(i)

def _renew_id_of_lo(op, i):
    op.id = "op_{0}".format(i)

def _renew_ids(net):
    for i, activity in enumerate(net.activities):
        _renew_id_of_activity(activity, i)
    for i, compartment in enumerate(net.compartments):
        _renew_id_of_compartment(compartment, i)
    for i, op in enumerate(net.los):
        _renew_id_of_lo(op, i)

def make_layout(net):
    import pygraphviz as pg
    class LayoutEnum(Enum):
        ACTIVITY = {'h': 60.0,'w': 108.0}
        LOGICAL_OPERATOR =  {'h': 42, 'w': 42}
        ACTIVITY_UI_OFFSET = {'y': 1 / 2, 'x': 1 / 5}
        ACTIVITY_UI = {'w': 22, 'h': 16}
    scaling = 1 / 72
    layout = {}
    G = pg.AGraph()
    dids = {}
    i = 0
    for act in net.activities:
        dids[act] = i
        G.add_node(i, shape = "box", width = LayoutEnum["ACTIVITY"].value['w'] * scaling, height = LayoutEnum["ACTIVITY"].value['h'] * scaling, fixedsize = True)
        i += 1
    for op in net.los:
        dids[op] = i
        G.add_node(i, shape = "circle", width = LayoutEnum["LOGICAL_OPERATOR"].value['w'] * scaling, height = LayoutEnum["LOGICAL_OPERATOR"].value['w'] * scaling, fixedsize = True)
        i += 1
    for op in net.los:
        for child in op.children:
            G.add_edge(dids[child], dids[op])
    for modulation in net.modulations:
        G.add_edge(dids[modulation.source], dids[modulation.target])
    G.layout(prog = "dot")
    ymax = 0
    for node in G.nodes():
        obj = None
        for key in dids.keys():
            if dids[key] == int(str(node)):
                obj = key
                break
        if isinstance(obj, Activity):
            y = round(float(node.attr["pos"].split(',')[1]) + LayoutEnum["ACTIVITY"].value['h'] / 2)
        else:
            y = round(float(node.attr["pos"].split(',')[1]) + LayoutEnum["LOGICAL_OPERATOR"].value['h'] / 2)
        if y > ymax:
            ymax = y

    for act in net.activities:
        layout[act] = {'y': round(ymax - (float(G.get_node(dids[act]).attr["pos"].split(',')[1]) + LayoutEnum["ACTIVITY"].value['h'] / 2)), \
                'x': round(float(G.get_node(dids[act]).attr["pos"].split(',')[0]) - LayoutEnum["ACTIVITY"].value['w'] / 2), \
                'h': LayoutEnum["ACTIVITY"].value['h'], \
                'w': LayoutEnum["ACTIVITY"].value['w']}
        if hasattr(act, "uis"):
            for ui in act.uis:
                layout[ui] = {'y': round(layout[act]['y'] - LayoutEnum["ACTIVITY_UI_OFFSET"].value['y'] * LayoutEnum["ACTIVITY_UI"].value['h']), \
                        'x': round(layout[act]['x'] - LayoutEnum["ACTIVITY_UI_OFFSET"].value['x'] * LayoutEnum["ACTIVITY_UI"].value['w']), \
                        'h': LayoutEnum["ACTIVITY_UI"].value['h'], \
                        'w': LayoutEnum["ACTIVITY_UI"].value['w']}
    for op in net.los:
        layout[op] = {'y': round(ymax - (float(G.get_node(dids[op]).attr["pos"].split(',')[1]) + LayoutEnum["LOGICAL_OPERATOR"].value['h'] / 2)), \
                'x': round(float(G.get_node(dids[op]).attr["pos"].split(',')[0]) - LayoutEnum["LOGICAL_OPERATOR"].value['w'] / 2), \
                'h': LayoutEnum["LOGICAL_OPERATOR"].value['h'], \
                'w': LayoutEnum["LOGICAL_OPERATOR"].value['w']}
        for child in op.children:
            start = G.get_edge(dids[child], dids[op]).attr["pos"].split(' ')[0].split(',')
            end = G.get_edge(dids[child], dids[op]).attr["pos"].split(' ')[-1].split(',')
            layout[(child, op)] = {"start": {'x': round(float(start[0])), 'y': round(ymax - float(start[1]))}, \
                    "end": {'x': round(float(end[0])), 'y': round(ymax - float(end[1]))}}
    for modulation in net.modulations:
        start = G.get_edge(dids[modulation.source], dids[modulation.target]).attr["pos"].split(' ')[0].split(',')
        end = G.get_edge(dids[modulation.source], dids[modulation.target]).attr["pos"].split(' ')[-1].split(',')
        layout[modulation] = {"start": {'x': round(float(start[0])), 'y': round(ymax - float(start[1]))}, \
                "end": {'x': round(float(end[0])), 'y': round(ymax - float(end[1]))}}
    return layout

