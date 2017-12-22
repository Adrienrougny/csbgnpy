from pyparsing import Word, alphanums, Optional, Literal, delimitedList, Forward, ParseException, Group, nums, Empty
import functools

from csbgnpy.pd.io.utils import *
from csbgnpy.pd.sv import *
from csbgnpy.pd.ui import *
from csbgnpy.pd.compartment import *
from csbgnpy.pd.entity import *

class Parser(object):
    def __init__(self):
        self.sep = "|"
        self.val = Word(alphanums)
        self.var = Word(alphanums)
        self.pre = Word(alphanums)
        self.label = Word(alphanums)

        self.sv = Optional(self.val("val")) + "@" + Optional(self.var("var"))
        self.sv.setParseAction(self._toks_to_sv)

        self.ui = Optional(self.pre("pre") + ":") + self.label("label")
        self.ui.setParseAction(self._toks_to_ui)

        self.svs = Literal("[") + Optional(Group(delimitedList(self.sv, delim = self.sep))("elems")) + Literal("]")

        self.uis = Literal("[") + Optional(Group(delimitedList(self.ui, delim = self.sep))("elems")) + Literal("]")

        self.compartment = "Compartment" + "(" + Optional(self.uis("uis")) + Optional(self.label("label")) + ")"
        self.compartment.setParseAction(self._toks_to_compartment)

        self.subentityclass = functools.reduce(lambda x, y: x | y, [Literal(elem.value.__name__) for elem in SubEntityEnum])
        self.subentityclass.setParseAction(self._toks_to_subentity_class)

        self.subentity = Forward()

        self.components = (Literal("[") + Optional(Group(delimitedList(self.subentity, delim = self.sep))("elems")) + Literal("]"))

        self.subentity <<= self.subentityclass("clazz") + "(" + (self.components("components") + self.uis("uis") + self.svs("svs") | \
                self.uis("uis") + self.svs("svs") | \
                self.components("components") | \
                Empty()) + \
                self.label("label") + ")"
        self.subentity.setParseAction(self._toks_to_subentity)

        self.entityclass = functools.reduce(lambda x, y: x | y, [Literal(elem.value.__name__) for elem in EntityEnum])
        self.entityclass.setParseAction(self._toks_to_entity_class)

        self.entity = self.entityclass("clazz") + "(" + (self.components("components") + self.uis("uis") + self.svs("svs") | \
                self.uis("uis") + self.svs("svs") | \
                self.components("components") | \
                Empty()) + \
                Optional(self.label("label")) + \
                Optional("#" + self.compartment("compartment")) + ")"
        self.entity.setParseAction(self._toks_to_entity)

        self.processparticipant = Optional(Word(nums)("stoech") + ":") + self.entity("participant")
        self.processparticipant.setParseAction(self._toks_to_processparticipant)

        self.processparticipants = (Literal("[") + Group(delimitedList(self.processparticipant, delim = self.sep))("elems") + Literal("]"))

        self.processclass = functools.reduce(lambda x, y: x | y, [Literal(elem.value.__name__) for elem in ProcessEnum])
        self.processclass.setParseAction(self._toks_to_process_class)

        self.process = self.processclass("clazz") + "(" + Optional(self.processparticipants("reactants") + self.processparticipants("products")) + Optional(self.label("label")) + ")"
        self.process.setParseAction(self._toks_to_process)

    def _toks_to_sv(self, toks):
        val = toks.val
        var = toks.var
        if not var:
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

parser = Parser()
# res = parser.entity.parseString("Macromolecule(m#Compartment(c))")
# res = parser.entity.parseString("Complex([SubComplex([SubMacromolecule(a)]c)][pre1:label1|pres2:label2][Val1@Var1|Val2@Var2]elabel#Compartment(clabel))")
# res = parser.entity.parseString("Complex([SubComplex([SubMacromolecule([][vaaal@vaaar]a)]c)][pre1:label1|pres2:label2][Val1@Var1|Val2@Var2]elabel#Compartment(clabel))")
# res = parser.entity.parseString("Macromolecule(m)")
res = parser.entity.parseString("EmptySet()")
res = parser.process.parseString("GenericProcess([Macromolecule(a)][Macromolecule([][P@var1]a)])")

# res = parser.components.parseString("[]")
# res = parser.subentity.parseString("SubComplex([SubMacromolecule([][vaaal@vaaar]a)]c)")
# res = parser.entity.parseString("Macromolecule([pre1:label1|pres2:label2][Val1@Var1|Val2@Var2]elabel#Compartment(clabel))")
print(res[0])
