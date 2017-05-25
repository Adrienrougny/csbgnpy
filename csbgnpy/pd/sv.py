class UndefinedVar(object):
    def __init__(self, num = None):
        self.num = num

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.num == other.num

    def __hash__(self):
        return hash((self.__class__, self.num,))

    def __str__(self):
        return "Undefined({0})".format(self.num)

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
