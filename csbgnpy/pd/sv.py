from copy import deepcopy

class UndefinedVar(object):
    """The class to model undefined variables"""
    def __init__(self, num = None):
        self.num = num

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.num == other.num

    def __hash__(self):
        return hash((self.__class__, self.num,))

    def __repr__(self):
        return "Undefined({0})".format(self.num)

    # def __deepcopy__(self, memo):
    #     cls = self.__class__
    #     result = cls.__new__(cls)
    #     memo[id(self)] = result
    #     for k, v in self.__dict__.items():
    #         setattr(result, k, deepcopy(v, memo))
    #     return result

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

    def __hash__(self):
        return hash((self.var, self.val))

    # def __deepcopy__(self, memo):
    #     cls = self.__class__
    #     result = cls.__new__(cls)
    #     memo[id(self)] = result
    #     for k, v in self.__dict__.items():
    #         setattr(result, k, deepcopy(v, memo))
    #     return result

    def __str__(self):
        s = ""
        if self.val:
            s += self.val
        s += "@"
        if not isinstance(self.var, UndefinedVar):
            s += self.var
        return s

    def __lt__(self, other):
        return str(self) < str(other)

    def __gt__(self, other):
        return str(self) > str(other)


