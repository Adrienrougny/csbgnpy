from copy import deepcopy

class Modulation(object):
    def __init__(self, source = None, target = None, id = None):
        self.source = source
        self.target = target
        self.id = id

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
                self.source == other.source and \
                self.target == other.target

    def __hash__(self):
        return hash((self.__class__, self.source, self.target))

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result

class Stimulation(Modulation):
    pass

class Inhibition(Modulation):
    pass

class Catalysis(Stimulation):
    pass

class NecessaryStimulation(Stimulation):
    pass
