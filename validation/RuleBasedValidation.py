# -*- coding: utf-8 -*-
from validation.utils import fileManagement
from validation.utils.RuleBasedValidStats import RuleBasedValidStats
from validation.core.RuleMap import RuleMap
from validation.core.Literal import Literal
from validation.sparql.SPARQLPrefixHandler import getPrefixes
import time
import math
import re

class RuleBasedValidation:
    def __init__(self, endpoint, node_order, shapesDict, validOutput, violatedOutput, option, statsOutputFile, logOutput):
        self.endpoint = endpoint
        self.node_order = node_order
        self.shapesDict = shapesDict
        self.validOutput = validOutput
        self.violatedOutput = violatedOutput
        self.option = option
        self.targetShapes = self.extractTargetShapes()
        self.targetShapePredicates = [s.getId() for s in self.targetShapes]
        self.evaluatedShapes = []
        self.statsOutput = statsOutputFile
        self.stats = RuleBasedValidStats()
        self.logOutput = logOutput

    def exec(self):
        firstShapeEval = self.shapesDict[self.node_order.pop(0)]
        order = 0  # evaluation order
        self.logOutput.write("Retrieving (intitial) targets ...")
        targets = self.extractTargetAtoms(firstShapeEval, order)
        self.logOutput.write("\nTargets retrieved.")
        self.logOutput.write("\nNumber of targets:\n" + str(len(targets)))
        self.stats.recordInitialTargets(str(len(targets)))
        start = time.time()
        self.validate(
            order,
            EvalState(targets),
            firstShapeEval
        )
        finish = time.time()
        elapsed = finish - start
        self.stats.recordTotalTime(elapsed)
        print("Total execution time: ", str(elapsed))
        self.logOutput.write("\nMaximal number or rules in memory: " + str(self.stats.maxRuleNumber))
        self.stats.writeAll(self.statsOutput)

        fileManagement.closeFile(self.validOutput)
        fileManagement.closeFile(self.violatedOutput)
        fileManagement.closeFile(self.statsOutput)
        fileManagement.closeFile(self.logOutput)

    def extractTargetAtoms(self, shape, order):
        return self.targetAtoms(shape, shape.getTargetQuery(), order)

    # Run every time a new shape is going to be evaluated.
    # Uses filtered target query to get possible validated targets
    def getNewTargetAtoms(self, shape, targetQuery, orderNumber, state):
        targetLiterals = self.targetAtoms(shape, targetQuery, orderNumber, state)
        if targetLiterals == None:
            targetLiterals = []
        state.remainingTargets.update(targetLiterals)

    def getInstancesList(self, shape):
        for evShape in self.evaluatedShapes:
            prevEvalShapeName = evShape.id
            if shape.referencingShapes.get(prevEvalShapeName) is not None:
                # if there was a target query assigned for the referenced shape
                if self.shapesDict[prevEvalShapeName].targetQuery is not None:
                    validInstances = self.shapesDict[prevEvalShapeName].bindings
                    invalidInstances = self.shapesDict[prevEvalShapeName].invalidBindings
                    return validInstances, invalidInstances, prevEvalShapeName
        return [], [], None

    def getSplitList(self, shortestInstancesList, N):
        listLength = math.ceil(len(shortestInstancesList) / N)
        shortestInstancesList = list(shortestInstancesList)
        return [shortestInstancesList[i:i + listLength] for i in range(0, len(shortestInstancesList), listLength)]

    def filteredTargetQuery(self, shape, targetQuery, instanceType):
        valList, invList, prevEvalShapeName = self.getInstancesList(shape)

        print("INSTANCES *** case: ", instanceType, len(valList), len(invList), prevEvalShapeName, shape.id)
        if valList == invList:
            return targetQuery

        if len(valList) > len(invList):
            shortestInstancesList = invList
        else:
            shortestInstancesList = valList

        if instanceType == "valid":
            if len(invList) == 0:
                return targetQuery
            if len(shortestInstancesList) == 0:
                shape.hasValidInstances = False
                return None

            maxListLength = 130
            chunks = len(shortestInstancesList) / maxListLength
            N = math.ceil(chunks)
            queries = []
            splitLists = self.getSplitList(shortestInstancesList, N)
            if chunks > 1:
                for i in range(0, N):
                    subList = splitLists[i]
                    instances = " ".join(subList)
                    queryTemplate = shape.referencingQueriesPos[prevEvalShapeName].getSparql()
                    queries.append(queryTemplate.replace("$to_be_replaced$", instances))
                return queries
            else:
                instances = " ".join(shortestInstancesList)
                queryTemplate = shape.referencingQueriesPos[prevEvalShapeName].getSparql()
                return queryTemplate.replace("$to_be_replaced$", instances)

        elif instanceType == "invalid":
            if len(shortestInstancesList) == 0:
                return None

            maxListLength = 120
            chunks = len(shortestInstancesList) / maxListLength
            N = math.ceil(chunks)
            queries = []
            splitLists = self.getSplitList(shortestInstancesList, N)
            if chunks > 1:
                for i in range(0, N):
                    subList = splitLists[i]
                    print(">>>" + shape.getId() + " sublist length:", len(subList))
                    instances = ", ".join(subList)
                    queryTemplate = shape.referencingQueriesNeg[prevEvalShapeName].getSparql()
                    queries.append(queryTemplate.replace("$to_be_replaced$", instances))
                return queries
            else:
                instances = ", ".join(shortestInstancesList)
                queryTemplate = shape.referencingQueriesNeg[prevEvalShapeName].getSparql()
                return queryTemplate.replace("$to_be_replaced$", instances)

    # Automatically sets the instanciated targets as invalid after running the query which uses
    # instances from previous shape evaluation as a filter
    def invalidTargetAtoms(self, shape, targetQuery, instanceType, depth, state):
        query = self.filteredTargetQuery(shape, targetQuery, instanceType)
        if query is None:
            return
        elif isinstance(query, str):
            self.logOutput.write("\n\nEvaluating query:\n" + query)
            start = time.time()
            eval = self.endpoint.runQuery(
                shape.getId(),
                query,
                "JSON"
            )
            bindings = eval["results"]["bindings"]
            state.invalidTargets.update([self.registerTarget(Literal(shape.getId(), b["x"]["value"], True),
                                                             False, depth, "", shape)
                                        for b in bindings])
            end = time.time()
            print("############################################################")
            print(">>>", shape.getId(), "evaluation time single FILTER: ", end - start)
            print("############################################################")
        else:  # list of queries
            bindings = set()
            for q in query:
                self.logOutput.write("\n\nEvaluating query:\n" + q)
                start = time.time()
                eval = self.endpoint.runQuery(
                    shape.getId(),
                    q,
                    "JSON"
                )

                currentBindings = eval["results"]["bindings"]
                atoms = [Literal(shape.getId(), b["x"]["value"], True) for b in currentBindings]
                bindings.intersection(atoms)
                end = time.time()
                print("############################################################")
                print(">>>", shape.getId(), "evaluation time mult FILTER: ", end - start)
                print("############################################################")
            state.invalidTargets.update([self.registerTarget(b,
                                                             False, depth, "", shape)
                                         for b in bindings])


    def targetAtoms(self, shape, targetQuery, depth, state=None):
        if depth == 0:  # base case (corresponds to the first shape being evaluated)
            query = targetQuery  # initial targetQuery set in initial shape (json file)
        else:
            if self.option == "violated" or self.option == "all":
                self.invalidTargetAtoms(shape, targetQuery, "invalid", depth, state)

            query = self.filteredTargetQuery(shape, targetQuery, "valid")
            if query is None:
                return
            elif isinstance(query, list):
                bindings = set()
                for q in query:
                    self.logOutput.write("\nEvaluating query:\n" + q)
                    start = time.time()
                    eval = self.endpoint.runQuery(
                        shape.getId(),
                        q,
                        "JSON"
                    )
                    currentBindings = eval["results"]["bindings"]
                    atoms = [Literal(shape.getId(), b["x"]["value"], True) for b in currentBindings]
                    bindings.update(atoms)
                    end = time.time()
                    print("############################################################")
                    print(">>> valid evaluation time mult VALUES keyword:", shape.getId(), end - start)
                    print("############################################################")
                targetLiterals = bindings
                return targetLiterals
            elif isinstance(query, str):
                self.logOutput.write("\nEvaluating query:\n" + query)

        start = time.time()
        eval = self.endpoint.runQuery(
            shape.getId(),
            query,
            "JSON"
        )

        bindings = eval["results"]["bindings"]
        targetLiterals = [Literal(shape.getId(), b["x"]["value"], True) for b in bindings]
        end = time.time()
        print("############################################################")
        print(">>> valid evaluation time single VALUES keyword:", shape.getId(), end - start)
        print("############################################################")
        return targetLiterals

    def extractTargetShapes(self):
        return [s for name, s in self.shapesDict.items() if self.shapesDict[name].getTargetQuery() is not None]


    def validate(self, depth, state, focusShape):  # Algorithm 1 modified (SHACL2SPARQL)
        # termination condition 1: all targets are validated/violated
        #if len(state.remainingTargets) == 0:
        #    return

        # termination condition 2: all shapes have been visited
        if len(state.visitedShapes) == len(self.shapesDict):
            if self.option == "valid" or self.option == "all":
                for t in state.remainingTargets:
                    self.registerTarget(t, True, depth, "not violated after termination", None)
            return

        self.logOutput.write("\n\n*************************************************")
        self.logOutput.write("\nStarting validation at depth: " + str(depth))

        self.evalShape(state, focusShape, depth)  # validate selected shape

        self.currentEvalShape = self.shapesDict[self.node_order.pop(0)] if len(self.node_order) > 0 else None
        if self.currentEvalShape is not None:
            self.evaluatedShapes.append(focusShape)
            self.getNewTargetAtoms(self.currentEvalShape, self.currentEvalShape.targetQuery, depth + 1, state)
        self.validate(depth + 1, state, self.currentEvalShape)

    def registerTarget(self, t, isValid, depth, logMessage, focusShape):
        fshape = ", focus shape " + focusShape.id if focusShape is not None else ""
        log = t.getStr() + ", depth " + str(depth) + fshape + ", " + logMessage + "\n"

        instance = "<" + t.getArg() + ">"
        #for key, value in getPrefixes().items():  # for using prefix notation in the instances of the query
        #    value = value[1:-1]
        #    if value in t.getArg():
        #        instance = instance.replace(value, key + ":")[1:-1]

        if isValid:
            self.shapesDict[t.getPredicate()].bindings.add(instance)
            if self.option == "valid" or self.option == "all":
                self.validOutput.write(log)
        else:
            self.shapesDict[t.getPredicate()].invalidBindings.add(instance)
            if self.option == "violated" or self.option == "all":
                self.violatedOutput.write(log)

    def saturate(self, state, depth, s):
        startN = time.time()
        negated = self.negateUnMatchableHeads(state, depth, s)
        endN = time.time()
        print("############################################################")
        print(">>> Time negated", s.getId(), "depth", depth, ": ", endN - startN)
        print("############################################################")
        startI = time.time()
        inferred = self.applyRules(state, depth, s)
        endI = time.time()
        print("############################################################")
        print(">>> Time inferred", s.getId(), "depth", depth, ": ", endI - startI)
        print("############################################################")
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

        for t in part2["true"]:
            self.registerTarget(t, True, depth, "", s)
        for t in part2["false"]:
            self.registerTarget(t, False, depth, "", s)

        #print("Remaining targets: " + str(len(state.remainingTargets)))
        self.logOutput.write("\nRemaining targets: " + str(len(state.remainingTargets)))
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
        self.logOutput.write("\nEvaluating queries for shape " + s.getId())
        state.visitedShapes.add(s)
        self.saveRuleNumber(state)
        if s.hasValidInstances:
            startQuery = time.time()
            self.evalConstraints(state, s)
            endQuery = time.time()
            print("############################################################")
            print(">>> Time eval all subqueries", s.getId(), endQuery - startQuery)
            print("############################################################")
            state.evaluatedPredicates.update(s.queriesIds)
            self.logOutput.write("\nStarting saturation ...")
            startS = time.time()
            self.saturate(state, depth, s)
            endS = time.time()
            self.stats.recordSaturationTime(endS - startS)
            print("############################################################")
            print(">>> Total time saturation", endS - startS)
            print("############################################################")
            self.logOutput.write("\nSaturation time: " + str(endS - startS) + " seconds")

            self.logOutput.write("\n\nValid targets: " + str(len(state.validTargets)))
            self.logOutput.write("\nInvalid targets: " + str(len(state.invalidTargets)))
            self.logOutput.write("\nRemaining targets: " + str(len(state.remainingTargets)))

    def saveRuleNumber(self, state):
        ruleNumber = state.ruleMap.getRuleNumber()
        self.logOutput.write("\nNumber of rules: " + str(ruleNumber))
        self.stats.recordNumberOfRules(ruleNumber)

    def evalConstraints(self, state, s):
        self.evalQuery(state, s.minQuery, s)

        for q in s.maxQueries:
            self.evalQuery(state, q, s)

    def evalQuery(self, state, q, s):
        self.logOutput.write("\n\nEvaluating query:\n" + q.getSparql())
        startQ = time.time()
        eval = self.endpoint.runQuery(q.getId(), q.getSparql(), "JSON")
        endQ = time.time()
        bindings = eval["results"]["bindings"]
        self.stats.recordQueryExecTime(endQ - startQ)
        self.logOutput.write("\nNumber of solution mappings: " + str(len(bindings)))
        self.stats.recordNumberOfSolutionMappings(len(bindings))
        self.stats.recordQuery()
        self.logOutput.write("\nGrounding rules ... ")
        startG = time.time()
        count = 0
        for b in bindings:
            self.evalBindingSet(state, b, q.getRulePattern(), s.rulePatterns)
            count += 1
        endG = time.time()
        #print("Bindings count:", count)
        self.stats.recordGroundingTime(endG - startG)
        self.logOutput.write(str(endG - startG) + " seconds")

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

        for t in inValidTargets:
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
    def __init__(self, targetLiterals):
        self.remainingTargets = targetLiterals
        self.ruleMap = RuleMap()
        self.assignment = set()
        self.visitedShapes = set()
        self.evaluatedPredicates = set()
        self.validTargets = set()
        self.invalidTargets = set()
