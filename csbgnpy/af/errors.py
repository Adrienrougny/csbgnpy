class ActivityLookupError(LookupError):
    def __init__(self, a):
        self.a = a

    def __str__(self):
        return "activity {} not found".format(self.id)
