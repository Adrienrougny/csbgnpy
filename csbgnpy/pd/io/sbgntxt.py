from pyparsing import Word, alphanums, Optional, Literal, delimitedList, Forward, ParseException, Group
from functools import reduce

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
        self.emptylist = Literal("[") + Literal("]")
        self.svs = self.emptylist ^ (Literal("[") + Group(delimitedList(self.sv, delim = self.sep)) + Literal("]"))
        self.svs.setParseAction(self._toks_to_svs)
        self.uis = self.emptylist ^ (Literal("[") + delimitedList(self.ui, delim = self.sep) + Literal("]"))
        self.uis.setParseAction(self._toks_to_uis)
        self.compartment = "Compartment" + "(" + Optional(self.uis("uis")) + Optional(self.label("label")) + ")"
        self.compartment.setParseAction(self._toks_to_compartment)
        entityclasses = [Literal(elem.value.__name__) for elem in EntityEnum]
        self.entityclass = entityclasses[0]
        for e in entityclasses[1:]:
            self.entityclass |= e
        self.entityclass.setParseAction(self._toks_to_entity_class)
        subentityclasses = [Literal(elem.value.__name__) for elem in SubEntityEnum]
        self.subentityclass = subentityclasses[0]
        for e in subentityclasses[1:]:
            self.subentityclass |= e
        self.subentityclass.setParseAction(self._toks_to_subentity_class)
        self.components = Forward()
        self.subentity = self.subentityclass("clazz") + "(" + Optional(self.components("components")) + Optional(self.uis("uis") + self.svs("svs")) + self.label("label") + ")"
        self.subentity.setParseAction(self._toks_to_subentity)
        self.components << (self.emptylist | (Literal("[") + delimitedList(self.subentity("subentity"), delim = self.sep) + Literal("]")))
        self.components.setParseAction(self._toks_to_components)
        self.entity = self.entityclass("clazz") + "(" + Optional(self.components("components")) + Optional(self.uis("uis") + self.svs("svs")) + self.label("label") + Optional("#" + self.compartment("compartment")) + ")"
        self.entity.setParseAction(self._toks_to_entity)

    def _toks_to_sv(self, toks):
        val = toks.var
        var = toks.var
        if not var:
            var = UndefinedVar()
        return StateVariable(val = val, var = var)

    def _toks_to_svs(self, toks):
        return toks[1]

    def _toks_to_ui(self, toks):
        pre = ""
        if toks.pre:
            pre = toks.pre
        label = toks.label
        return UnitOfInformation(pre, label)

    def _toks_to_uis(self, toks):
        return toks[1:-1]

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

    def _toks_to_components(self, toks):
        return toks[1:-1]

    def _toks_to_entity(self, toks):
        ltoks = [tok for tok in toks]
        entity = toks.clazz()
        if toks.label:
            entity.label = toks.label
        if toks.svs:
            ind = ltoks.index(toks.svs)
            while isinstance(toks[ind], StateVariable):
                entity.add_sv(toks[ind])
                ind += 1
        if toks.uis:
            ind = ltoks.index(toks.uis)
            while isinstance(toks[ind], UnitOfInformation):
                entity.add_ui(toks[ind])
                ind += 1
        if toks.compartment:
            compartment = self._toks_to_compartment(toks.compartment)
            entity.compartment = compartment
        if toks.components:
            print(toks.components)
            ind = ltoks.index(toks.components)
            while isinstance(toks[ind], SubEntity):
                entity.add_component(toks[ind])
                ind += 1
        return entity

    def _toks_to_subentity_class(self, toks):
        for elem in SubEntityEnum:
            if elem.value.__name__ == toks[0]:
                return elem.value
        return None

    def _toks_to_subentity(self, toks):
        ltoks = [tok for tok in toks]
        subentity = toks.clazz()
        if toks.label:
            subentity.label = toks.label
        if toks.svs:
            ind = ltoks.index(toks.svs)
            while isinstance(toks[ind], StateVariable):
                subentity.add_sv(toks[ind])
                ind += 1
        if toks.uis:
            ind = ltoks.index(toks.uis)
            while isinstance(toks[ind], UnitOfInformation):
                subentity.add_ui(toks[ind])
                ind += 1
        if toks.components:
            ind = ltoks.index(toks.components)
            while isinstance(toks[ind], SubEntity):
                subentity.add_component(toks[ind])
                ind += 1
        return subentity

parser = Parser()
# res = parser.entity.parseString("Macromolecule(m#Compartment(c))")
res = parser.entity.parseString("Complex([SubComplex([SubMacromolecule(a)]c)][pre1:label1|pres2:label2][Val1@Var1|Val2@Var2]elabel#Compartment(clabel))")
# res = parser.entity.parseString("Macromolecule([pre1:label1|pres2:label2][Val1@Var1|Val2@Var2]elabel#Compartment(clabel))")
print(res)
