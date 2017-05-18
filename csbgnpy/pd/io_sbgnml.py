from csbgnpy.pd.entity import *

class EntityEnum(Enum):
    UNSPECIFIED_ENTITY = UnspecifiedEntity
    SIMPLE_CHEMICAL = SimpleChemical
    MACROMOLECULE = Macromolecule
    NUCLEIC_ACID_FEATURE = NucleicAcidFeature
    SIMPLE_CHEMICAL_MULTIMER = SimpleChemicalMultimer
    MACROMOLECULE_MULTIMER = MacromoleculeMultimer
    NUCLEIC_ACID_FEATURE_MULTIMER = NucleicAcidFeatureMultimer
    COMPLEX = Complex
    COMPLEX_MULTIMER = ComplexMultimer
    SOURCE_AND_SINK = EmptySet
    PERTURBING_AGENT = PerturbingAgent

def read_sbgnml(*filenames):
    net = csbgnpy.pd.Network()
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
    net.entities = entities
    net.processes = processes
    net.modulations = modulations
    net.compartments = compartments
    net.los = los
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
            sv.var = csbgnpy.utils.Undefined(i)
        else:
            sv.var = glyph.get_state().get_variable()
    else:
        sv.var = csbgnpy.utils.Undefined(i)
    return sv

def _make_compartment_from_glyph(glyph):
    comp = csbgnpy.pd.Compartment()
    comp.id = glyph.get_id()
    comp.label = glyph.get_label().get_text()
    return comp

def _make_entity_from_glyph(glyph, sbgnmap, compartments):
    entity = EntityEnum[glyph.get_class().name].value()
    entity.id = glyph.get_id()
    if g
    if glyph.get_label() is not None:
        entity.label = glyph.get_label().get_text()
    comp_id = glyph.get_compartmentRef()
    if comp_id is not None:
        comp_glyph = get_glyph_by_id(sbgnmap, comp_id)
        comp = _make_compartment_from_glyph(comp_glyph)
        existent_comp = get_object_from_collection(comp, compartments)
        entity.compartment = existent_comp
    for subglyph in glyph.get_glyph():
        if subglyph.get_class().name in [attribute.name for attribute in list(csbgnpy.pd.EntityClazz)]:
            subentity = _make_subentity_from_glyph(subglyph, sbgnmap)
            entity.add_component(subentity)
        elif subglyph.get_class().name == "UNIT_OF_INFORMATION":
            ui = _make_ui_from_glyph(subglyph)
            entity.add_unit_of_information(ui)
    i = 1
    for subglyph in get_ordered_list_of_state_variables(glyph):
        sv = _make_sv_from_glyph(subglyph, i)
        if isinstance(sv.variable, csbgnpy.utils.Undefined):
            i += 1
        entity.add_state_variable(sv)
    return entity

def _make_subentity_from_glyph(glyph, sbgnmap):
    subentity = csbgnpy.pd.Entity()
    subentity.id = glyph.get_id()
    subentity.clazz = csbgnpy.pd.SubEntityClazz["SUB_" + glyph.get_class().name]
    if glyph.get_label() is not None:
        subentity.label = glyph.get_label().get_text()
    for subglyph in glyph.get_glyph():
        if subglyph.get_class().name in [attribute.name for attribute in list(csbgnpy.pd.EntityClazz)]:
            subsubentity = _make_subentity_from_glyph(subglyph, sbgnmap)
            subentity.add_component(subsubentity)
        elif subglyph.get_class().name == "UNIT_OF_INFORMATION":
            ui = _make_ui_from_glyph(subglyph)
            subentity.add_unit_of_information(ui)
    i = 1
    for subglyph in get_ordered_list_of_state_variables(glyph):
        sv = _make_sv_from_glyph(subglyph, i)
        if isinstance(sv.variable, csbgnpy.utils.Undefined):
            i += 1
        subentity.add_state_variable(sv)
    return subentity

def _make_logical_operator_node_from_glyph(glyph, sbgnmap, entities, compartments, logical_operator_nodes):
    op = csbgnpy.pd.LogicalOperatorNode()
    op.clazz = csbgnpy.pd.LogicalOperatorClazz[glyph.get_class().name]
    for arc in sbgnmap.get_arc():
        if arc.get_class().name == "LOGIC_ARC" and arc.get_target() in [port.get_id() for port in glyph.get_port()]:
            source_id = arc.get_source()
            source_glyph = get_glyph_by_id_or_port_id(sbgnmap, source_id)
            if source_glyph.get_class().name in [attribute.name for attribute in list(csbgnpy.pd.EntityClazz)]:
                source = _make_entity_from_glyph(source_glyph, sbgnmap, compartments)
                existent_source = get_object_from_collection(source, entities)
                op.add_child(existent_source)
            elif source_glyph.get_class().name in [attribute.name for attribute in list(csbgnpy.pd.LogicalOperatorClazz)]:
                source = _make_logical_operator_node_from_glyph(source_glyph, sbgnmap, entities, compartments, logical_operator_nodes)
                existent_source = get_object_from_collection(source, logical_operator_nodes)
                if existent_source is not None:
                    op.add_child(existent_source)
                else:
                    op.add_child(source)
    return op

"""Still have to take into account stoech !"""
def _make_process_from_glyph(glyph, sbgnmap, entities, compartments):
    proc = csbgnpy.pd.Process()
    proc.id = glyph.get_id()
    proc.clazz = csbgnpy.pd.ProcessClazz[glyph.get_class().name]
    if glyph.get_label() is not None:
        proc.label = glyph.get_label().get_text()
    for arc in sbgnmap.get_arc():
        if arc.get_class().name == "CONSUMPTION" and get_glyph_by_id_or_port_id(sbgnmap, arc.get_target()) == glyph:
            source_id = arc.get_source()
            source_glyph = get_glyph_by_id_or_port_id(sbgnmap, source_id)
            source = _make_entity_from_glyph(source_glyph, sbgnmap, compartments)
            existent_source = get_object_from_collection(source, entities)
            proc.add_reactant(existent_source)
        elif arc.get_class().name == "PRODUCTION" and get_glyph_by_id_or_port_id(sbgnmap, arc.get_source()) == glyph:
            target_id = arc.get_target()
            target_glyph = get_glyph_by_id_or_port_id(sbgnmap, target_id)
            target = _make_entity_from_glyph(target_glyph, sbgnmap, compartments)
            existent_target = get_object_from_collection(target, entities)
            proc.add_product(existent_target)
    return proc

def _make_modulation_from_arc(arc, sbgnmap, entities, compartments, logical_operator_nodes, processes):
    source_id = arc.get_source()
    source_glyph = get_glyph_by_id_or_port_id(sbgnmap, source_id)
    if source_glyph.get_class().name in [attribute.name for attribute in list(csbgnpy.pd.EntityClazz)]:
        source = _make_entity_from_glyph(source_glyph, sbgnmap, compartments)
        existent_source = get_object_from_collection(source, entities)
    elif source_glyph.get_class().name in [attribute.name for attribute in list(csbgnpy.pd.LogicalOperatorClazz)]:
        source = _make_logical_operator_node_from_glyph(source_glyph, sbgnmap, entities, compartments, logical_operator_nodes)
        existent_source = get_object_from_collection(source, logical_operator_nodes)
    target_id = arc.get_target()
    target_glyph = get_glyph_by_id_or_port_id(sbgnmap, target_id)
    target = _make_process_from_glyph(target_glyph, sbgnmap, entities, compartments)
    existent_target = get_object_from_collection(target, processes)
    clazz = csbgnpy.pd.ModulationClazz[arc.get_class().name]
    modulation = csbgnpy.pd.Modulation(clazz, existent_source, existent_target)
    return modulation

def _make_glyph_from_entity(entity):
    g = libsbgn.glyph()
    if isinstance(entity, csbgnpy.pd.Entity):
        g.set_class(libsbgn.GlyphClass[entity.clazz.name])
        g.set_id(entity.id)
        label = libsbgn.label()
        if entity.has_label():
            label.set_text(entity.label)
        else:
            label.set_text("")
        g.set_label(label)
        for subentity in entity.components:
            gc = _make_glyph_from_subentity(subentity)
            g.add_glyph(gc)
        for i, sv in enumerate(entity.svs):
            gsv = libsbgn.glyph()
            gsv.set_id(entity.id + "_sv_{0}".format(i))
            gsv.set_class(libsbgn.GlyphClass["STATE_VARIABLE"])
            gsv.set_state(libsbgn.stateType(sv.variable, sv.value))
            bbox = libsbgn.bbox(0, 0, 0, 0)
            gsv.set_bbox(bbox)
            g.add_glyph(gsv)
        for i, ui in enumerate(entity.uis):
            gui = libsbgn.glyph()
            gui.set_id(entity.id + "_ui_{0}".format(i))
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
    elif isinstance(entity, csbgnpy.pd.EmptySet):
        g.set_id("emptyset")
        g.set_class(libsbgn.GlyphClass.SOURCE_AND_SINK)
    bbox = libsbgn.bbox(0, 0, 0, 0)
    g.set_bbox(bbox)
    return g

def _make_glyph_from_logical_operator_node(op):
    g = libsbgn.glyph()
    g.set_class(libsbgn.GlyphClass[op.clazz.name])
    g.set_id(op.id)
    bbox = libsbgn.bbox(0, 0, 0, 0)
    g.set_bbox(bbox)
    return g

def _make_glyph_from_subentity(subentity):
    g = libsbgn.glyph()
    g.set_class(libsbgn.GlyphClass[subentity.clazz.name[4:]]) #remove the SUB_ from the class name
    g.set_id(subentity.id)
    bbox = libsbgn.bbox(0, 0, 0, 0)
    g.set_bbox(bbox)
    label = libsbgn.label()
    label.set_text(subentity.label)
    g.set_label(label)
    for subsubentity in subentity.components:
        gc = _make_glyph_from_subentity(subsubentity)
        g.add_glyph(gc)
    for i, sv in enumerate(subentity.svs):
        gsv = libsbgn.glyph()
        gsv.set_id(subentity.id + "_sv_{0}".format(i))
        gsv.set_class(libsbgn.GlyphClass["STATE_VARIABLE"])
        gsv.set_state(libsbgn.stateType(sv.variable, sv.value))
        bbox = libsbgn.bbox(0, 0, 0, 0)
        gsv.set_bbox(bbox)
        g.add_glyph(gsv)
    for i, ui in enumerate(subentity.uis):
        gui = libsbgn.glyph()
        gui.set_id(subentity.id + "_ui_{0}".format(i))
        gui.set_class(libsbgn.GlyphClass["UNIT_OF_INFORMATION"])
        label = libsbgn.label()
        if ui.prefix is not None:
            label.set_text(ui.prefix() + ':' + ui.label)
        else:
            label.set_text(ui.label)
        gui.set_label(label)
        bbox = libsbgn.bbox(0, 0, 0, 0)
        gui.set_bbox(bbox)
        g.add_glyph(gui)
    return g


def _make_glyph_from_process(process):
    p = libsbgn.glyph()
    p.set_class(libsbgn.GlyphClass[process.clazz.name])
    p.set_id(process.id)
    label = libsbgn.label()
    if process.has_label():
        label.set_text(process.label)
    else:
        label.set_text("")
    p.set_label(label)
    bbox = libsbgn.bbox(0, 0, 0, 0)
    p.set_bbox(bbox)
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
    return p

def _make_arcs_from_process(process, dids):
    arcs = []
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
    arc.set_class(libsbgn.ArcClass[modulation.clazz.name])
    return arc

def _make_arcs_from_logical_operator_node(op, dids):
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

def _renew_ids(net):
    for i, entity in enumerate(net.entities):
        if isinstance(entity, csbgnpy.pd.Entity):
            entity.id = "epn_{0}".format(i)
            for j, subentity in enumerate(entity.components): # should be made recursive
                subentity.id = "{0}_sub_{1}".format(entity.id, j)
            for k, sv in enumerate(entity.svs):
                sv.id = "{0}_sv_{1}".format(entity.id, k)
            for l, ui in enumerate(entity.uis):
                ui.id = "{0}_sv_{1}".format(entity.id, l)
    for i, compartment in enumerate(net.compartments):
        compartment.id = "comp_{0}".format(i)
    for i, process in enumerate(net.processes):
        process.id = "proc_{0}".format(i)
    for i, op in enumerate(net.logical_operator_nodes):
        op.id = "op_{0}".format(i)

def write_sbgnml(net, filename, renew_ids = True):
    sbgn = libsbgn.sbgn()
    sbgnmap = libsbgn.map()
    language = libsbgn.Language.PD
    sbgnmap.set_language(language)
    sbgn.set_map(sbgnmap);
    dids = {}
    if renew_ids:
        _renew_ids(net)
    for entity in net.entities:
        g = _make_glyph_from_entity(entity)
        sbgnmap.add_glyph(g)
        dids[entity] = g.get_id()
    for op in net.logical_operator_nodes:
        g = _make_glyph_from_logical_operator_node(op)
        sbgnmap.add_glyph(g)
        dids[op] = g.get_id()
        arcs = _make_arcs_from_logical_operator_node(op, dids)
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


