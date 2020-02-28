# -*- coding: utf-8 -*-

class AtomicConstraintImpl:

    def __init__(self, id=None, isPos=None, violated=False, datatype=None, value=None, shapeRef=None):
        self.id = id
        self.isPos = isPos
        self.violated = violated

        self.datatype = datatype
        self.value = value
        self.shapeRef = shapeRef

        self.variables = ()

    def getDatatype(self):
        return self.datatype

    def getValue(self):
        return self.value

    def getShapeRef(self):
        return self.shapeRef

    def getId(self):
        return self.id

    def getIsPos(self):
        return self.isPos

    def generateVariables(self, varGenerator, type, numberOfVariables):
        vars = []
        for elem in range(numberOfVariables):
            vars.append(varGenerator.generateVariable(type))

        return vars

    @property
    def getVariables(self):
        return self.variables