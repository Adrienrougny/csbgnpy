from enum import Enum
import libsbgnpy.libsbgn as libsbgn
from csbgnpy.utils import *
from csbgnpy.af.compartment import *
from csbgnpy.af.activity import *
from csbgnpy.af.modulation import *
from csbgnpy.af.lo import *
from csbgnpy.af.ui import *
from csbgnpy.af.network import *

def read(*filenames):
    net = Network()
    activities = set()
    modulations = set()
    for filename in filenames:
        f = open(filename)
        for line in f:
            l = line[:-1].split("\t")
            if len(l) != 3:
                l = line[:-1].split(" ")
            source = BiologicalActivity()
            source.label = l[0]
            activities.add(source)
            print(source)
            target = BiologicalActivity()
            target.label = l[2]
            activities.add(target)
            if l[1] == "-1":
                mod = Inhibition()
            elif l[1] == "1":
                mod = Stimulation()
            mod.source = source
            mod.target = target
            print(target)
            modulations.add(mod)
            print(mod)
    net.activities = list(activities)
    net.modulations = list(modulations)
    return net

def write(net, filename):
    def _get_paths(obj):
        paths = []
        if isinstance(obj, Activity):
            paths.append([obj])
        else:
            for child in obj.children:
                child_paths = _get_paths(child)
                for path in child_paths:
                    paths.append([obj] + path)
        return paths
    f = open(filename, 'w')
    for modulation in net.modulations:
        if isinstance(modulation.source, Activity):
            f.write("{} {}  {}\n".format(modulation.source.label, 1 if isinstance(modulation, Stimulation) else -1, modulation.target.label))
        elif isinstance(modulation.source, LogicalOperator):
            paths = _get_paths(modulation.source)
            for path in paths:
                f.write("{} {}  {}\n".format(path[-1].label, 1 if isinstance(modulation, Stimulation) and len([obj for obj in path if isinstance(obj, NotOperator)]) % 2 == 0 or isinstance(modulation, Inhibition) and len([obj for obj in path if isinstance(obj, NotOperator)]) % 2 == 1 else -1, modulation.target.label))
    f.close()


