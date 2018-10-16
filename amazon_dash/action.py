

class Action:
    def __init__(self, use, params=None, condition=None, template=None):
        self.use = use
        self.params = params
        self.condition = condition
        self.template = template
