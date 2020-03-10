# -*- coding: utf-8 -*-
__author__ = "Monica Figuera and Philipp D. Rohde"

import os
import json
from validation.sparql.SPARQLPrefixHandler import getPrefixString
from validation.VariableGenerator import VariableGenerator
from validation.constraints.MinMaxConstraint import MinMaxConstraint
from validation.constraints.MinOnlyConstraint import MinOnlyConstraint
from validation.constraints.MaxOnlyConstraint import MaxOnlyConstraint
from validation.Shape import Shape
from validation.SchemaImpl import SchemaImpl


class ShapeParser:
    # TODO: Schema will become Graph

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
            return ".json"  # dot added for convenience

    def parseJson(self, path):
        targetQuery = None

        file = open(path, "r")
        obj = json.load(file)
        targetDef = obj.get("targetDef")

        if targetDef is not None:
            query = targetDef["query"]
            if query is not None:
                targetQuery = getPrefixString() + query
            targetDef = targetDef["class"]

        name = obj["name"]
        constraints = self.parseConstraints(name, obj["constraintDef"]["conjunctions"], targetDef)

        return Shape(name, targetDef, targetQuery, constraints)

    def parseConstraints(self, shapeName, array, targetDef):
        varGenerator = VariableGenerator()
        id = shapeName + "_d1"  # str(i + 1) but there is only one set of conjunctions
        return [self.parseConstraint(varGenerator, array[0][i], id + "_c" + str(i + 1), targetDef) for i in range(len(array))]

    def parseConstraint(self, varGenerator, obj, id, targetDef):
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
                    return MinMaxConstraint(varGenerator, id, oPath, oMin, oMax, oNeg, oDatatype, oValue, oShapeRef, targetDef)
                return MinOnlyConstraint(varGenerator, id, oPath, oMin, oNeg, oDatatype, oValue, oShapeRef, targetDef)
            if oMax is not None:
                return MaxOnlyConstraint(varGenerator, id, oPath, oMax, oNeg, oDatatype, oValue, oShapeRef, targetDef)

        # TODO
        #return new LocalConstraintImpl(id, oDatatype, oValue, oShapeRef, oNeg);
