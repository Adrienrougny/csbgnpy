from csbgnpy.utils import escape_string

class UndefinedVar(object):
    """The class to model undefined variables"""
    def __init__(self, num = None):
        self.num = num

    def __eq__(self, other):
        return isinstance(other, UndefinedVar) and self.num == other.num


class StateVariable(object):
    """The class to model state variables"""
    def __init__(self, var = None, val = None, id = None):
        self.var = var
        self.val = val
        self.id = id

    def __eq__(self, other):
        return isinstance(other, StateVariable) and \
                self.var == other.var and \
                self.val == other.val


    def __str__(self):
        s = ""
        if self.val:
            s += escape_string(self.val)
        s += "@"
        if not isinstance(self.var, UndefinedVar):
            s += escape_string(self.var)
        # else:
        #     s += "Undefined({})".format(self.var.num)
        return s

    def __lt__(self, other):
        return str(self) < str(other)

    def __gt__(self, other):
        return str(self) > str(other)
