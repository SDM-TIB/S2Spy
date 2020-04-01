class RuleMap:
    def __init__(self):
        self.map = {}
        self.ruleNumber = 0
        self.mapStr = {}

    def addRule(self, head, body):
        if not isinstance(head, str):
            head = head.getStr()
        bodies = self.mapStr.get(head)
        if bodies is None:
            s = set()
            setStr = set()
            for elem in body:
                s.add(elem)
                setStr.add(elem.getStr())

            self.map[head] = s
            self.ruleNumber += 1

            self.mapStr[head] = setStr
        else:
            self.map[head].update([elem for elem in body if elem.getStr() not in self.mapStr[head]])
            self.mapStr[head].update([elem.getStr() for elem in body])
            self.ruleNumber += 1
        #for k, v in self.map.items():
        #    print("key:", k)
        #    print("values:", [va.getPredicate() + va.getArg() + str(va.getIsPos()) for va in list(v)])
        #print("UPDATE DONE *** \n")

    def getAllBodyAtoms(self):
        return list(set().union(*self.map.values()))

    def keySet(self):
        return self.map.keys()
