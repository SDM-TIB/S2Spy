# -*- coding: utf-8 -*-
from validation.utils import fileManagement

class RuleBasedValidation:

    def __init__(self, endpoint, schema, logOutput, validTargetsOuput, invalidTargetsOuput, statsOutput):
        self.endpoint = endpoint
        self.schema = schema
        self.logOutput = logOutput
        self.validTargetsOuput = validTargetsOuput
        self.invalidTargetsOuput = invalidTargetsOuput
        self.statsOutput = statsOutput

        self.targetShapes = self.extractTargetShapes()  # set of shapes
        self.targetShapePredicates = [shape.getId() for shape in self.targetShapes]  # set of strings

        self.stats = None  # TODO new RuleBasedValidStats();
        self.resultSet = None  # TODO new RuleBasedResultSet();

    def exec(self):
        fileManagement.closeFile(self.logOutput)
        fileManagement.closeFile(self.validTargetsOuput)
        fileManagement.closeFile(self.invalidTargetsOuput)
        fileManagement.closeFile(self.statsOutput)

    def extractTargetShapes(self):
        return [shape for shape in self.schema.getShapes() if shape.getTargetQuery() is not None]