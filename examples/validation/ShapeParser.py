# -*- coding: utf-8 -*-
import os
import json
from validation.SPARQLPrefixHandler import getPrefixString
from validation.VariableGenerator import VariableGenerator
from validation.constraints.MinOnlyConstraintImpl import MinOnlyConstraintImpl
from validation.constraints.MaxOnlyConstraintImpl import MaxOnlyConstraintImpl
from validation.constraints.ConstraintConjunctionImpl import ConstraintConjunctionImpl
from validation.ShapeImpl import ShapeImpl
from validation.SchemaImpl import SchemaImpl


class ShapeParser:

    def __init__(self):
        return

    def parseSchemaFromDir(self, path, shapeFormat):
        fileExtension = self.getFileExtension(shapeFormat)
        filesAbsPaths = []
        # r=root, d=directories, f = files
        for r, d, f in os.walk(path):
            for file in f:
                if fileExtension in file:
                    filesAbsPaths.append(os.path.join(r, file))

        if shapeFormat == "JSON":
            shapes = [self.parseJson(p) for p in filesAbsPaths]
            return SchemaImpl(shapes)
        else:
            print("Unexpected format: " + shapeFormat)

    def getFileExtension(self, shapeFormat):
        if shapeFormat == "SHACL":
            return ".ttl"
        else:
            return ".json" # dot added for convenience

    def parseJson(self, path):
        targetQuery = None

        file = open(path, "r")
        obj = json.load(file)
        targetDef = obj.get("targetDef")

        if targetDef is not None:
            query = targetDef["query"]
            if query is not None:
                targetQuery = getPrefixString() + query

        name = obj["name"]
        constraintsConjunctions = self.parseConstraints(name, obj["constraintDef"]["conjunctions"])

        return ShapeImpl(
                name,
                targetDef,
                targetQuery,
                constraintsConjunctions
        )

    def parseConstraints(self, shapeName, array):
        return [self.parseDisjunct(array[i], shapeName + "_d" + str(i + 1)) for i in range(len(array))]

    def parseDisjunct(self, array, id):
        varGenerator = VariableGenerator()
        constraints = [self.parseConstraint(varGenerator, array[i], id + "_c" + str(i + 1)) for i in range(len(array))]

        minConstraints = [inst for inst in constraints if isinstance(inst, MinOnlyConstraintImpl)]
        maxConstraints = [inst for inst in constraints if isinstance(inst, MaxOnlyConstraintImpl)]
        localConstraints = []  # *** hardcoded

        return ConstraintConjunctionImpl(
                id,
                minConstraints,
                maxConstraints,
                localConstraints
        )

    def parseConstraint(self, varGenerator, obj, id):
        min = obj.get("min")
        max = obj.get("max")
        shapeRef = obj.get("shape")
        datatype = obj.get("datatype")
        value = obj.get("value")
        path = obj.get("path")
        negated = obj.get("negated")

        oMin = None if (min is None) else int(min)
        oMax = None if (max is None) else int(max)
        oShapeRef = None if (shapeRef is None) else str(shapeRef)
        oDatatype = None if (datatype is None) else str(datatype)
        oValue = None if (value is None) else str(value)
        oPath = None if (path is None) else str(path)
        oNeg = True if (negated is None) else not negated  # True means it is a positive constraint

        if oPath is not None:
            if oMin is not None:
                if oMax is not None:
                    pass  # TODO
                return MinOnlyConstraintImpl(varGenerator, id, oPath, oMin, oNeg, oDatatype, oValue, oShapeRef)
            if oMax is not None:
                return MaxOnlyConstraintImpl(varGenerator, id, oPath, oMax, oNeg, oDatatype, oValue, oShapeRef)

        # TODO
        #return new LocalConstraintImpl(id, oDatatype, oValue, oShapeRef, oNeg);
