# -*- coding: utf-8 -*-
from validation.utils import fileManagement
from validation.EvalPath import EvalPath
from validation.core.RuleMap import RuleMap


class RuleBasedValidation:
    def __init__(self, endpoint, node_order, shapesDict, validTargetsOuput):
        self.endpoint = endpoint
        self.node_order = node_order
        self.shapesDict = shapesDict
        self.validTargetsOuput = validTargetsOuput

        self.targetShapes = self.extractTargetShapes()  # set of shapes
        self.targetShapePredicates = [shape.getId() for shape in self.targetShapes]  # set of strings

        self.stats = None  # TODO new RuleBasedValidStats();
        self.resultSet = None  # TODO new RuleBasedResultSet();

    def exec(self):
        targets = self.extractTargetAtoms()

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

        fileManagement.closeFile(self.validTargetsOuput)

    def extractTargetAtoms(self):
        return [self.targetAtoms(shape, shape.getTargetQuery())
                for shape in self.targetShapes if shape.getTargetQuery() is not None]

    def targetAtoms(self, shape, targetQuery):
        eval = self.endpoint.runQuery(
                shape.getId(),
                targetQuery
        )
        return ""  # TODO

    def extractTargetShapes(self):

        return [self.shapesDict[shape] for shape in self.shapesDict
                if self.shapesDict[shape].getTargetQuery() is not None]

    def validate(self, depth, state, focusShapes):  # Algorithm 1 modified (SHACL2SPARQL)

        self.validateFocusShapes(state, focusShapes, depth)

        # termination condition 1: all targets are validated/violated
        # termination condition 2: all shapes have been visited

    def registerTarget(self, t, isValid, depth, state, logMessage, focusShape):
        log = str(t) + ", depth " + depth
                #(focusShape.map(shape -> ", focus shape " + shape).orElse("")) + ", " + logMessage
        evalPaths = None
        if isValid:
            self.validTargetsOuput.write(log)
            evalPaths = state.getEvalPaths(focusShape.get()) if focusShape is not None else set()
            self.resultSet.registerValidTarget(t, depth, focusShape, evalPaths)
        else:
            pass
            #self.invalidTargetsOuput.write(log);
            #Shape shape = focusShape.orElseThrow(
            #        () -> new RuntimeException("A violation result must have a focus shape"));
            #resultSet.registerInvalidTarget(t, depth, shape, state.getEvalPaths(shape));

    def saturate(self, state, depth, s):
        negated = self.negateUnMatchableHeads(state, depth, s)
        inferred = self.applyRules(state, depth, s)
        if negated or inferred:
            pass
            #self.saturate(state, depth, s)

    def applyRules(self, state, depth, s):
        return True   # TODO

    def getRules(self, head, bodies, state, retainedRules):
        return

    def validateFocusShapes(self, state, focusShapes, depth):
        for s in focusShapes:
            self.evalShape(state, s, depth)

    def evalShape(self, state, s, depth):
        self.evalConstraints(state, s)

        #state.evaluatedPredicates.addAll(s.getPredicates());
        #state.addVisitedShape(s);
        #saveRuleNumber(state);

        self.saturate(state, depth, s)

    def evalConstraints(self, state, s):
        self.evalQuery(state, s.minQuery, s)

        for q in s.maxQueries:
            self.evalQuery(state, q, s)

    def evalQuery(self, state, q, s):
        print("query to be evaluated", q.getId(), q.getSparql())
        #logOutput.start("Evaluating query:\n" + q.getSparql());
        eval = self.endpoint.runQuery(q.getId(), q.getSparql())

    def negateUnMatchableHeads(self, state, depth, s):
        return  # TODO

    def getNegatedAtom(self, a):
        return a.getNegation() if a.isPos() else a

    def isSatisfiable(self, a, state, ruleHeads):
        return (not a.getPredicate() in state.evaluatedPredicates) or (a.getAtom() in ruleHeads) or (a in state.assignment)

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
