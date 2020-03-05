# -*- coding: utf-8 -*-
import os
from validation.ShapeParser import ShapeParser
from validation.RuleBasedValidation import RuleBasedValidation
from validation.utils import fileManagement

class Eval:

    def __init__(self, args):
        """
        :type args: ...
        """
        self.endpoint = args.endpoint
        self.outputDir = args.outputDir
        self.shapeFormat = "JSON"

        self.schema = None
        self.graph = None

        self.parseArguments(args)

        shapes = self.schema.getShapes()
        for s in shapes:
            s.askViolations()
            s.computeConstraintQueries(self.schema, self.graph)

        self.createOutputDir()

        validation = RuleBasedValidation(
                            self.endpoint,
                            self.schema,
                            fileManagement.openFile("validation.log"),
                            fileManagement.openFile("targets_valid.log"),
                            fileManagement.openFile("targets_violated.log"),
                            fileManagement.openFile("stats.txt")
                    )

    def createOutputDir(self):
        path = os.getcwd()
        os.makedirs(path + '/' + self.outputDir, exist_ok=True)

    # to do: schemaFile and schemaString
    def parseArguments(self, args):
        # E.g.: -d. ../examples/shapes/nonRec/2/ "http://dbpedia.org/sparql". /output/

        schemaDir = args.d
        self.schema = self.getSchema(schemaDir)  # *** parse and interpret schema files

        #log.info("endPoint: |" + endpoint.getURL() + "|");
        #schemaDir.ifPresent(d -> log.info("shape directory: |" + d + "|"));
        #log.info("output directory: |" + outputDir + "|");

    def getSchema(self, schemaDir):
        shapeParser = ShapeParser() # instantiate before calling its functions
        return shapeParser.parseSchemaFromDir(schemaDir, self.shapeFormat)
