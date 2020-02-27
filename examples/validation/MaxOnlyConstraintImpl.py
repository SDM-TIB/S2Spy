from validation.VariableGenerator import VariableType
from validation.AtomicConstraintImpl import AtomicConstraintImpl

class MaxOnlyConstraintImpl(AtomicConstraintImpl):

    def __init__(self, varGenerator, id, path, max, datatype=None, value=None, shapeRef=None, isPos=None):
        super().__init__()
        self.varGenerator = varGenerator
        self.path = path
        self.max = max
        self.variables = self.computeVariables()

        self.id = id
        self.shapeRef = shapeRef
        self.isPos = isPos

    def computeVariables(self):
        atomicConstraint = AtomicConstraintImpl()
        return atomicConstraint.generateVariables(self.varGenerator, VariableType.VALIDATION, self.max + 1)

    @property
    def getMax(self):
        return self.max

    @property
    def getPath(self):
        return self.path
