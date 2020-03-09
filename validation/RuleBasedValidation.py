# -*- coding: utf-8 -*-
from validation.utils import fileManagement
from validation.EvalPath import EvalPath
from validation.core.RuleMap import RuleMap


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
        self.logOutput.write("Retrieving targets ...")
        targets = self.extractTargetAtoms()
        self.logOutput.write("\nTargets retrieved.")
        self.logOutput.write("Number of targets:\n" + str(len(targets)))
        #stats.recordInitialTargets(targets.size());

        evalPathsMap = {}

        for shape in self.targetShapes:
            evalPathsMap[shape] = EvalPath()

        self.validate(
            0,
            EvalState(
                targets,
                RuleMap(),
                set(),
                set(),
                set(),
                set(),
                set(),
                evalPathsMap
            ),
            self.targetShapes
        )

        fileManagement.closeFile(self.logOutput)
        fileManagement.closeFile(self.validTargetsOuput)
        fileManagement.closeFile(self.invalidTargetsOuput)
        fileManagement.closeFile(self.statsOutput)

    def extractTargetAtoms(self):
        return [self.targetAtoms(shape, shape.getTargetQuery())
                for shape in self.targetShapes if shape.getTargetQuery() is not None]

    def targetAtoms(self, shape, targetQuery):
        self.logOutput.write("Evaluating query:\n" + targetQuery)
        eval = self.endpoint.runQuery(
                shape.getId(),
                targetQuery
        )
        return ""

    def extractTargetShapes(self):
        return [shape for shape in self.schema.getShapes() if shape.getTargetQuery() is not None]

    def validate(self, depth, state, focusShapes):  # Algorithm 1 modified (SHACL2SPARQL)

        self.validateFocusShapes(state, focusShapes, depth)

        # termination condition 1: all targets are validated/violated
        # termination condition 2: all shapes have been visited

    def validateFocusShapes(self, state, focusShapes, depth):
        for s in focusShapes:
            self.evalShape(state, s, depth)

    def evalShape(self, state, s, depth):
        self.logOutput.write("evaluating queries for shape " + s.getId())
        for d in s.getDisjuncts():
            self.evalDisjunct(state, d, s)

        #state.evaluatedPredicates.addAll(s.getPredicates());
        #state.addVisitedShape(s);
        #saveRuleNumber(state);

        #self.logOutput.start("saturation ...")
        #saturate(state, depth, s)
        #stats.recordSaturationTime(self.logOutput.elapsed())
        self.logOutput.write("\nvalid targets: " + str(len(state.validTargets)))
        self.logOutput.write("\nInvalid targets: " + str(len(state.invalidTargets)))
        self.logOutput.write("\nRemaining targets: " + str(len(state.remainingTargets)))

    def evalDisjunct(self, state, d, s):
        self.evalQuery(state, d.getMinQuery(), s)

        for q in d.getMaxQueries():
            self.evalQuery(state, q, s)

    def evalQuery(self, state, q, s):
        print("query to be evaluated", q.getId(), q.getSparql())
        #logOutput.start("Evaluating query:\n" + q.getSparql());
        eval = self.endpoint.runQuery(q.getId(), q.getSparql())


class EvalState:
    def __init__(self, targetLiterals, ruleMap, assignment, visitedShapes, evaluatedPredicates, validTargets, invalidTargets, evalPathsMap):
        self.remainingTargets = targetLiterals
        self.ruleMap = ruleMap
        self.assignment = assignment
        self.visitedShapes = visitedShapes
        self.evaluatedPredicates = evaluatedPredicates
        self.validTargets = validTargets
        self.invalidTargets = invalidTargets
        self.evalPathsMap = evalPathsMap  # Map from shape name to a set of evaluation paths
