# -*- coding: utf-8 -*-
__author__ = "Philipp D. Rohde"

from SHACL2SPARQLpy.ShapeParser import ShapeParser
from SHACL2SPARQLpy.sparql.SPARQLEndpoint import SPARQLEndpoint
from SHACL2SPARQLpy.utils import fileManagement
from SHACL2SPARQLpy.RuleBasedValidation import RuleBasedValidation
from SHACL2SPARQLpy.utils.globals import PARSING_ORDER


class ShapeNetwork:

    def __init__(self, schemaDir, schemaFormat, endpointURL, useSelectiveQueries, maxSplitSize, outputDir, ORDERBYinQueries):
        self.shapes = ShapeParser().parseShapesFromDir(schemaDir, schemaFormat, useSelectiveQueries, maxSplitSize, ORDERBYinQueries)
        self.shapesDict = {shape.getId(): shape for shape in self.shapes}  # TODO: use only the dict?
        self.endpoint = SPARQLEndpoint(endpointURL)
        self.outputDirName = outputDir

    @staticmethod
    def get_node_order():
        """The execution order of SHACL2SPARQL is based on the order of files as returned by the file system."""
        return PARSING_ORDER

    def validate(self):
        """Execute the Validation of the Shape Network."""
        node_order = self.get_node_order()

        for s in self.shapes:
            s.computeConstraintQueries()

        instancesReport = self.getInstances(node_order)
        return instancesReport

    def getInstances(self, node_order):
        """
        Reports valid and violated constraints of the graph
        :param node_order:
        """
        RuleBasedValidation(
            self.endpoint,
            node_order,
            self.shapesDict,
            fileManagement.openFile(self.outputDirName, "validation.log"),
            fileManagement.openFile(self.outputDirName, "targets_valid.log"),
            fileManagement.openFile(self.outputDirName, "targets_violated.log"),
            fileManagement.openFile(self.outputDirName, "stats.txt"),
            fileManagement.openFile(self.outputDirName, "traces.csv")
        ).exec()
        return 'Go to log files in {} folder to see report'.format(self.outputDirName)
