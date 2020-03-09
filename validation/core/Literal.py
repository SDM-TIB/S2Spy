# -*- coding: utf-8 -*-

class Literal:
    def __init__(self, pred, arg, isPos):
        self.pred = pred
        self.arg = arg
        self.isPos = isPos

    def getPredicate(self):
        return self.pred

    def getArg(self):
        return self.arg

    def getIsPos(self):
        return self.isPos

    def equals(self, o):
        if self == o:
            return True
        if o is None or type(self) != type(o):
            return False
        literal = o
        return self.isPos == literal.isPos and \
               self.pred == literal.pred and \
               self.arg == literal.arg
