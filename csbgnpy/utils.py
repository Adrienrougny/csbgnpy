from modgrammar import *

class IdLookupError(LookupError):
    def __init__(self, id):
        self.id = id

    def __str__(self):
        return "id {0} not found".format(self.id)

class ObjectLookupError(LookupError):
    def __init__(self, obj):
        self.obj = obj

    def __str__(self):
        return "obj {0} not found".format(self.obj)

class GlyphIdLookupError(IdLookupError):
    def __init__(self, id):
        super().__init__(id)

    def __str__(self):
        return "glyph {0} not found".format(self.id)


def mean(c):
    return sum(c) / len(c)

def quote_string(s):
    return '"{0}"'.format(s)

def normalize_string(s):
    s = s.replace("*","_star")
    s = s.replace("@","_star")
    s = s.replace("@","_star")
    s = s.replace("+","_plus")
    s = s.replace("/","_")
    s = s.replace(" ","_")
    s = s.replace("-","_")
    s = s.replace("\n","_")
    s = s.replace("α","a")
    s = s.replace("β","b")
    s = s.replace("γ","c")
    s = s.replace("δ","d")
    s = s.replace("κ","g")
    s = s.lower()
    return s

def escape_string(s):
    s = s.replace("\n", "\\n")
    return s

def deescape_string(s):
    s = s.replace("\\n", "\n")
    return s

def get_object(obj, coll):
    for obj2 in coll:
        if obj2 == obj:
            return obj2
    raise ObjectLookupError(obj)

def get_object_by_id(coll, id):
    for obj in coll:
        if hasattr(obj, "id"):
            if obj.id == id:
                return obj
    raise IdLookupError(id)

def get_glyph_by_id_or_port_id(sbgnmap, id):
    for glyph in sbgnmap.get_glyph():
        if glyph.get_id() == id:
            return glyph
        for port in glyph.get_port():
            if port.get_id() == id:
                return glyph
    raise GlyphLookupError(id)

class GSimpleTerm(Grammar):
    grammar = (REF("GInteger") | REF("GConstant") | REF("GVariable") | REF("GString"))

class GComplexTerm(Grammar):
    grammar = (REF("GFunctionalTerm"))

class GTerm(Grammar):
    grammar = (REF("GSimpleTerm") | REF("GComplexTerm"))

class GInteger(Grammar):
    grammar = (OPTIONAL("-"), WORD("0-9"))
    def grammar_elem_init(self, sessiondata):
        s = ""
        if self[0]:
            s = "-"
        s += self[1].string
        self.name = s

class GString(Grammar):
    grammar = ('"', WORD('^"'), '"')
    def grammar_elem_init(self, sessiondata):
        self.name = self[1].string

class GVariable(Grammar):
    grammar = WORD("A-Z", "A-Za-z0-9_")
    def grammar_elem_init(self, sessiondata):
        self.name = self[0].string

class GConstant(Grammar):
    grammar = WORD("a-z", "A-Za-z0-9_")
    def grammar_elem_init(self, sessiondata):
        self.name = self[0].string

class GFunctionalTerm(Grammar):
    grammar = (WORD("a-z", "A-Za-z0-9_"), '(', LIST_OF(REF("GTerm"), sep= ','), ')')
    def grammar_elem_init(self, sessiondata):
        self.name = self[0].string
        self.arguments = [arg[0][0] for arg in self[2] if arg.string != ',']

class GAtom(Grammar):
    grammar = (WORD("A-Za-z", "A-Za-z0-9_"), '(', LIST_OF(REF("GTerm"), sep = ','), ')')
    def grammar_elem_init(self, sessiondata):
        self.name = self[0].string
        self.arguments = [arg[0][0] for arg in self[2] if arg.string != ',']

class FunctionalTerm(object):
    def __init__(self, name = None, arguments = None):
        self.name = name
        if arguments is None:
            self.arguments = []
        else:
            self.arguments = arguments

    def isground(self):
        for arg in self.arguments:
            if not arg.isground():
                return False
        return True

    def terminal_terms(self):
        terms = []
        for arg in self.arguments:
            argterms = arg.terminal_terms()
            for term in argterms:
                terms.append(term)
        return terms

    def __eq__(self, other):
        return self.__class__ == other.__class__ and str(self) == str(other)

    def substitute(self, dsub):
        new = deepcopy(self)
        for i, arg in enumerate(self.arguments):
            if isinstance(arg, Variable):
                if arg in dsub:
                    new.arguments[i] = dsub[arg]
            elif (isinstance(arg, FunctionalTerm) or isinstance(arg, Operation)) and not arg.isground():
                new.arguments[i] = arg.substitute(dsub)
        return new

    def substitute_in_order(self, lsub):
        dsub = Substitution()
        terms = self.terminal_terms()
        vars = [term for term in terms if isinstance(term, Variable)]
        for i, var in enumerate(vars):
            if i >= len(lsub):
                break
            dsub[var] = lsub[i]
        return self.substitute(dsub)

    def __str__(self):
        return self.name + "(" + ",".join([str(arg) for arg in self.arguments]) + ")"

    def __hash__(self):
        return hash((self.name, tuple(self.arguments)))

class Constant(object):
    def __init__(self, name = None):
        self.name = name

    def isground(self):
        return True

    def terminal_terms(self):
        return [self]

    def __lt__(self, other):
        return str(self) < str(other)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.__class__ == other.__class__ and str(self) == str(other)

    def __hash__(self):
        return hash((self.__class__, self.name))

class Variable(object):
    def __init__(self, name = None):
        self.name = name

    def isground(self):
        return False

    def terminal_terms(self):
        return [self]

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.__class__ == other.__class__ and str(self) == str(other)

    def __hash__(self):
        return hash((self.__class__, self.name))

class Atom(object):
    def __init__(self, name = None, arguments = None):
        self.name = name
        if not arguments:
            self.arguments = []
        else:
            self.arguments = arguments

    def isground(self):
        for arg in self.atom.arguments:
                if not arg.isground():
                    return False
        return True

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.name == other.name and self.arguments == other.arguments

    def terminal_terms(self):
        terms = []
        for arg in self.arguments:
            argterms = arg.terminal_terms()
            for term in argterms:
                terms.append(term)
        return terms

    def substitute(self, dsub):
        new = deepcopy(self)
        for i, arg in enumerate(self.arguments):
            if isinstance(arg, Variable):
                if arg in dsub:
                    new.arguments[i] = dsub[arg]
            elif isinstance(arg, FunctionalTerm) or isinstance(arg, Operation) and not arg.isground():
                new.arguments[i] = arg.substitute(dsub)
        return new

    def substitute_in_order(self, lsub):
        dsub = Substitution()
        terms = self.terminalTerms()
        vars = [term for term in terms if isinstance(term, Variable)]
        for i, var in enumerate(vars):
            if i >= len(lsub):
                break
            dsub[var] = lsub[i]
        return self.substitute(dsub)

    def eval(self):
        new = deepcopy(self)
        for i, arg in enumerate(new.arguments):
            if isinstance(arg, Operation) and arg.isground():
                new.arguments[i] = Constant(str(eval(str(arg))))
        return new

    def __str__(self):
        return "{0}({1})".format(self.name, ','.join([str(arg) for arg in self.arguments]))

    def __hash__(self):
        return hash((self.__class__, self.name, tuple(self.arguments)))

def logic_factory(obj):
    if isinstance(obj, GVariable):
        return Variable(obj.name)
    elif isinstance(obj, GConstant):
        return Constant(obj.name)
    elif isinstance(obj, GInteger):
        return Constant(obj.name)
    elif isinstance(obj, GString):
        return Constant(obj.name)
    elif isinstance(obj, GFunctionalTerm):
        return FunctionalTerm(obj.name, [logic_factory(arg) for arg in obj.arguments])
    elif isinstance(obj, GAtom):
        return Atom(obj.name, [logic_factory(arg) for arg in obj.arguments])
    return None

def parse_atom(s):
    parser = GAtom.parser()
    try:
        atom = parser.parse_text(s, matchtype = "complete", eof = True)
        atom = logic_factory(atom)
        return atom
    except ParseError as error:
        print('Parsing error, col {}: got "{}", expected {}'.format(error.col, s[error.col], ' or '.join(['"{}"'.format(str(exp)) for exp in error.expected])))
        print("Parse error:".format(s))
        exit()
