import libsbgnpy.libsbgn as libsbgn
import csbgnpy.AF
# from EntityClazz import *
# from ProcessClazz import *
# from ModulationClazz import *
# from SubEntityClazz import *
# from StateVariable import *
# from LogicalOperator import *
# from UnitOfInformation import *

class Utils:
    @staticmethod
    def get_object_from_collection(obj, coll):
        for obj2 in coll:
            if obj2 == obj:
                return obj2
        return None

    @staticmethod
    def get_glyph_by_id_or_port_id(sbgnmap, i):
        for glyph in sbgnmap.get_glyph():
            if glyph.get_id() == i:
                return glyph
            for port in glyph.get_port():
                if port.get_id() == i:
                    return glyph
        return None

    @staticmethod
    def get_glyph_by_id(sbgnmap, id):
        for glyph in sbgnmap.get_glyph():
            if glyph.get_id() == id:
                return glyph
        return None


    @staticmethod
    def read_SBGNML(*filenames):
        net = csbgnpy.AF.Network()
        activities = set()
        compartments = set()
        modulations = set()
        logical_operator_nodes = set()
        for filename in filenames: #multiple files can be read at once
            sbgn = libsbgn.parse(filename, silence=True)
            sbgnmap = sbgn.get_map()
            for glyph in sbgnmap.get_glyph(): # making compartments
                if glyph.get_class().name == "COMPARTMENT":
                    comp = csbgnpy.AF.Utils._make_compartment_from_glyph(glyph)
                    compartments.add(comp)
            for glyph in sbgnmap.get_glyph(): # making activities
                if glyph.get_class().name in [attribute.name for attribute in list(csbgnpy.AF.ActivityClazz)]:
                    act  = csbgnpy.AF.Utils._make_activity_from_glyph(glyph, sbgnmap, compartments)
                    activities.add(act)
            for glyph in sbgnmap.get_glyph(): # making logical operator nodes
                if glyph.get_class().name in [attribute.name for attribute in list(csbgnpy.AF.LogicalOperatorClazz)]:
                    op  = csbgnpy.AF.Utils._make_logical_operator_node_from_glyph(glyph, sbgnmap, activities, compartments, logical_operator_nodes)
                    logical_operator_nodes.add(op)
            for arc in sbgnmap.get_arc(): # making modulations
                if glyph.get_class().name in [attribute.name for attribute in list(csbgnpy.AF.ModulationClazz)]:
                    mod = csbgnpy.AF.Utils._make_modulation_from_arc(arc, sbgnmap, activities, compartments, logical_operator_nodes)
                    modulations.add(mod)
        for act in activities:
            net.add_activity(act)
        for comp in compartments:
            net.add_compartment(comp)
        for mod in modulations:
            net.add_modulation(mod)
        for op in logical_operator_nodes:
            net.add_logical_operator_node(op)
        return net

    @staticmethod
    def _make_compartment_from_glyph(glyph):
        comp = csbgnpy.AF.Compartment()
        comp.set_id = glyph.get_id()
        if glyph.get_label() is not None:
            comp.label = glyph.get_label().get_text()
        return comp

    @staticmethod
    def _make_unit_of_informatiom_from_glyph(glyph):
        if glyph.get_label() is not None:
            label = glyph.get_label().get_text()
            clazz = csbgnpy.AF.UnitOfInformationClazz[libsbgn.GlyphClass(glyph.get_entity().get_name()).name]
        return csbgnpy.AF.UnitOfInformation(glyph.get_id(), clazz, label)

    @staticmethod
    def _make_activity_from_glyph(glyph, sbgnmap, compartments):
        act = csbgnpy.AF.Activity()
        act.id = glyph.get_id()
        act.clazz = csbgnpy.AF.ActivityClazz[glyph.get_class().name]
        if glyph.get_label() is not None:
            act.label = glyph.get_label().get_text()
        comp_id = glyph.get_compartmentRef()
        if comp_id is not None:
            comp_glyph = csbgnpy.AF.Utils.get_glyph_by_id(sbgnmap, comp_id)
            comp = csbgnpy.AF.Utils._make_compartment_from_glyph(comp_glyph)
            existent_comp = csbgnpy.AF.Utils.get_object_from_collection(comp, compartments)
            act.compartment = existent_comp
        for subglyph in glyph.get_glyph():
            if subglyph.get_class().name == "UNIT_OF_INFORMATION":
                ui = csbgnpy.AF.Utils._make_unit_of_informatiom_from_glyph(subglyph)
                act.ui = ui
        return act

    @staticmethod
    def _make_logical_operator_node_from_glyph(glyph, sbgnmap, activities, compartments, logical_operator_nodes):
        op = csbgnpy.AF.LogicalOperatorNode()
        op.clazz = csbgnpy.AF.LogicalOperatorClazz[glyph.get_class().name]
        for arc in sbgnmap.get_arc():
            if arc.get_class().name == "LOGIC_ARC" and arc.get_target() in [port.get_id() for port in glyph.get_port()]:
                source_id = arc.get_source()
                source_glyph = csbgnpy.AF.Utils.get_glyph_by_id_or_port_id(sbgnmap, source_id)
                if source_glyph.get_class().name in [attribute.name for attribute in list(csbgnpy.AF.ActivityClazz)]:
                    source = csbgnpy.AF.Utils._make_activity_from_glyph(source_glyph, sbgnmap, compartments)
                    existent_source = csbgnpy.AF.Utils.get_object_from_collection(source, activities)
                    op.add_child(existent_source)
                elif source_glyph.get_class().name in [attribute.name for attribute in list(csbgnpy.AF.LogicalOperatorClazz)]:
                    source = csbgnpy.AF.Utils._make_logical_operator_node_from_glyph(source_glyph, sbgnmap, activities, compartments, logical_operator_nodes)
                    existent_source = csbgnpy.AF.Utils.get_object_from_collection(source, logical_operator_nodes)
                    if existent_source is not None:
                        op.add_child(existent_source)
                    else:
                        op.add_child(source)
        return op

    @staticmethod
    def _make_modulation_from_arc(arc, sbgnmap, activities, compartments, logical_operator_nodes):
        source_id = arc.get_source()
        source_glyph = csbgnpy.AF.Utils.get_glyph_by_id_or_port_id(sbgnmap, source_id)
        if source_glyph.get_class().name in [attribute.name for attribute in list(csbgnpy.AF.ActivityClazz)]:
            source = csbgnpy.AF.Utils._make_activity_from_glyph(source_glyph, sbgnmap, compartments)
            existent_source = csbgnpy.AF.Utils.get_object_from_collection(source, activities)
        elif source_glyph.get_class().name in [attribute.name for attribute in list(csbgnpy.AF.LogicalOperatorClazz)]:
            source = csbgnpy.AF.Utils._makeLogicalOperatorFromGlyph(source_glyph, sbgnmap, activities, compartments)
            existent_source = csbgnpy.AF.Utils.get_object_from_collection(source, logical_operator_nodes)
        target_id = arc.get_target()
        target_glyph = csbgnpy.AF.Utils.get_glyph_by_id_or_port_id(sbgnmap, target_id)
        target = csbgnpy.AF.Utils._make_activity_from_glyph(target_glyph, sbgnmap, compartments)
        existent_target = csbgnpy.AF.Utils.get_object_from_collection(target, activities)
        clazz = csbgnpy.AF.ModulationClazz[arc.get_class().name]
        modulation = csbgnpy.AF.Modulation(clazz, existent_source, existent_target)
        return modulation
