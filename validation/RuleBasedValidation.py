# -*- coding: utf-8 -*-
from validation.utils import fileManagement
from validation.EvalPath import EvalPath
from validation.core.RuleMap import RuleMap
from validation.core.Literal import Literal
import time
import re

class RuleBasedValidation:
    def __init__(self, endpoint, node_order, shapesDict, validTargetsOuput):
        self.endpoint = endpoint
        self.node_order = node_order
        self.shapesDict = shapesDict
        self.validTargetsOuput = validTargetsOuput
        self.targetShapePredicates = []

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
            return self.targetAtoms(shape, shape.getTargetQuery())

    def targetAtoms(self, shape, targetQuery):
        eval = self.endpoint.runQuery(
                shape.getId(),
                targetQuery,
                "JSON"
        )
        bindings = eval["results"]["bindings"]
        targetLiterals = [Literal(shape.getId(), b["x"]["value"], True) for b in bindings]

        return targetLiterals

    def validate(self, depth, state, focusShape):  # Algorithm 1 modified (SHACL2SPARQL)
        # termination condition 1: all targets are validated/violated
        if len(state.remainingTargets) == 0:
            return

        # termination condition 2: all shapes have been visited
        if len(state.visitedShapes) == len(self.shapesDict):
            for t in state.remainingTargets:
                self.registerTarget(t, True, depth, state, "not violated after termination", [])
            return

        self.evalShape(state, focusShape, depth)  # validate selected shape
        if len(self.node_order) == 0:
            return

        self.currentEvalShape = self.shapesDict[self.node_order.pop(0)]
        self.targetShapePredicates = self.currentEvalShape.id  # ***

        self.validate(depth + 1, state, self.currentEvalShape)

    def registerTarget(self, t, isValid, depth, state, logMessage, focusShape):
        # save result to output file
        return True

    def saturate(self, state, depth, s):
        negated = self.negateUnMatchableHeads(state, depth, s)
        inferred = self.applyRules(state, depth, s)
        print("Saturate: ", negated, inferred)

        if negated or inferred:
            self.saturate(state, depth, s)

    def getStrPredicate(self, a):
        pred = re.split("\(", a, 1)[0]
        pred = re.split("!", pred)[0]
        return pred

    def applyRules(self, state, depth, s):
        retainedRules = RuleMap()
        freshLiterals = [self._applyRules(head, [bodies], state, retainedRules) for head, bodies in state.ruleMap.map.items()
                         if self._applyRules(head, [bodies], state, retainedRules) is not None]  # *** [bodies]

        state.ruleMap = retainedRules
        state.assignment.update(freshLiterals)

        if len(freshLiterals) == 0:
            return False

        candidateValidTargets = [a for a in freshLiterals if self.getStrPredicate(a) in self.targetShapePredicates]

        part1 = dict()
        part1["true"] = [t for t in state.remainingTargets if t in candidateValidTargets]
        part1["false"] = [t for t in state.remainingTargets if t not in candidateValidTargets]

        state.remainingTargets = part1["false"]

        part2 = dict()
        part2["true"] = [t for t in part1["true"] if t.getIsPos()]
        part2["false"] = [t for t in part1["true"] if not t.getIsPos()]

        state.validTargets.update(part2["true"])
        state.invalidTargets.update(part2["false"])

        # TODO: register valid/invalid targets

        print("Remaining targets: " + str(len(state.remainingTargets)))

        return True

    def _applyRules(self, head, bodies, state, retainedRules):
        if any([self.applyRule(head, b, state, retainedRules) for b in bodies]):
            return head
        return None

    def applyRule(self, head, body, state, retainedRules):
        bodyStrMap = [elem.getStr() for elem in body]
        if set(bodyStrMap) <= state.assignment:
            return True

        matches = [a.getNegation().getStr() for a in body if a.getNegation().getStr() in state.assignment]  # ***
        if len(matches) == 0:  # no match
            retainedRules.addRule(head, body)

        return False

    def evalShape(self, state, s, depth):
        self.evalConstraints(state, s)
        state.evaluatedPredicates.update(s.queriesIds)
        state.visitedShapes.add(s)

        self.saturate(state, depth, s)

    def evalConstraints(self, state, s):
        self.evalQuery(state, s.minQuery, s)

        for q in s.maxQueries:
            self.evalQuery(state, q, s)

    def evalQuery(self, state, q, s):
        eval = self.endpoint.runQuery(q.getId(), q.getSparql(), "JSON")
        bindings = eval["results"]["bindings"]
        count = 0
        start = time.time()
        for b in bindings:
            self.evalBindingSet(state, b, q.getRulePattern(), s.rulePatterns)
            count += 1
        end = time.time()
        print("Rule maps runtime: ", end - start, " - Bindings count:", count)

    def evalBindingSet(self, state, bs, queryRP, shapeRPs):
        self._evalBindingSet(state, bs, queryRP)
        for p in shapeRPs:
            self._evalBindingSet(state, bs, p)


    def _evalBindingSet(self, state, bs, pattern):
        bindingVars = list(bs.keys())
        if all(elem in bindingVars for elem in pattern.getVariables()):
            state.ruleMap.addRule(
                    pattern.instantiateAtom(pattern.getHead(), bs),
                    pattern.instantiateBody(bs)
            )

    # This procedure derives negative information
    # For any (possibly negated) atom 'a' that is either a target or appears in some rule, we
    # may be able to infer that 'a' cannot hold:
    #   if 'a' is not in state.assignment
    #   if the query has already been evaluated,
    #   and if there is not rule with 'a' as its head.
    # Thus, in such case, 'not a' is added to state.assignment.
    def negateUnMatchableHeads(self, state, depth, s):
        ruleHeads = state.ruleMap.keySet()
        initialAssignmentSize = len(state.assignment)

        # first negate unmatchable body atoms (add not satisfied body atoms)
        state.assignment.update([self.getNegatedAtom(a).getStr() for a in state.ruleMap.getAllBodyAtoms()
                                 if not self.isSatisfiable(a, state, ruleHeads)])

        # then negate unmatchable targets
        part2 = dict()
        part2["true"] = [a for a in state.remainingTargets if self.isSatisfiable(a, state, ruleHeads)]
        part2["false"] = [a for a in state.remainingTargets if not self.isSatisfiable(a, state, ruleHeads)]

        inValidTargets = part2["false"]
        state.invalidTargets.update(inValidTargets)
        # register invalid target

        state.assignment.update([t.getNegation().getStr() for t in inValidTargets])  # (?)

        state.remainingTargets = set(part2["true"])

        return initialAssignmentSize != len(state.assignment)  # False when no new assignments

    def getNegatedAtom(self, a):
        return a.getNegation() if a.getIsPos() else a

    def isSatisfiable(self, a, state, ruleHeads):
        return (a.getPredicate() not in state.evaluatedPredicates) \
                or (a.getStr() in list(ruleHeads)) \
                or (a.getStr() in state.assignment)

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
