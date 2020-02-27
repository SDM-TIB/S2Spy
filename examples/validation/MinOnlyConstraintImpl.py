# -*- coding: utf-8 -*-
from validation.VariableGenerator import VariableType
from validation.AtomicConstraintImpl import AtomicConstraintImpl

class MinOnlyConstraintImpl(AtomicConstraintImpl):

    def __init__(self, varGenerator, id, path, min, datatype=None, value=None, shapeRef=None, isPos=None):
        super().__init__()
        self.varGenerator = varGenerator
        self.path = path
        self.min = min
        self.variables = self.computeVariables()

        self.id = id
        self.shapeRef = shapeRef
        self.isPos = isPos

    def computeVariables(self):
        atomicConstraint = AtomicConstraintImpl()
        return atomicConstraint.generateVariables(self.varGenerator, VariableType.VALIDATION, self.min)

    @property
    def getMin(self):
        return self.min

    @property
    def getPath(self):
        return self.path