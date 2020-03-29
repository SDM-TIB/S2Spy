class RuleMap:
    def __init__(self):
        self.map = {}
        self.ruleNumber = 0
        self.mapStr = {}

    def addRule(self, head, body):
        bodies = self.map.get(head)
        for k in self.keySet():
            if head.getPredicate() == k.getPredicate() and head.getArg() == k.getArg():
                bodies = self.map[k]
                head = k

        if bodies is None:
            if len(body) > 0:
                s = set()
                setStr = set()
                for elem in body:
                    s.add(elem)
                    setStr.add(elem.getStr())

                self.map[head] = s
                self.ruleNumber += 1

                self.mapStr[head.getStr()] = setStr
        else:
            for elem in body:
                if elem.getStr() not in self.mapStr[head.getStr()]:
                    self.map[head].add(elem)
                    self.mapStr[head.getStr()].add(elem.getStr())
                self.ruleNumber += 1
        #for k, v in self.map.items():
        #    print("key:", k.getPredicate(), k.getArg(), k.isPos)
        #    print("values:", [va.getPredicate() + va.getArg() + str(va.getIsPos()) for va in list(v)])
        #print("UPDATE DONE *** \n")

    def getAllBodyAtoms(self):
        return list(set().union(*self.map.values()))

    def keySet(self):
        return self.map.keys()
