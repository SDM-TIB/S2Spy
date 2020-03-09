class RuleMap:
    def __init__(self):
        self.map = set()
        self.ruleNumber = 0

    def addRule(self, head, body):
        bodies = self.map.get(head)
        # TODO
