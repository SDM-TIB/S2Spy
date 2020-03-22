# -*- coding: utf-8 -*-
import os
from validation.sparql.SPARQLEndpoint import SPARQLEndpoint
from validation.ShapeParser import ShapeParser
from validation.RuleBasedValidation import RuleBasedValidation
from validation.utils import fileManagement
from validation.core.GraphTraversal import GraphTraversal
from validation.core.ValidationTask import ValidationTask
from validation.ShapeNetwork import ShapeNetwork


class Eval:
    def __init__(self, args):
        """
        :type args: ...
        """
        self.outputDir = args.outputDir
        self.shapeFormat = "JSON"

        self.task = None
        if args.g:
            self.task = ValidationTask.GRAPH_VALIDATION
        elif args.s:
            self.task = ValidationTask.SHAPE_VALIDATION
        elif args.t:
            self.task = ValidationTask.INSTANCES_VALID
        elif args.v:
            self.task = ValidationTask.INSTACES_VIOLATION

        if args.graphTraversal == "DFS":
            self.graphTraversal = GraphTraversal.DFS
        elif args.graphTraversal == "BFS":
            self.graphTraversal = GraphTraversal.BFS

        self.createOutputDir()
        schemaDir = args.d
        workInParallel = False
        self.network = ShapeNetwork(schemaDir, self.shapeFormat, args.endpoint, self.graphTraversal, self.task, workInParallel)

        report = self.network.validate()  # run the evaluation of the SHACL constraints over the specified endpoint
        print("Report:", report)

#
#        validation = RuleBasedValidation(
#                        self.endpoint,
#                        self.schema,
#                        fileManagement.openFile("validation.log"),
#                        fileManagement.openFile("targets_valid.log"),
#                        fileManagement.openFile("targets_violated.log"),
#                        fileManagement.openFile("stats.txt")
#                    )
#
#        validation.exec()

    def createOutputDir(self):
        path = os.getcwd()
        os.makedirs(path + '/' + self.outputDir, exist_ok=True)

    def getSchema(self, schemaDir):
        shapeParser = ShapeParser()  # instantiate before calling its functions
        return shapeParser.parseSchemaFromDir(schemaDir, self.shapeFormat)
