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
