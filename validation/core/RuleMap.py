class RuleMap:
    def __init__(self):
        self.map = {}

    def addRule(self, head, body):
        if self.map.get(head) is None:
            s = set()
            s.add(frozenset(body))
            self.map[head] = s
        else:
            self.map[head].add(frozenset(body))  # does not return a boolean value, therefore summing 1 to ruleNumber
                                                 # each time is not going to be accurate

    def getAllBodyAtoms(self):
        return list(frozenset().union(*set().union(*self.map.values())))

    def keySet(self):
        return set(self.map.keys())
