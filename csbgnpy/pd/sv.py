class StateVariable:

    def __init__(self, id = None, variable = None, value = None):
        self.id = id
        self.variable = variable
        self.value = value

    def __eq__(self, other):
        return isinstance(other, StateVariable) and \
                self.variable == other.variable and \
                self.value == other.value

    def __hash__(self):
        return hash((self.variable, self.value))
