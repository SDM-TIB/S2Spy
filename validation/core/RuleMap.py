from collections import OrderedDict

class RuleMap:
    def __init__(self):
        self.map = {}
        self.ruleNumber = 0

    def addRule(self, head, body):
        if not isinstance(head, str):
            head = head.getStr()
        bodies = self.map.get(head)
        if bodies is None:
            s = set()
            s.add(frozenset(body))

            self.map[head] = s
            self.ruleNumber += 1
        else:
            self.map[head].add(frozenset(body))
            self.ruleNumber += 1

    def getAllBodyAtoms(self):
        return list(frozenset().union(*set().union(*self.map.values())))

    def keySet(self):
        return set(self.map.keys())
