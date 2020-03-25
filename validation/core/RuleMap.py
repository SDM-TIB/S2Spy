class RuleMap:
    def __init__(self):
        self.map = {}
        self.ruleNumber = 0

    def addRule(self, head, body):
        bodies = self.map.get(head)
        for k in self.keySet():
            if head.getPredicate() == k.getPredicate() and head.getArg() == k.getArg():
                bodies = self.map[k]
                head = k

        if bodies is None:
            s = set()
            for elem in body:
                s.add(elem)

            self.map[head] = s
            self.ruleNumber += 1
        else:
            for elem in body:
                if elem not in self.map[head]:
                    self.map[head].add(elem)
                self.ruleNumber += 1

    def getAllBodyAtoms(self):
        return self.map.values()

    def keySet(self):
        return self.map.keys()
