import csbgnpy.pd

class EmptySet(object):
    def __init__(self, id = None):
        self.id = id

    def __eq__(self, other):
        return isinstance(other, csbgnpy.pd.EmptySet)

    def __hash__(self):
        return hash("emty_set")
