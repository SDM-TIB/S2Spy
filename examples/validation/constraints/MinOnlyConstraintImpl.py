# -*- coding: utf-8 -*-
from validation.VariableGenerator import VariableType
from validation.constraints.AtomicConstraintImpl import AtomicConstraintImpl
from validation.sparql import ASKQuery


class MinOnlyConstraintImpl(AtomicConstraintImpl):

    def __init__(self, varGenerator, id, path, min, isPos, datatype=None, value=None, shapeRef=None):
        super().__init__(id, isPos, None, datatype, value, shapeRef)
        self.varGenerator = varGenerator
        self.path = path
        self.min = min
        self.variables = self.computeVariables()

    def computeVariables(self):
        atomicConstraint = AtomicConstraintImpl()
        return atomicConstraint.generateVariables(self.varGenerator, VariableType.VALIDATION, self.min)

    @property
    def getMin(self):
        return self.min

    @property
    def getPath(self):
        return self.path

#    def isSatisfied(self):
#        if self.satisfied is not None:
#            return self.satisfied
#        if self.min == 1:
#            # exists query
#        else:
#            # min query
#        # set self.satisfied
#        # return self.satisfied
