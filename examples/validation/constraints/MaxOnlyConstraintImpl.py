from validation.VariableGenerator import VariableType
from validation.constraints.Constraint import Constraint


class MaxOnlyConstraintImpl(Constraint):

    def __init__(self, varGenerator, id, path, max, isPos, datatype=None, value=None, shapeRef=None):
        super().__init__(id, isPos, None, datatype, value, shapeRef)
        self.varGenerator = varGenerator
        self.path = path
        self.max = max
        self.variables = self.computeVariables()

    def computeVariables(self):
        atomicConstraint = Constraint()
        return atomicConstraint.generateVariables(self.varGenerator, VariableType.VALIDATION, self.max + 1)

    @property
    def getMax(self):
        return self.max

    @property
    def getPath(self):
        return self.path

    def isSatisfied(self):
        return False  # TODO

    def getValidInstances(self):
        return []  # TODO

    def getViolations(self):
        return []  # TODO
