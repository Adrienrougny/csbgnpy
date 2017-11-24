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

    def __hash__(self):
        return hash((self.__class__, self.source, self.target))

class Stimulation(Modulation):
    """The class to model positive influences"""
    pass

class Inhibition(Modulation):
    """The class to model negative influences"""
    pass

class NecessaryStimulation(Stimulation):
    """The class to model necessary stimulations"""
    pass
