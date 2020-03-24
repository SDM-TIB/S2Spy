class RuleMap:
    def __init__(self):
        self.map = {}
        self.ruleNumber = 0

    def addRule(self, head, body):
        strHead = str(head.pred) + " - " + str(head.arg) + " - " + str(head.isPos)
        bodies = self.map.get(head)
        if bodies is None:
            s = set(body)
            self.map[head] = s
            self.ruleNumber += 1
        else:
            if bodies.add(body):
                self.ruleNumber += 1

    def getAllBodyAtoms(self):
        return self.map.values()

    def keySet(self):
        return self.map.keys()
