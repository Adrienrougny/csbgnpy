from enum import Enum
import libsbgnpy.libsbgn as libsbgn
from csbgnpy.utils import *
from csbgnpy.af.compartment import *
from csbgnpy.af.activity import *
from csbgnpy.af.modulation import *
from csbgnpy.af.lo import *
from csbgnpy.af.ui import *
from csbgnpy.af.network import Network
from csbgnpy.af.io.utils import *
from csbgnpy.af.io.utils import _obj_from_coll

def read(*filenames):
    """Builds a map from SBGN-ML files

    :param filenames: names of files to be read
    :return: a map that is the union of the maps described in the input files
    """
    net = Network()
    compartments = set([])
    activities = set([])
    los = []
    modulations = set([])
    for filename in filenames:
        dids = {}
        sbgn = libsbgn.parse(filename, silence=True)
        sbgnmap = sbgn.get_map()
        for glyph in sbgnmap.get_glyph(): # making compartments
            if glyph.get_class().name == "COMPARTMENT":
                comp = _make_compartment_from_glyph(glyph) if comp not in compartments:
                    compartments.add(comp)
                    dids[comp.id] = comp
                else:
                    dids[comp.id] = _obj_from_coll(comp, compartments)
        for glyph in sbgnmap.get_glyph():
            if glyph.get_class().name in [attribute.name for attribute in list(ActivityEnum)]:
                activity = _make_activity_from_glyph(glyph, dids)
                if activity not in activities:
                    activities.add(activity)
                    dids[activity.id] = activity
                else:
                    dids[activity.id] = _obj_from_coll(activity, activities)
                for port in glyph.get_port():
                    dids[port.id] = activity
            elif glyph.get_class().name in [attribute.name for attribute in list(LogicalOperatorEnum)]:
                op  = _make_lo_node_from_glyph(glyph)
                los.append(op)
                dids[op.id] = op
                for port in glyph.get_port():
                    dids[port.id] = op
        for arc in sbgnmap.get_arc(): # making modulations
            elif arc.get_class().name == "LOGIC_ARC":
                _make_lo_child_from_arc(arc, dids)
            elif arc.get_class().name in [attribute.name for attribute in list(ModulationEnum)]:
                mod = _make_modulation_from_arc(arc, dids)
                modulations.add(mod)
    los = set(los)
    for op in los:
        for i, child in enumerate(op.children):
            if isinstance(child, LogicalOperator):
                op.children[i] = _obj_from_coll(child, los)
    for mod in modulations:
        if isinstance(mod.source, LogicalOperator):
            mod.source = _obj_from_coll(mod.source, los)
        mod.target = _obj_from_coll(mod.target, processes)
    net.activities = list(activities)
    net.compartments = list(compartments)
    net.los = list(los)
    net.modulations = list(modulations)
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

def _make_compartment_ui_from_glyph(glyph):
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

def _make_compartment_from_glyph(glyph):
    comp = Compartment()
    comp.id = glyph.get_id()
    if glyph.get_label():
        if glyph.get_label().get_text():
            comp.label = glyph.get_label().get_text()
    return comp

def _make_activity_from_glyph(glyph, dids):
    activity = ActivityEnum[glyph.get_class().name].value()
    activity.id = glyph.get_id()
    if glyph.get_label():
        if glyph.get_label().get_text():
            activity.label = glyph.get_label().get_text()
    comp_id = glyph.get_compartmentRef()
    if comp_id is not None:
        activity.compartment = dids[comp_id]
    for subglyph in glyph.get_glyph():
        if subglyph.get_class().name == "UNIT_OF_INFORMATION":
            ui = _make_activity_ui_from_glyph(subglyph)
            activity.add_ui(ui)
    return activity

def _make_lo_node_from_glyph(glyph):
    op = LogicalOperatorEnum[glyph.get_class().name].value()
    op.id = glyph.get_id()
    return op

def _make_lo_child_from_arc(arc, dids):
    source_id = arc.get_source()
    target_id = arc.get_target()
    dids[target_id].add_child(dids[source_id])

def _make_modulation_from_arc(arc, dids):
    modulation = ModulationEnum[arc.get_class().name].value()
    source_id = arc.get_source()
    target_id = arc.get_target()
    modulation.source = dids[source_id]
    modulation.target = dids[target_id]
    return modulation

def write(net, filename, renew_ids = False, layout = None):
    """Writes a map to an SBGN-ML file

    :param filename: the SBGN-ML file to be created
    :param renew_ids: if True, renews the ids of the glyphs
    """
    sbgn = libsbgn.sbgn()
    sbgnmap = libsbgn.map()
    language = libsbgn.Language.PD
    sbgnmap.set_language(language)
    sbgn.set_map(sbgnmap)
    dids = {}
    if renew_ids:
        _renew_ids(net)
    for comp in net.compartments:
        g = _make_glyphs_from_compartment(comp, dids, layout)
        sbgnmap.add_glyph(g)
    for activity in net.activities:
        g = _make_glyphs_from_activity(activity, dids, layout)
        sbgnmap.add_glyph(g)
    for op in net.los:
        g = _make_glyphs_from_lo(op, dids, layout)
        sbgnmap.add_glyph(g)
        arcs = _make_arcs_from_lo(op, dids, layout)
        for arc in arcs:
            sbgnmap.add_arc(arc)
    for modulation in net.modulations:
        arc = _make_arcs_from_modulation(modulation, dids, layout)
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

def _make_glyphs_from_compartment(comp, dids, layout):
    gs = []
    if comp in layout:
        ls = layout[comp]
    else:
        ls = [NodeLayout()]
    for l, i in enumerate(ls):
        g = libsbgn.glyph()
        g.set_class(libsbgn.GlyphClass.COMPARTMENT)
        label = libsbgn.label()
        label.set_text(comp.label)
        g.set_label(label)
        # setting the layout
        bbox = libsbgn.bbox(l.x, l.y, l.w, l.h)
        for pl in l:
            gport = libsbgn.port()
            gport.set_id(pl.id)
            gport.set_x(pl.x)
            gport.set_y(pl.y)
            g.add_port(gport)
        g.set_bbox(bbox)
        if l.id:
            g.set_id(l.id)
        else:
            if comp.id:
                if len(ls) > 1:
                    id = "{}.{}".format(comp.id, i)
                else:
                    id = comp.id
            else:
                if len(ls) > 1:
                    id = "{}.{}".format(str(comp), i)
                else:
                    id = str(comp)
        g.set_id(id)
        gs.append(g)
        dids[comp].append(id)
    return gs

def _make_glyphs_from_activity(activity, dids, layout):
    gs = []
    if activity in layout:
        ls = layouy[activity]
    else:
        ls = [NodeLayout]
    for l in ls:
        g = libsbgn.glyph()
        g.set_class(libsbgn.GlyphClass[ActivityEnum(activity.__class__).name])
        if hasattr(activity, "label"):
            label = libsbgn.label()
            label.set_text(activity.label)
            g.set_label(label)
        if hasattr(activity, "compartment"):
            if acitivity.compartment is not None:
                g.set_compartmentRef(dids[activity.compartment][0]) # first compartment is always assigned
        if hasattr(activity, "uis"):
            for ui in activity.uis:
                gui = libsbgn.glyph()
                gui.set_class(libsbgn.GlyphClass["UNIT_OF_INFORMATION"])
                label = libsbgn.label()
                if ui.label:
                    label.set_text(ui.label)
                gui.set_label(label)
                entity = libsbgn.entityType()
                entity.set_name(ui.type.value)
                gui.set_entity(entity)
                # setting the layout
                if layout and ui in layout:
                    l = layout[ui]
                else:
                    l = NodeLayout()
                bbox = libsbgn.bbox(l.x, l.y, l.w, l.h)
                for pl in l:
                    gport = libsbgn.port()
                    gport.set_id(pl.id)
                    gport.set_x(pl.x)
                    gport.set_y(pl.y)
                    gui.add_port(gport)
                gui.set_bbox(bbox)
                if l.id:
                    gui.set_id(l.id)
                else:
                    if ui.id:
                        gui.set_id(ui.id)
                    else:
                        gui.set_id(str(ui))
                g.add_glyph(gui)
        # setting the layout
        if layout and activity in layout:
            l = layout[activity]
        else:
            l = NodeLayout()
        bbox = libsbgn.bbox(l.x, l.y, l.w, l.h)
        for pl in l:
            gport = libsbgn.port()
            gport.set_id(pl.id)
            gport.set_x(pl.x)
            gport.set_y(pl.y)
            g.add_port(gport)
        g.set_bbox(bbox)
        if l.id:
            g.set_id(l.id)
        else:
            if activity.id:
                g.set_id(activity.id)
            else:
                g.set_id(str(activity))
    return g

def _make_glyph_from_lo(op, layout):
    g = libsbgn.glyph()
    g.set_class(libsbgn.GlyphClass[LogicalOperatorEnum(op.__class__).name])
    g.set_id(op.id)
    # setting the layout
    if layout and op in layout:
        l = layout[op]
    else:
        l = NodeLayout()
    bbox = libsbgn.bbox(l.x, l.y, l.w, l.h)
    for port in l:
        if port in layout:
            pl = layout[port]
        else:
            pl = PortLayout()
        gport = libsbgn.port()
        gport.set_id(port.id)
        gport.set_x(pl.x)
        gport.set_y(pl.y)
        g.add_port(gport)
    g.set_bbox(bbox)
    return g

def _make_arc_from_modulation(modulation, dids, layout):
    arc = libsbgn.arc()
    source = arc.source
    target = arc.target
    # source and targets may be ports
    if layout and (source, target) in layout:
        l = layout[(source, target)]
    else:
        l = ArcLayout()
    if l.source:
        arc.set_source(l.source.id)
    else:
        arc.set_source(dids[source])
    if l.target:
        arc.set_target(l.target.id)
    else:
        arc.set_target(dids[modulation.target])
    start = libsbgn.startType(l[0][0], l[0][1]) # TODO: add intermediary points
    end = libsbgn.endType(l[-1][0], l[-1][1])
    arc.set_start(start)
    arc.set_end(end)
    arc.set_class(libsbgn.ArcClass[ModulationEnum(modulation.__class__).name])
    return arc

def _make_arcs_from_lo(op, dids):
    arcs = set()
    for child in op.children:
        arc = libsbgn.arc()
        arc.set_source(dids[child])
        arc.set_target(dids[op])
        arc.set_id("log_{0}_{1}".format(dids[child], dids[op]))
        start = libsbgn.startType(0, 0)
        end = libsbgn.endType(0, 0)
        arc.set_start(start)
        arc.set_end(end)
        arc.set_class(libsbgn.ArcClass["LOGIC_ARC"])
        arcs.add(arc)
    return arcs

def _renew_ids(net):
    for i, activity in enumerate(sorted(net.activities)):
        _renew_id_of_activity(acitivity, i)
    for i, compartment in enumerate(sorted(net.compartments)):
        _renew_id_of_compartment(compartment, i)
    for i, op in enumerate(sorted(net.los)):
        _renew_id_of_lo(op, i)

def _renew_unknown_ids(net):
    for i, activity in enumerate(sorted(net.activities)):
        if not activity.id:
            _renew_id_of_activity(activity, i)
    for i, compartment in enumerate(sorted(net.compartments)):
        if not compartment.id:
            _renew_id_of_compartment(compartment, i)
    for i, op in enumerate(sorted(net.los)):
        if not op.id:
            _renew_id_of_lo(op, i)
def _renew_id_of_activity(activity, i):
        activity.id = "act_{0}".format(i)
        if hasattr(activity, "uis"):
            for l, ui in enumerate(sorted(activity.uis)):
                _renew_id_of_ui(ui, activity, l)

def _renew_id_of_ui(ui, activity, l):
    ui.id = "{0}_ui_{1}".format(activity.id, l)

def _renew_id_of_compartment(compartment, i):
    compartment.id = "comp_{0}".format(i)

def _renew_id_of_lo(op, i):
    op.id = "op_{0}".format(i)
