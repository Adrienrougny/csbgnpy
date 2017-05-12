from math import atan2

import libsbgnpy.libsbgn as libsbgn
import csbgnpy.pd

def get_ordered_list_of_state_variables(glyph):
    l = []
    for subglyph in glyph.get_glyph():
        if subglyph.get_class().name == "STATE_VARIABLE":
            l.append(subglyph)
    if len(l) == 0:
        return l
    lx = [g.bbox.x for g in l]
    ly = [g.bbox.y for g in l]
    center = tuple([csbgnpy.utils.mean(lx), csbgnpy.utils.mean(ly)])
    lsorted = sorted(l, key = lambda g: atan2(center[1] - g.bbox.y, center[0] - g.bbox.x))
    # leftcorner = tuple(glyph.bbox.x, glyph.bbox.y)
    # leftcorner_angle = atan2(center[1] - leftcorner[1], center[0] - leftcorner[0])
    # angles = [atan2(center[1] - g.bbox.y, center[0] - g.bbox.x) for g in l]
    return lsorted

def get_object_from_collection(obj, coll):
    for obj2 in coll:
        if obj2 == obj:
            return obj2
    return None

def get_glyph_by_id_or_port_id(sbgnmap, i):
    for glyph in sbgnmap.get_glyph():
        if glyph.get_id() == i:
            return glyph
        for port in glyph.get_port():
            if port.get_id() == i:
                return glyph
    return None

def get_glyph_by_id(sbgnmap, id):
    for glyph in sbgnmap.get_glyph():
        if glyph.get_id() == id:
            return glyph
    return None

def read_SBGNML(*filenames):
    net = csbgnpy.pd.Network()
    compartments = set()
    entities = set()
    processes = set()
    modulations = set()
    logical_operator_nodes = set()
    for filename in filenames:
        sbgn = libsbgn.parse(filename, silence=True)
        sbgnmap = sbgn.get_map()
        for glyph in sbgnmap.get_glyph(): # making compartments
            if glyph.get_class().name == "COMPARTMENT":
                comp = utils._make_compartment_from_glyph(glyph)
                compartments.add(comp)
        for glyph in sbgnmap.get_glyph(): # making entities
            if glyph.get_class().name in [attribute.name for attribute in list(csbgnpy.pd.EntityClazz)]:
                entity = csbgnpy.pd.utils._make_entity_from_glyph(glyph, sbgnmap, compartments)
                entities.add(entity)
        for glyph in sbgnmap.get_glyph(): # making processes
            if glyph.get_class().name in [attribute.name for attribute in list(csbgnpy.pd.ProcessClazz)]:
                proc = utils._make_process_from_glyph(glyph, sbgnmap, entities, compartments)
                processes.add(proc)
        for glyph in sbgnmap.get_glyph(): # making logical operator nodes
            if glyph.get_class().name in [attribute.name for attribute in list(csbgnpy.pd.LogicalOperatorClazz)]:
                op  = csbgnpy.pd.utils._make_logical_operator_node_from_glyph(glyph, sbgnmap, entities, compartments, logical_operator_nodes)
                logical_operator_nodes.add(op)
        for arc in sbgnmap.get_arc(): # making modulations
            if arc.get_class().name in [attribute.name for attribute in list(csbgnpy.pd.ModulationClazz)]:
                mod = csbgnpy.pd.utils._make_modulation_from_arc(arc, sbgnmap, entities, compartments, logical_operator_nodes, processes)
                modulations.add(mod)
    for entity in entities:
        net.add_entity(entity)
    for proc in processes:
        net.add_process(proc)
    for mod in modulations:
        net.add_modulation(mod)
    for comp in compartments:
        net.add_compartment(comp)
    for op in logical_operator_nodes:
        net.add_logical_operator_node(op)
    return net

def _make_ui_from_glyph(glyph):
    if glyph.get_label() is not None:
        label = glyph.get_label().get_text()
        if ':' in label:
            return csbgnpy.pd.UnitOfInformation(glyph.get_id(), label.split(':')[0], label.split(':')[1])
        else:
            return csbgnpy.pd.UnitOfInformation(glyph.get_id(), None, label)
    else:
        return csbgnpy.pd.UnitOfInformation(glyph.get_id(), None, None)

def _make_sv_from_glyph(glyph, i):
    if glyph.get_state() is not None:
        id = glyph.get_id()
        value = glyph.get_state().get_value()
        if glyph.get_state().get_variable() is None:
            variable = csbgnpy.utils.Undefined(i)
        else:
            variable = glyph.get_state().get_variable()
    else:
        value = None
        variable = csbgnpy.utils.Undefined(i)
    return csbgnpy.pd.StateVariable(None, variable, value)

def _make_compartment_from_glyph(glyph):
    comp = Compartment()
    comp.id = glyph.get_id()
    comp.label = glyph.get_label().get_text()
    return comp

def _make_entity_from_glyph(glyph, sbgnmap, compartments):
    if glyph.get_class().name == "SOURCE_AND_SINK":
        return csbgnpy.pd.EmptySet()
    entity = csbgnpy.pd.Entity()
    entity.id = glyph.get_id()
    entity.clazz = csbgnpy.pd.EntityClazz[glyph.get_class().name]
    if glyph.get_label() is not None:
        entity.label = glyph.get_label().get_text()
    comp_id = glyph.get_compartmentRef()
    if comp_id is not None:
        comp_glyph = csbgnpy.pd.utils.get_glyph_by_id(sbgnmap, comp_id)
        comp = csbgnpy.pd.utils._make_compartment_from_glyph(comp_glyph)
        existent_comp = csbgnpy.pd.utils.get_object_from_collection(comp, compartments)
        entity.compartment = existent_comp
    for subglyph in glyph.get_glyph():
        if subglyph.get_class().name in [attribute.name for attribute in list(csbgnpy.pd.EntityClazz)]:
            subentity = csbgnpy.pd.utils._make_subentity_from_glyph(subglyph, sbgnmap)
            entity.add_component(subentity)
        elif subglyph.get_class().name == "UNIT_OF_INFORMATION":
            ui = utils._make_ui_from_glyph(subglyph)
            entity.add_unit_of_information(ui)
    i = 1
    for subglyph in csbgnpy.pd.utils.get_ordered_list_of_state_variables(glyph):
        sv = utils._make_sv_from_glyph(subglyph, i)
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
            subsubentity = csbgnpy.pd.utils._make_subentity_from_glyph(subglyph, sbgnmap)
            subentity.add_component(subsubentity)
        elif subglyph.get_class().name == "UNIT_OF_INFORMATION":
            ui = utils._make_ui_from_glyph(subglyph)
            subentity.add_unit_of_information(ui)
    i = 1
    for subglyph in csbgnpy.pd.utils.get_ordered_list_of_state_variables(glyph):
        sv = utils._make_sv_from_glyph(subglyph, i)
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
            source_glyph = csbgnpy.pd.utils.get_glyph_by_id_or_port_id(sbgnmap, source_id)
            if source_glyph.get_class().name in [attribute.name for attribute in list(csbgnpy.pd.EntityClazz)]:
                source = csbgnpy.pd.utils._make_entity_from_glyph(source_glyph, sbgnmap, compartments)
                existent_source = csbgnpy.pd.utils.get_object_from_collection(source, entities)
                op.add_child(existent_source)
            elif source_glyph.get_class().name in [attribute.name for attribute in list(csbgnpy.pd.LogicalOperatorClazz)]:
                source = csbgnpy.pd.utils._make_logical_operator_node_from_glyph(source_glyph, sbgnmap, entities, compartments, logical_operator_nodes)
                existent_source = csbgnpy.pd.utils.get_object_from_collection(source, logical_operator_nodes)
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
        if arc.get_class().name == "CONSUMPTION" and csbgnpy.pd.utils.get_glyph_by_id_or_port_id(sbgnmap, arc.get_target()) == glyph:
            source_id = arc.get_source()
            source_glyph = csbgnpy.pd.utils.get_glyph_by_id_or_port_id(sbgnmap, source_id)
            source = csbgnpy.pd.utils._make_entity_from_glyph(source_glyph, sbgnmap, compartments)
            existent_source = csbgnpy.pd.utils.get_object_from_collection(source, entities)
            proc.add_reactant(existent_source)
        elif arc.get_class().name == "PRODUCTION" and csbgnpy.pd.utils.get_glyph_by_id_or_port_id(sbgnmap, arc.get_source()) == glyph:
            target_id = arc.get_target()
            target_glyph = csbgnpy.pd.utils.get_glyph_by_id_or_port_id(sbgnmap, target_id)
            target = csbgnpy.pd.utils._make_entity_from_glyph(target_glyph, sbgnmap, compartments)
            existent_target = csbgnpy.pd.utils.get_object_from_collection(target, entities)
            proc.add_product(existent_target)
    return proc

def _make_modulation_from_arc(arc, sbgnmap, entities, compartments, logical_operator_nodes, processes):
    source_id = arc.get_source()
    source_glyph = csbgnpy.pd.utils.get_glyph_by_id_or_port_id(sbgnmap, source_id)
    if source_glyph.get_class().name in [attribute.name for attribute in list(csbgnpy.pd.EntityClazz)]:
        source = csbgnpy.pd.utils._make_entity_from_glyph(source_glyph, sbgnmap, compartments)
        existent_source = csbgnpy.pd.utils.get_object_from_collection(source, entities)
    elif source_glyph.get_class().name in [attribute.name for attribute in list(csbgnpy.pd.LogicalOperatorClazz)]:
        source = csbgnpy.pd.utils._make_logical_operator_node_from_glyph(source_glyph, sbgnmap, entities, compartments, logical_operator_nodes)
        existent_source = csbgnpy.pd.utils.get_object_from_collection(source, logical_operator_nodes)
    target_id = arc.get_target()
    target_glyph = csbgnpy.pd.utils.get_glyph_by_id_or_port_id(sbgnmap, target_id)
    target = csbgnpy.pd.utils._make_process_from_glyph(target_glyph, sbgnmap, entities, compartments)
    existent_target = csbgnpy.pd.utils.get_object_from_collection(target, processes)
    clazz = csbgnpy.pd.ModulationClazz[arc.get_class().name]
    modulation = csbgnpy.pd.Modulation(clazz, existent_source, existent_target)
    return modulation
