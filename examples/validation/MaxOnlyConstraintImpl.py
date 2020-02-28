from validation.VariableGenerator import VariableType
from validation.AtomicConstraintImpl import AtomicConstraintImpl

class MaxOnlyConstraintImpl(AtomicConstraintImpl):

    def __init__(self, varGenerator, id, path, max, isPos, datatype=None, value=None, shapeRef=None):
        super().__init__()
        self.varGenerator = varGenerator
        self.path = path
        self.max = max
        self.variables = self.computeVariables()

        self.id = id
        self.isPos = isPos
        self.shapeRef = shapeRef
        self.violated = False

    def computeVariables(self):
        atomicConstraint = AtomicConstraintImpl()
        return atomicConstraint.generateVariables(self.varGenerator, VariableType.VALIDATION, self.max + 1)

    @property
    def getMax(self):
        return self.max

    @property
    def getPath(self):
        return self.path
