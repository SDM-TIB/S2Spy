# -*- coding: utf-8 -*-
from validation.utils import fileManagement
from validation.EvalPath import EvalPath
from validation.core.RuleMap import RuleMap
from validation.sparql.SPARQLEndpoint import SPARQLEndpoint

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
        firstShapeEval = self.shapesDict[self.node_order.pop(0)]
        targets = self.extractTargetAtoms(firstShapeEval)
        evalPathsMap = {firstShapeEval.id: EvalPath()}

        self.validate(
            0,
            EvalState(
                targets,
                evalPathsMap
            ),
            firstShapeEval
        )

        fileManagement.closeFile(self.validTargetsOuput)

    def extractTargetAtoms(self, shape):
        if shape.getTargetQuery() is None:
            return []
        else:
            return [self.targetAtoms(shape, shape.getTargetQuery())]

    def targetAtoms(self, shape, targetQuery):
        eval = self.endpoint.runQuery(
                shape.getId(),
                targetQuery,
                "JSON"
        )
        return ""  # TODO

    def extractTargetShapes(self):
        return [self.shapesDict[shape] for shape in self.shapesDict
                if self.shapesDict[shape].getTargetQuery() is not None]

    def validate(self, depth, state, focusShape):  # Algorithm 1 modified (SHACL2SPARQL)
        # termination condition 1: all targets are validated/violated
        if len(state.remainingTargets) == 0:
            return

        # termination condition 2: all shapes have been visited
        if len(state.visitedShapes) == len(self.shapesDict):
            for t in state.remainingTargets:
                self.registerTarget(t, True, depth, state, "not violated after termination", [])
            return

        print("focus shape: ", focusShape)
        self.evalShape(state, focusShape, depth)
        if len(self.node_order) == 0:
            return

        nextEvalShape = self.shapesDict[self.node_order.pop(0)]
        self.validate(depth + 1, state, nextEvalShape)

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

    #def validateFocusShapes(self, state, focusShapes, depth):
    #    for s in focusShapes:
    #        self.evalShape(state, s, depth)

    def evalShape(self, state, s, depth):
        self.evalConstraints(state, s)
        state.evaluatedPredicates.update(s.getPredicates())
        state.visitedShapes.add(s)
        #saveRuleNumber(state)

        self.saturate(state, depth, s)

    def evalConstraints(self, state, s):
        self.evalQuery(state, s.minQuery, s)

        for q in s.maxQueries:
            self.evalQuery(state, q, s)

    def evalQuery(self, state, q, s):
        eval = self.endpoint.runQuery(q.getId(), q.getSparql(), 'JSON')
        #print(eval)

    def negateUnMatchableHeads(self, state, depth, s):
        return  # TODO

    def getNegatedAtom(self, a):
        return a.getNegation() if a.isPos() else a

    def isSatisfiable(self, a, state, ruleHeads):
        return (not a.getPredicate() in state.evaluatedPredicates) or (a.getAtom() in ruleHeads) or (a in state.assignment)

class EvalState:
    def __init__(self, targetLiterals, evalPathsMap):
        self.remainingTargets = targetLiterals
        self.ruleMap = RuleMap()
        self.assignment = set()
        self.visitedShapes = set()
        self.evaluatedPredicates = set()
        self.validTargets = set()
        self.invalidTargets = set()
        self.evalPathsMap = evalPathsMap  # Map from shape name to a set of evaluation paths
