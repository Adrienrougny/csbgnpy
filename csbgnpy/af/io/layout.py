class Layout(dict):
    pass

class NodeLayout(object):
    def __init__(self, id = None, x = 0, y = 0, w = 0, h = 0, ports = None):
        self.id = id
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.ports = ports if ports else []

class ArcLayout(object):
    def __init__(self, id = None, source = None, target = None, points = None):
        self.id = id
        self.source = source
        self.target = terget
        self.points = points if points else [(0,0), (0,0)]

class PortLayout(object):
    def __init__(self, id = None, x = 0, y = 0):
        self.id = id
        self.x = x
        self.y = y
