from csbgnpy import *

class Modulation:

    def __init__(self, clazz = None, source = None, target = None):
        self.source = source
        self.target = target
        self.clazz = clazz

    def __eq__(self, other):
        return self.source == other.source and \
                self.target == other.target

    def __hash__(self):
        return hash((self.source, self.target))
