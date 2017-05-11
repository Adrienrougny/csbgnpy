import csbgnpy.PD

class EmptySet(object):
    def __init__(self):
        pass

    def __eq__(self, other):
        return isinstance(other, csbgnpy.PD.EmptySet)

    def __hash__(self):
        return hash("emty_set")
