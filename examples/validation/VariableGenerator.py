# -*- coding: utf-8 -*-
from enum import Enum

class VariableGenerator:
    def __init__(self):
        self.index = 0

    def incrementAndGet(self):
        self.index += 1
        return self.index

    def generateVariable(self, type):
        type = "p_"  # *** hardcoded
        i = self.incrementAndGet()
        return str(type) + str(i)

    def getFocusNodeVar(self):
        return "x"


class VariableType(Enum):
    VALIDATION = "p_"
    VIOLATION = "n_"  # not used

    @classmethod
    def prefix(cls):
        return cls.VALIDATION