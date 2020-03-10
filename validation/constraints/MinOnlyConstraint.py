# -*- coding: utf-8 -*-
__author__ = "Monica Figuera and Philipp D. Rohde"

from validation.VariableGenerator import VariableType
from validation.constraints.Constraint import Constraint
from validation.sparql.ASKQuery import *


class MinOnlyConstraint(Constraint):

    def __init__(self, varGenerator, id, path, min, isPos, datatype=None, value=None, shapeRef=None, targetDef=None):
        super().__init__(id, isPos, None, datatype, value, shapeRef, targetDef)
        self.varGenerator = varGenerator
        self.path = path
        self.min = min
        self.variables = self.computeVariables()

    def computeVariables(self):
        atomicConstraint = Constraint()
        return atomicConstraint.generateVariables(self.varGenerator, VariableType.VALIDATION, self.min)

    @property
    def getMin(self):
        return self.min

    @property
    def getPath(self):
        return self.path

    def isSatisfied(self):
        if self.satisfied is not None:
            return self.satisfied
        if self.min == 1:
            self.satisfied = ASKQueryExistsConstraint(self.path, self.target).evaluate()
        else:
            self.satisfied = ASKQueryMinCardConstraint(self.path, self.target, self.min).evaluate()

        return self.satisfied

    def getValidInstances(self):
        return []

    def getViolations(self):
        return []
