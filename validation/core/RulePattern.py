# -*- coding: utf-8 -*-

class RulePattern:
    # If a value for each variable is produced (by a solution mapping), then the rule pattern can be instantiated.
    # Note that it may be the case that these variables do not appear in the the body of the rule (because there is no constraint to propagate on these values, they only need to exist)

    def __init__(self, head, body):
        self.head = head
        self.literals = body

        if len(body) > 0:
            if type(body[0]) == list:
                body = body[0]          # *** (1)

        #print("Rule Pattern - head: ", head.getPredicate(), " ", head.getArg(), " body: ", str([b.getPredicate() + " " + b.getArg() + " " + str(b.getIsPos()) for b in body]))

        self.variables = [head.getArg()] + [a.getArg() for a in body if a is not None]

    def getVariables(self):
        return self.variables