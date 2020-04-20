# -*- coding: utf-8 -*-
from validation.utils import fileManagement
from validation.EvalPath import EvalPath
from validation.core.RuleMap import RuleMap
from validation.core.Literal import Literal
import time
import re

class RuleBasedValidation:
    def __init__(self, endpoint, node_order, shapesDict, validOutput=None, violatedOutput=None):
        self.endpoint = endpoint
        self.node_order = node_order
        self.shapesDict = shapesDict
        self.validOutput = validOutput
        self.violatedOutput = violatedOutput
        targetShapes = self.extractTargetShapes()
        self.targetShapePredicates = [s.getId() for s in targetShapes]
        self.option = "valid"

    def exec(self, option):
        firstShapeEval = self.shapesDict[self.node_order.pop(0)]
        targets = self.extractTargetAtoms(firstShapeEval)
        evalPathsMap = {firstShapeEval.id: EvalPath()}
        self.option = option

        self.validate(
            0,
            EvalState(
                targets,
                evalPathsMap
            ),
            firstShapeEval
        )

        fileManagement.closeFile(self.validOutput)
        fileManagement.closeFile(self.violatedOutput)

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

    def extractTargetShapes(self):
        return [s for name, s in self.shapesDict.items() if self.shapesDict[name].getTargetQuery() is not None]


    def validate(self, depth, state, focusShape):  # Algorithm 1 modified (SHACL2SPARQL)
        # termination condition 1: all targets are validated/violated
        if len(state.remainingTargets) == 0:
            return

        # termination condition 2: all shapes have been visited
        if len(state.visitedShapes) == len(self.shapesDict):  # this condition is never fulfilled ***
            if self.option == "valid":
                for t in state.remainingTargets:
                    self.registerTarget(t, True, depth, "not violated after termination", None)
            return

        self.evalShape(state, focusShape, depth)  # validate selected shape

        self.currentEvalShape = self.shapesDict[self.node_order.pop(0)] if len(self.node_order) > 0 else None
        self.validate(depth + 1, state, self.currentEvalShape)

    def registerTarget(self, t, isValid, depth, logMessage, focusShape):
        fshape = ", focus shape " + focusShape.id if focusShape is not None else ""
        log = t.getStr() + ", depth " + str(depth) + fshape + ", " + logMessage + "\n"
        if isValid:
            self.validOutput.write(log)
        else:
            self.violatedOutput.write(log)

    def saturate(self, state, depth, s):
        negated = self.negateUnMatchableHeads(state, depth, s)
        inferred = self.applyRules(state, depth, s)
        if negated or inferred:
            self.saturate(state, depth, s)

    def getStrPredicate(self, a):
        pred = re.split("\(", a, 1)[0]
        pred = re.split("!", pred)[0]
        return pred

    # INFER procedure performs 2 types of inferences:
    # 1. If the set of rules contains a rule and each of the rule bodies has already been inferred
    #    => head of the rule is inferred, rule dropped.
    # 2. If the negation of any rule body has already been inferred
    #    => this rule cannot be applied (rule head not inferred) so the entire entire rule is dropped.
    def applyRules(self, state, depth, s):
        retainedRules = RuleMap()                                                               # (2)
        freshLiterals = list(filter(lambda rule: rule is not None,                              # (4)
                                    [self._applyRules(head, bodies, state, retainedRules)
                                     for head, bodies in state.ruleMap.map.items()])            # (3)
                             )

        state.ruleMap = retainedRules
        state.assignment.update(freshLiterals)

        if len(freshLiterals) == 0:
            return False

        candidateValidTargets = [a for a in freshLiterals if self.getStrPredicate(a) in self.targetShapePredicates]

        part1 = dict()
        part1["true"] = [t for t in state.remainingTargets if t.getStr() in candidateValidTargets]
        part1["false"] = [t for t in state.remainingTargets if t.getStr() not in candidateValidTargets]

        state.remainingTargets = part1["false"]

        part2 = dict()
        part2["true"] = [t for t in part1["true"] if t.getIsPos()]
        part2["false"] = [t for t in part1["true"] if not t.getIsPos()]

        state.validTargets.update(part2["true"])
        state.invalidTargets.update(part2["false"])

        if self.option == "valid":
            for t in part2["true"]:
                self.registerTarget(t, True, depth, "", s)
        elif self.option == "violated":
            for t in part2["false"]:
                self.registerTarget(t, False, depth, "", s)

        #print("Remaining targets: " + str(len(state.remainingTargets)))

        return True

    def _applyRules(self, head, bodies, state, retainedRules):
        tempRetainedBodies = []
        anyInvalidRule = list(filter(lambda rule: rule is True,
                                     [self.applyRule(head, b, state, tempRetainedBodies) for b in bodies]))
        if len(anyInvalidRule) > 0:  # if any invalid body rule
            return head
        else:
            for b in tempRetainedBodies:
                retainedRules.addRule(head, b)
        return None

    def applyRule(self, head, body, state, tempRetainedBodies):
        bodyStrMap = [elem.getStr() for elem in body]
        if set(bodyStrMap) <= state.assignment:  # invalid
            return True

        matches = [a.getNegation().getStr() for a in body if a.getNegation().getStr() in state.assignment]  # ***
        if len(matches) == 0:  # no match
            tempRetainedBodies.append(body)  # not invalid
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
        state.assignment.update(list({self.getNegatedAtom(a).getStr()
                                for a in state.ruleMap.getAllBodyAtoms()
                                if not self.isSatisfiable(a, state, ruleHeads)}))

        # then negate unmatchable targets
        part2 = dict()
        part2["true"] = []
        part2["false"] = []
        for a in state.remainingTargets:
            if self.isSatisfiable(a, state, ruleHeads):
                part2["true"].append(a)
            else:
                part2["false"].append(a)

        inValidTargets = part2["false"]
        state.invalidTargets.update(inValidTargets)

        if self.option == "violated":
            for t in state.invalidTargets:
                self.registerTarget(t, False, depth, "", s)

        state.assignment.update([t.getNegation().getStr() for t in inValidTargets])  # (?)

        state.remainingTargets = set(part2["true"])

        return initialAssignmentSize != len(state.assignment)  # False when no new assignments

    def getNegatedAtom(self, a):
        return a.getNegation() if a.getIsPos() else a

    def isSatisfiable(self, a, state, ruleHeads):
        notNegated = a.getStr()[1:] if not a.getIsPos() else a.getStr()
        return (a.getPredicate() not in state.evaluatedPredicates) \
                or (notNegated in ruleHeads) \
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
