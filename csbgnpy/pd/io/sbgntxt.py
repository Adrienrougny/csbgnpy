from pyparsing import Word, alphanums, Optional, Literal, delimitedList, Forward, ParseException, Group, nums, Empty, printables, OneOrMore, WordEnd, Combine
import functools

from csbgnpy.pd.io.utils import *
from csbgnpy.pd.sv import *
from csbgnpy.pd.ui import *
from csbgnpy.pd.compartment import *
from csbgnpy.pd.entity import *

def read(*filenames):
    from csbgnpy.pd.network import Network
    net = Network()
    parser = Parser()
    for filename in filenames:
        with open(filename) as f:
            for i, line in enumerate(f):
                elem = None
                if line[-1] == "\n":
                    line = line[:-1]
                try:
                    elem = parser.entry.parseString(line)[0]
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
    with open(filename, 'w') as f:
        for entity in net.entities:
            f.write("{}\n".format(str(entity)))
        for process in net.processes:
            f.write("{}\n".format(str(process)))
        for modulation in net.modulations:
            f.write("{}\n".format(str(modulation)))
        for op in net.los:
            f.write("{}\n".format(str(op)))
        for comp in net.compartments:
            f.write("{}\n".format(str(comp)))

class Parser(object):
    def __init__(self, debug = False):
        self.sep = "|"
        self.val = Word(alphanums + "β/_?")
        self.var = Word(alphanums + "β ")
        self.pre = Word(alphanums + "β")
        self.strlabel = alphanums + "β/_* -+("
        self.label = Word(self.strlabel + ")")
        self.labelend = Combine(OneOrMore(Word(self.strlabel) | ")" +~WordEnd(wordChars = self.strlabel + ")")))
        self.labelendend = Combine(OneOrMore(Word(self.strlabel) | Literal(")") + ~(Literal(")") + WordEnd(wordChars = self.strlabel + ")"))))

        self.sv = Literal("@") ^ self.val("val") ^ (self.val("val") + "@") ^ ("@" + self.var("var")) ^ (self.val("val") + "@" + self.var("var")) ^ Empty()
        self.sv.setParseAction(self._toks_to_sv)

        self.ui = Optional(self.pre("pre") + ":") + self.label("label")
        self.ui.setParseAction(self._toks_to_ui)

        self.svs = Literal("[") + (Empty() ^ Group(delimitedList(self.sv, delim = self.sep))("elems")) + Literal("]")

        self.uis = Literal("[") + Optional(Group(delimitedList(self.ui, delim = self.sep))("elems")) + Literal("]")

        self.compartment = Literal("Compartment") + \
                Literal("(") + \
                Optional(self.uis("uis")) + \
                Optional(self.labelend("label")) + Literal(")")

        self.compartmentinent = Literal("Compartment") + \
                Literal("(") + \
                Optional(self.uis("uis")) + \
                Optional(self.labelendend("label")).setDebug(flag = debug) + Literal(")").setDebug(flag = debug)

        self.compartment.setParseAction(self._toks_to_compartment)
        self.compartmentinent.setParseAction(self._toks_to_compartment)

        self.subentityclass = functools.reduce(lambda x, y: x ^ y, [Literal(elem.value.__name__) for elem in SubEntityEnum])
        self.subentityclass.setParseAction(self._toks_to_subentity_class)

        self.subentity = Forward()

        self.components = (Literal("[") + Optional(Group(delimitedList(self.subentity, delim = self.sep))("elems")) + Literal("]"))

        self.subentity <<= self.subentityclass("clazz") + "(" + \
                (self.components("components") + self.uis("uis") + self.svs("svs") ^ \
                self.uis("uis") + self.svs("svs") ^ \
                self.components("components") ^ \
                Empty()) + \
                self.labelend("label") + \
                Literal(")")

        self.subentity.setParseAction(self._toks_to_subentity)

        self.entityclass = functools.reduce(lambda x, y: x ^ y, [Literal(elem.value.__name__) for elem in EntityEnum])
        self.entityclass.setParseAction(self._toks_to_entity_class)

        self.entity = self.entityclass("clazz") + Literal("(") + \
                (self.components("components") + self.uis("uis") + self.svs("svs") ^ \
                self.uis("uis") + self.svs("svs") ^ \
                self.components("components") ^ \
                Empty()) + \
                (self.label("label") + Literal("#") + self.compartmentinent("compartment") + Literal(")") ^ \
                self.labelend("label") + Literal(")") ^ \
                Empty() + Literal(")"))
                # Optional(self.label("label")) + \
                # Optional("#" + self.compartment("compartment")) + ")"
        self.entity.setParseAction(self._toks_to_entity)

        self.processparticipant = Optional(Word(nums)("stoech") + ":") + self.entity("participant")
        self.processparticipant.setParseAction(self._toks_to_processparticipant)

        self.processparticipants = (Literal("[") + Group(delimitedList(self.processparticipant, delim = self.sep))("elems") + Literal("]"))

        self.processclass = functools.reduce(lambda x, y: x ^ y, [Literal(elem.value.__name__) for elem in ProcessEnum])
        self.processclass.setParseAction(self._toks_to_process_class)

        self.process = self.processclass("clazz").setDebug(flag = debug) + \
                Literal("(").setDebug(flag = debug) + \
                Optional(self.processparticipants("reactants").setDebug(flag = debug) + \
                self.processparticipants("products").setDebug(flag = debug)) + \
                Optional(self.labelend("label")).setDebug(flag = debug) + \
                Literal(")").setDebug(flag = debug)

        self.processinmod = self.processclass("clazz").setDebug(flag = debug) + \
                Literal("(").setDebug(flag = debug) + \
                Optional(self.processparticipants("reactants").setDebug(flag = debug) + \
                self.processparticipants("products").setDebug(flag = debug)) + \
                Optional(self.labelendend("label")).setDebug(flag = debug) + \
                Literal(")").setDebug(flag = debug)

        self.process.setParseAction(self._toks_to_process)
        self.processinmod.setParseAction(self._toks_to_process)

        self.loclass = functools.reduce(lambda x, y: x ^ y, [Literal(elem.value.__name__) for elem in LogicalOperatorEnum])
        self.loclass.setParseAction(self._toks_to_lo_class)

        self.lo = Forward()

        self.lochild = self.entity | self.lo
        # self.lochild.setParseAction(self._toks_to_lochild)

        self.lochildren = (Literal("[") + Group(delimitedList(self.lochild, delim = self.sep))("elems") + Literal("]"))

        self.lo <<= self.loclass("clazz") + "(" + self.lochildren("children") + ")"
        self.lo.setParseAction(self._toks_to_lo)

        self.modulationclass = functools.reduce(lambda x, y: x ^ y, [Literal(elem.value.__name__) for elem in ModulationEnum])
        self.modulationclass.setParseAction(self._toks_to_modulation_class)

        self.modulationsource = self.entity | self.lo
        self.modulationtarget = self.processinmod

        self.modulation = self.modulationclass("clazz").setDebug(flag = debug) + \
                Literal("(").setDebug(flag = debug) + \
                self.modulationsource("source").setDebug(flag = debug) + \
                Literal(self.sep).setDebug(flag = debug) + \
                self.modulationtarget("target").setDebug(flag = debug) + \
                Literal(")").setDebug(flag = debug)

        self.modulation.setParseAction(self._toks_to_modulation)

        self.entry = self.entity ^ self.process ^ self.lo ^ self.compartment ^ self.modulation

    def _toks_to_sv(self, toks):
        val = None
        if toks.val:
            val = toks.val
        if toks.var:
            var = toks.var
        else:
            var = UndefinedVar()
        return StateVariable(val = val, var = var)

    def _toks_to_ui(self, toks):
        pre = ""
        if toks.pre:
            pre = toks.pre
        label = toks.label
        return UnitOfInformation(pre, label)

    def _toks_to_compartment(self, toks):
        label = ""
        if toks.label:
            label = toks.label
        return Compartment(label)

    def _toks_to_entity_class(self, toks):
        for elem in EntityEnum:
            if elem.value.__name__ == toks[0]:
                return elem.value
        return None

    def _toks_to_entity(self, toks):
        entity = toks.clazz()
        if toks.label:
            entity.label = toks.label
        if toks.svs:
            for sv in toks.svs.elems:
                entity.add_sv(sv)
        if toks.uis:
            for ui in toks.uis.elems:
                entity.add_ui(ui)
        if toks.compartment:
            compartment = self._toks_to_compartment(toks.compartment)
            entity.compartment = compartment
        if toks.components:
            for subentity in toks.components.elems:
                entity.add_component(subentity)
        return entity

    def _toks_to_subentity_class(self, toks):
        for elem in SubEntityEnum:
            if elem.value.__name__ == toks[0]:
                return elem.value
        return None

    def _toks_to_subentity(self, toks):
        subentity = toks.clazz()
        if toks.label:
            subentity.label = toks.label
        if toks.svs:
            for sv in toks.svs.elems:
                subentity.add_sv(sv)
        if toks.uis:
            for ui in toks.uis.elems:
                subentity.add_ui(ui)
        if toks.components:
            for subsubentity in toks.components.elems:
                subentity.add_component(subsubentity)
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
            process.label = toks.label
        for reactant in toks.reactants.elems:
            process.reactants += reactant
        for product in toks.products.elems:
            process.products += product
        return process

    def _toks_to_modulation_class(self, toks):
        for elem in ModulationEnum:
            if elem.value.__name__ == toks[0]:
                return elem.value
        return None

    def _toks_to_modulation(self, toks):
        modulation = toks.clazz()
        modulation.source = toks.source
        modulation.target = toks.target
        return modulation

    def _toks_to_lo_class(self, toks):
        for elem in LogicalOperatorEnum:
            if elem.value.__name__ == toks[0]:
                return elem.value
        return None

    def _toks_to_lo(self, toks):
        op = toks.clazz()
        for child in toks.children.elems:
            op.add_child(child)
        return op
