class RuleMap:
    def __init__(self):
        self.map = {}
        self.ruleNumber = 0

    def addRule(self, head, body):
        if self.map.get(head) is None:
            s = set()
            s.add(frozenset(body))
            self.map[head] = s
        else:
            self.map[head].add(frozenset(body))

        self.ruleNumber += 1

    def getAllBodyAtoms(self):
        return list(frozenset().union(*set().union(*self.map.values())))

    def keySet(self):
        return set(self.map.keys())

    def getRuleNumber(self):
        return self.ruleNumber
