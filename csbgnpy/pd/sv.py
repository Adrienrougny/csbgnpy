class StateVariable:
    def __init__(self, var = None, val = None, id = None):
        self.var = var
        self.val = val
        self.id = id

    def __eq__(self, other):
        return isinstance(other, StateVariable) and \
                self.var == other.var and \
                self.val == other.val

    def __hash__(self):
        return hash((self.var, self.val))
