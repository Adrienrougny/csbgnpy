from copy import deepcopy

class Modulation(object):
    """The class to model modulations"""
    def __init__(self, source = None, target = None, id = None):
        self.source = source
        self.target = target
        self.id = id

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
                self.source == other.source and \
                self.target == other.target

    def __str__(self):
        return "{}({}|{})".format(self.__class__.__name__, self.source, self.target)

    def __lt__(self, other):
        return str(self) < str(other)

    def __gt__(self, other):
        return str(self) > str(other)



class Stimulation(Modulation):
    """The class to model stimulations"""
    pass

class Inhibition(Modulation):
    """The class to model inhibitions"""
    pass

class Catalysis(Stimulation):
    """The class to model stimulations"""
    pass

class NecessaryStimulation(Stimulation):
    """The class to model necessary stimulations"""
    pass

class AbsoluteInhibition(Inhibition):
    """The class to model absolute inhibitions"""
    pass

class AbsoluteStimulation(Stimulation):
    """The class to model absolute stimulations"""
    pass
