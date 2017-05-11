class UnitOfInformation:

    def __init__(self, id = None, clazz = None, label = None):
        self.id = id
        self.clazz = clazz
        self.label = label

    def getId(self):
        return self.id

    def getClazz(self):
        return self.clazz

    def getLabel(self):
        return self.label

    def setClazz(self, clazz):
        self.clazz = clazz

    def setLabel(self, label):
        self.label = label

    def setId(self, i):
        self.id = i

    def __eq__(self, other):
        return isinstance(other, UnitOfInformation) and \
                self.clazz == other.clazz and \
                self.label == other.label

    def __hash__(self):
        return hash((self.clazz, self.label))

    def __str__(self):
        return "id: {0}, {1}:{2}".format(self.id, self.clazz, self.label)
