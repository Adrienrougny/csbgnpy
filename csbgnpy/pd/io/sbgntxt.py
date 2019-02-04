from pyparsing import Word, pyparsing_unicode, Optional, Literal, delimitedList, Forward, ParseException, Group, nums, Empty, printables, OneOrMore, WordEnd, Combine, Suppress, FollowedBy, oneOf
import functools

from csbgnpy.pd.io.utils import *
from csbgnpy.pd.sv import *
from csbgnpy.pd.ui import *
from csbgnpy.pd.compartment import *
from csbgnpy.pd.entity import *
from csbgnpy.utils import deescape_string

def read(*filenames):
    """Builds a map from SBGNtxt files

    :param filenames: names of files to be read
    :return: a map that is the union of the maps described in the input files
     """
    from csbgnpy.pd.network import Network
    net = Network()
    parser = Parser()
    for filename in filenames:
        with open(filename) as f:
            for i, line in enumerate(f):
                elem = None
                line = line.rstrip("\n\r")
                if len(line) > 0 and line.lstrip()[0] != "#":
                    try:
                        elem = parser.entry.parseString(line, parseAll = True)[0]
                    except ParseException as err:
                        print("Error in file {}, line {}, col {}".format(filename, i + 1, err.col))
                    if isinstance(elem, Entity):
                        net.add_entity(elem)
                    elif isinstance(elem, Process):
                        net.add_process(elem)
                    elif isinstance(elem, Compartment):
                        net.add_compartment(elem)
                    elif isinstance(elem, LogicalOperator):
                        net.add_lo(elem)
                    elif isinstance(elem, Modulation):
                        net.add_modulation(elem)
    return net

def write(net, filename):
    """Writes a map to a SBGNtxt file

    :param filename: the SBGNtxt file to be created
    """
    sbgntxt = network_to_strings(net)
    f = open(filename, 'w')
    f.write('\n'.join(sorted([str(s) for s in sbgntxt])))
    f.close()

def network_to_strings(net):
    l = []
    for entity in net.entities:
        l.append(str(entity))
    for comp in net.compartments:
        l.append(str(comp))
    for op in net.los:
        l.append(str(op))
    for mod in net.modulations:
        l.append(str(mod))
    for proc in net.processes:
        l.append(str(proc))
    return l

class Parser(object):
    """The class to parse SBGNtxt elements"""
    def __init__(self, debug = False):
        self.escaped_string = Combine(OneOrMore(oneOf(" ".join(["\{}".format(c) for c in RESERVED_CHARS])) | Word(pyparsing_unicode.Latin1.printables + pyparsing_unicode.Greek.printables + " ", excludeChars = RESERVED_CHARS, exact = 1)))
        self.sep = "|"
        self.left = "["
        self.right = "]"
        self.val = self.escaped_string
        self.var = self.escaped_string
        self.pre = self.escaped_string
        self.label = self.escaped_string

        self.sv = Literal("@") ^ self.val("val") ^ (self.val("val") + Literal("@")) ^ (Literal("@") + self.var("var")) ^ (self.val("val") + Literal("@") + self.var("var"))
        self.svs = Suppress(self.left) + (delimitedList(self.sv, delim = self.sep) | Empty()) + Suppress(self.right)
        self.sv.setParseAction(self._toks_to_sv)

        self.ui = Optional(self.pre("pre") + Literal(":")) + self.label("label")
        self.uis = Suppress(self.left) + (delimitedList(self.ui, delim = self.sep) | Empty()) + Suppress(self.right)
        self.ui.setParseAction(self._toks_to_ui)

        self.compartment = Literal("Compartment") + \
                Literal("(") + \
                Optional(self.uis("uis")) + \
                Optional(self.label("label")) + \
                Literal(")")
        self.compartment.setParseAction(self._toks_to_compartment)

        self.subentityclass = functools.reduce(lambda x, y: x ^ y, [Literal(elem.value.__name__) for elem in SubEntityEnum])
        self.subentityclass.setParseAction(self._toks_to_subentity_class)

        self.subentity = Forward()

        self.components = Suppress(self.left) + Optional(delimitedList(self.subentity, delim = self.sep)) + Suppress(self.right)

        self.subentity <<= self.subentityclass("clazz") + \
                Literal("(") + \
                (self.components("components") + self.uis("uis") + self.svs("svs") ^ \
                self.uis("uis") + self.svs("svs") ^ \
                self.components("components") ^ \
                Empty()) + \
                Optional(self.label("label")) + \
                Literal(")")
        self.subentity.setParseAction(self._toks_to_subentity)

        self.entityclass = functools.reduce(lambda x, y: x ^ y, [Literal(elem.value.__name__) for elem in EntityEnum])
        self.entityclass.setParseAction(self._toks_to_entity_class)

        self.entity = self.entityclass("clazz") + \
                Literal("(") + \
                (self.components("components") + self.uis("uis") + self.svs("svs") ^ \
                self.uis("uis") + self.svs("svs") ^ \
                self.components("components") ^ \
                Empty()) + \
                Optional(self.label("label")) + \
                Optional(Literal("#") + self.compartment("compartment")) + \
                Literal(")")
        self.entity.setParseAction(self._toks_to_entity)

        self.processparticipant = Optional(Word(nums)("stoech") + ":") + self.entity("participant")
        self.processparticipant.setParseAction(self._toks_to_processparticipant)

        self.processparticipants = Suppress(self.left) + delimitedList(self.processparticipant, delim = self.sep) + Suppress(self.right)

        self.processclass = functools.reduce(lambda x, y: x ^ y, [Literal(elem.value.__name__) for elem in ProcessEnum])
        self.processclass.setParseAction(self._toks_to_process_class)

        self.process = self.processclass("clazz") + \
                Literal("(") + \
                Optional(self.processparticipants("reactants") + self.processparticipants("products")) + \
                Optional(self.label("label")) + \
                Literal(")")
        self.process.setParseAction(self._toks_to_process)

        self.loclass = functools.reduce(lambda x, y: x ^ y, [Literal(elem.value.__name__) for elem in LogicalOperatorEnum])
        self.loclass.setParseAction(self._toks_to_lo_class)

        self.lo = Forward()

        self.lochild = self.entity | self.lo

        self.lochildren = Suppress(self.left) + delimitedList(self.lochild, delim = self.sep) + Suppress(self.right)

        self.lo <<= self.loclass("clazz") + "(" + self.lochildren("children") + ")"
        self.lo.setParseAction(self._toks_to_lo)

        self.modulationclass = functools.reduce(lambda x, y: x ^ y, [Literal(elem.value.__name__) for elem in ModulationEnum])
        self.modulationclass.setParseAction(self._toks_to_modulation_class)

        self.modulationsource = self.entity | self.lo
        self.modulationtarget = self.process

        self.modulation = self.modulationclass("clazz") + \
                Literal("(") + \
                self.modulationsource("source") + \
                Literal(self.sep) + \
                self.modulationtarget("target") + \
                Literal(")")
        self.modulation.setParseAction(self._toks_to_modulation)

        self.entry = (self.entity ^ self.process ^ self.lo ^ self.compartment ^ self.modulation) + Optional(Literal("#") + OneOrMore(Word(pyparsing_unicode.Latin1.alphanums + pyparsing_unicode.Greek.alphanums)))

    def _toks_to_sv(self, toks):
        val = None
        var = None
        if toks.val:
            val = deescape_string(toks.val)
        if toks.var:
            var = deescape_string(toks.var)
        return StateVariable(val = val, var = var)

    def _toks_to_ui(self, toks):
        pre = None
        if toks.pre:
            pre = deescape_string(toks.pre)
        label = deescape_string(toks.label)
        return UnitOfInformation(prefix = pre, label = label)

    def _toks_to_compartment(self, toks):
        label = None
        uis = None
        if toks.label:
            label = deescape_string(toks.label)
        if toks.uis:
            uis = deescape_string(toks.uis)
        return Compartment(label = label, uis = uis)

    def _toks_to_entity_class(self, toks):
        for elem in EntityEnum:
            if elem.value.__name__ == toks[0]:
                return elem.value
        return None

    def _toks_to_entity(self, toks):
        entity = toks.clazz()
        if toks.label:
            entity.label = deescape_string(toks.label)
        if toks.svs:
            for sv in toks.svs:
                entity.add_sv(sv)
        if toks.uis:
            entity.uis = toks.uis
        if toks.compartment:
            entity.compartment = toks.compartment
        if toks.components:
            entity.components = toks.components
        return entity

    def _toks_to_subentity_class(self, toks):
        for elem in SubEntityEnum:
            if elem.value.__name__ == toks[0]:
                return elem.value
        return None

    def _toks_to_subentity(self, toks):
        subentity = toks.clazz()
        if toks.label:
            subentity.label = deescape_string(toks.label)
        if toks.svs:
            for sv in toks.svs:
                subentity.add_sv(sv)
        if toks.uis:
            subentity.uis = toks.uis
        if toks.components:
            subentity.components = toks.components
        return subentity

    def _toks_to_process_class(self, toks):
        for elem in ProcessEnum:
            if elem.value.__name__ == toks[0]:
                return elem.value
        return None

    def _toks_to_processparticipant(self, toks):
        stoech = 1
        if toks.stoech:
            stoech = int(toks.stoech)
        return [[toks.participant] * int(stoech)]

    def _toks_to_process(self, toks):
        process = toks.clazz()
        if toks.label:
            process.label = deescape_string(toks.label)
        for reactant in toks.reactants:
            process.reactants += reactant
        for product in toks.products:
            process.products += product
        return process

    def _toks_to_modulation_class(self, toks):
        for elem in ModulationEnum:
            if elem.value.__name__ == toks[0]:
                return elem.value
        return None

    def _toks_to_modulation(self, toks):
        modulation = toks.clazz()
        modulation.source = toks.source[0]
        modulation.target = toks.target
        return modulation

    def _toks_to_lo_class(self, toks):
        for elem in LogicalOperatorEnum:
            if elem.value.__name__ == toks[0]:
                return elem.value
        return None

    def _toks_to_lo(self, toks):
        op = toks.clazz()
        for child in toks.children:
            op.add_child(child)
        return op
