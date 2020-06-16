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
        self.evalOption = option
        self.targetShapes = self.extractTargetShapes()
        self.targetShapePredicates = [s.getId() for s in self.targetShapes]
        self.evaluatedShapes = []  # used for the filtering queries
        self.stats = RuleBasedValidStats()
        self.statsOutput = statsOutputFile
        self.logOutput = logOutput

        self.prevEvalShapeName = None

    def exec(self):
        firstShapeEval = self.shapesDict[self.node_order.pop(0)]
        depth = 0  # evaluation order
        self.logOutput.write("Retrieving (initial) targets ...")
        targets = self.extractInitialTargetAtoms(firstShapeEval, depth)
        self.logOutput.write("\nTargets retrieved.")
        self.logOutput.write("\nNumber of targets:\n" + str(len(targets)))
        self.stats.recordInitialTargets(str(len(targets)))
        start = time.time()
        self.validate(
            depth,
            EvalState(targets),
            firstShapeEval
        )
        finish = time.time()
        elapsed = finish - start
        self.stats.recordTotalTime(elapsed)
        print("Total execution time: ", str(elapsed))
        self.logOutput.write("\nMaximal (initial) number or rules in memory: " + str(self.stats.maxRuleNumber))
        self.stats.writeAll(self.statsOutput)

        fileManagement.closeFile(self.validOutput)
        fileManagement.closeFile(self.violatedOutput)
        fileManagement.closeFile(self.statsOutput)
        fileManagement.closeFile(self.logOutput)

    def getInstancesList(self, shape):
        for evShape in self.evaluatedShapes:
            prevEvalShapeName = evShape.id
            if shape.referencingShapes.get(prevEvalShapeName) is not None:
                # if there was a target query assigned for the referenced shape
                if self.shapesDict[prevEvalShapeName].targetQuery is not None:
                    self.prevEvalShapeName = prevEvalShapeName
                    prevValidInstances = self.shapesDict[prevEvalShapeName].bindings
                    prevInvalidInstances = self.shapesDict[prevEvalShapeName].invalidBindings
                    return prevValidInstances, prevInvalidInstances, prevEvalShapeName
        return [], [], None

    def getSplitList(self, shortestInstancesList, N):
        listLength = math.ceil(len(shortestInstancesList) / N)
        shortestInstancesList = list(shortestInstancesList)
        return [shortestInstancesList[i:i + listLength] for i in range(0, len(shortestInstancesList), listLength)]

    # Retrieves already formatted list or lists or valid/invalid instances of previous shape
    def getFormattedInstances(self, instances, separator, maxListLength):
        chunks = len(instances) / maxListLength
        N = math.ceil(chunks)
        if chunks > 1:
            splitLists = self.getSplitList(instances, N)
            return [separator.join(subList) for subList in splitLists]
        else:
            return [separator.join(instances)]

    def filteredQuery(self, queryTemplate, instancesList, separator, maxListLength):
        formattedInstancesLists = self.getFormattedInstances(instancesList, separator, maxListLength)
        return [queryTemplate.replace("$to_be_replaced$", sublist) for sublist in formattedInstancesLists]

    def filteredTargetQuery(self, shape, targetQuery, bindingsType, valList, invList, prevEvalShapeName):
        print("INSTANCES *** case: ", bindingsType, len(valList), len(invList), prevEvalShapeName, shape.id)
        if valList == invList:
            return [targetQuery]

        shortestInstancesList = valList if len(valList) < len(invList) else invList
        maxSplitNumber = shape.maxSplitSize  # heuristic of maximum possible number of instances considered to allow using filtering queries instead of initial target query
        maxInstancesPerQuery = 115 # number from which the list is going to start being split because of the max number of characters allowed in a query

        if bindingsType == "valid":
            if len(invList) == 0 or len(shortestInstancesList) > maxSplitNumber:
                return [targetQuery]
            elif len(valList) == 0:
                shape.hasValidInstances = False
                return None  # no query to be evaluated since no new possible target literals to be found

            if shortestInstancesList == valList:
                queryTemplate = shape.referencingQueries_VALUES[prevEvalShapeName].getSparql()
                separator = " "
            else:
                queryTemplate = shape.referencingQueries_FILTER_NOT_IN[prevEvalShapeName].getSparql()
                separator = ","

            return self.filteredQuery(queryTemplate, shortestInstancesList, separator, maxInstancesPerQuery)

        elif bindingsType == "invalid":
            if len(valList) == 0 or len(shortestInstancesList) > maxSplitNumber:
                return [targetQuery]  # retrieve all possible instances and register them as invalid without verifying
                                      # whether the others constraints of the shape are satisfied or not
            elif len(invList) == 0:
                return None

            if shortestInstancesList == invList:
                queryTemplate = shape.referencingQueries_VALUES[prevEvalShapeName].getSparql()
                separator = " "
            else:
                queryTemplate = shape.referencingQueries_FILTER_NOT_IN[prevEvalShapeName].getSparql()
                separator = ","

            return self.filteredQuery(queryTemplate, shortestInstancesList, separator, maxInstancesPerQuery)

    def validTargetAtoms(self, shape, targetQuery, bType, prevValList, prevInvList, prevEvalShapename):
        query = self.filteredTargetQuery(shape, targetQuery, bType, prevValList, prevInvList, prevEvalShapename)
        # when the lists are not split, the variable 'query' returns an array with one single query

        if query is None:
            print("(NO NEEDED QUERY FOR THE CURRENT CASE).")
            return []  # no target atoms / literals retrieved
        else:
            targetLiterals = set()
            for q in query:
                bindings = self.evalTargetQuery(shape, q)
                targetLiterals.union([Literal(shape.getId(), b["x"]["value"], True) for b in bindings])
            return targetLiterals

    # Automatically sets the instanciated targets as invalid after running the query which uses
    # instances from previous shape evaluation as a filter
    def invalidTargetAtoms(self, shape, targetQuery, bType, prevValList, prevInvList, prevEvalShapeName, depth, state):
        query = self.filteredTargetQuery(shape, targetQuery, bType, prevValList, prevInvList, prevEvalShapeName)
        if query is None:
            print("(NO NEEDED QUERY FOR THE CURRENT CASE).")
        else:
            invalidBindings = set()
            qn = 0
            for q in query:
                bindings = self.evalTargetQuery(shape, q)
                print("^^^^^ bindings:", len(bindings))
                if qn == 0:
                    # update empty set
                    invalidBindings.union([Literal(shape.getId(), b["x"]["value"], True) for b in bindings])
                    qn += 1
                else:
                    invalidBindings.intersection([Literal(shape.getId(), b["x"]["value"], True) for b in bindings])
            print("invalidating...", len(invalidBindings))
            state.invalidTargets.update(invalidBindings)
            for b in invalidBindings:
                self.registerTarget(b, False, depth, "", shape)

    # Extracts target atom from first evaluated shape
    def extractInitialTargetAtoms(self, shape, order):
        return self.targetAtoms(shape, shape.getTargetQuery(), order)

    # Runs every time a new shape is going to be evaluated.
    # May use filter queries based on previously valid/invalid targets
    def extractNextTargetAtoms(self, shape, targetQuery, orderNumber, state):
        targetLiterals = self.targetAtoms(shape, targetQuery, orderNumber, state)
        state.remainingTargets.update(targetLiterals)

    def evalTargetQuery(self, shape, query):
        self.logOutput.write("\nEvaluating query:\n" + query)
        start = time.time()
        eval = self.endpoint.runQuery(
            shape.getId(),
            query,
            "JSON"
        )
        end = time.time()
        print("############################################################")
        print(">>> Time eval target query", shape.getId(), end - start)
        print("############################################################")
        return eval["results"]["bindings"]

    # Returns bindings obtained from the evaluation of the endpoint
    def targetAtoms(self, shape, targetQuery, depth, state=None):
        prevValList, prevInvList, prevEvalShapeName = self.getInstancesList(shape)
        if depth == 0 or prevEvalShapeName is None:  # base case (corresponds to the first shape being evaluated)
            query = targetQuery  # initial targetQuery set in shape file (json file)

            bindings = self.evalTargetQuery(shape, query)
            return [Literal(shape.getId(), b["x"]["value"], True) for b in bindings]  # target literals
        else:
            atoms = self.validTargetAtoms(shape, targetQuery, "valid", prevValList, prevInvList, prevEvalShapeName)

            if self.evalOption == "violated" or self.evalOption == "all":
                self.invalidTargetAtoms(shape, targetQuery, "invalid", prevValList, prevInvList, prevEvalShapeName,
                                        depth, state)

            return atoms

    def extractTargetShapes(self):
        return [s for name, s in self.shapesDict.items() if self.shapesDict[name].getTargetQuery() is not None]

    def validate(self, depth, state, focusShape):  # Algorithm 1 modified (SHACL2SPARQL)
        # termination condition 1: all targets are validated/violated  # does not apply anymore since we do not
        #if len(state.remainingTargets) == 0:                          # get all possible initial targets (considering
        #    return                                                    # all shapes of the network) from the beginning

        # termination condition 2: all shapes have been visited
        if len(state.visitedShapes) == len(self.shapesDict):
            if self.evalOption == "valid" or self.evalOption == "all":
                for t in state.remainingTargets:
                    self.registerTarget(t, True, depth, "not violated after termination", None)
            return

        self.logOutput.write("\n\n*************************************************")
        self.logOutput.write("\nStarting validation at depth: " + str(depth))

        self.validateFocusShape(state, focusShape, depth)

        # select next shape to be evaluated from the already defined list with the evaluation order
        self.nextEvalShape = self.shapesDict[self.node_order.pop(0)] if len(self.node_order) > 0 else None
        if self.nextEvalShape is not None:
            self.evaluatedShapes.append(focusShape)
            self.logOutput.write("\n\n*************************************************************************")
            self.logOutput.write("\n*************************************************")
            self.logOutput.write("\nRetrieving (next) targets ...")
            self.prevEvalShapeName = None  # reset previous value
            self.extractNextTargetAtoms(self.nextEvalShape, self.nextEvalShape.targetQuery, depth + 1, state)

        self.validate(depth + 1, state, self.nextEvalShape)

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
            if self.evalOption == "valid" or self.evalOption == "all":
                self.validOutput.write(log)
        else:
            self.shapesDict[t.getPredicate()].invalidBindings.add(instance)
            if self.evalOption == "violated" or self.evalOption == "all":
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
        #print("############################################################")
        print(">>> Time inferred", s.getId(), "depth", depth, ": ", endI - startI)
        #print("############################################################")
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

    def validateFocusShape(self, state, focusShape, depth):
        self.evalShape(state, focusShape, depth)  # validate current selected shape

    def evalShape(self, state, s, depth):
        self.logOutput.write("\nEvaluating queries for shape " + s.getId())

        if s.hasValidInstances:             # if the current shape is connected in the network as a parent to a shape
            startQ = time.time()            # that was already evaluated and has any valid instances, then saturate
            self.evalConstraints(state, s)  # 'eval Disjunct'
            endQ = time.time()
            print("############################################################")
            print(">>> Time eval all subqueries", s.getId(), endQ - startQ)
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

        state.addVisitedShape(s)
        self.saveRuleNumber(state)

        self.logOutput.write("\n\nValid targets: " + str(len(state.validTargets)))
        self.logOutput.write("\nInvalid targets: " + str(len(state.invalidTargets)))
        self.logOutput.write("\nRemaining targets: " + str(len(state.remainingTargets)))

    def saveRuleNumber(self, state):
        ruleNumber = state.ruleMap.getRuleNumber()
        self.logOutput.write("\nNumber of rules: " + str(ruleNumber))
        self.stats.recordNumberOfRules(ruleNumber)

    def filteredMinQuery(self, shape, templateQuery, prevValidInstances, prevInvalidInstances,
                         maxSplitNumber, maxInstancesPerQuery):
        if self.prevEvalShapeName is not None \
                and len(prevValidInstances) > 0 and len(prevInvalidInstances) > 0 \
                and len(prevValidInstances) <= maxSplitNumber:
            VALUES_clauses = ""
            instancesLists = self.getFormattedInstances(prevValidInstances, "", maxInstancesPerQuery)
            for c in shape.constraints:
                if c.shapeRef == self.prevEvalShapeName:
                    var = " ?" + c.variables[0]
                    VALUES_clauses += "VALUES" + var + " {$instances$}\n"
            queries = []
            for sublist in instancesLists:
                queries.append(templateQuery.replace("$to_be_replaced$", VALUES_clauses.replace("$instances$", sublist)))
            return queries

        return templateQuery.replace("$to_be_replaced$", "\n")

    def filteredMaxQuery(self, shape, templateQuery, prevValidInstances, prevInvalidInstances,
                         maxSplitNumber, maxInstancesPerQuery):
        if self.prevEvalShapeName is not None \
                and len(prevValidInstances) > 0 and len(prevInvalidInstances) > 0 \
                and len(prevValidInstances) <= maxSplitNumber:
            VALUES_clauses = ""
            refPaths = "\n"
            instancesLists = self.getFormattedInstances(prevValidInstances, "", maxInstancesPerQuery)
            for c in shape.constraints:
                if c.shapeRef == self.prevEvalShapeName:
                    var = " ?" + c.variables[0]
                    focusVar = c.varGenerator.getFocusNodeVar()
                    VALUES_clauses += "VALUES" + var + " {$instances$}\n"
                    refPaths += "?" + focusVar + " " + c.path + var + ".\n"
            queries = []
            for sublist in instancesLists:
                queries.append(templateQuery.replace("$to_be_replaced$",
                                                     VALUES_clauses.replace("$instances$", sublist) + refPaths))
            return queries

        return templateQuery.replace("$to_be_replaced$", "\n")

    def evalConstraints(self, state, s):
        valInst = self.shapesDict[self.prevEvalShapeName].bindings if self.prevEvalShapeName is not None else []
        invInst = self.shapesDict[self.prevEvalShapeName].invalidBindings if self.prevEvalShapeName is not None else []

        print("------------------------------------------------------------")
        maxSplitNumber = s.maxSplitSize
        maxInstancesPerQuery = 80
        minQuery = self.filteredMinQuery(s, s.minQuery.getSparql(), valInst, invInst, maxSplitNumber, maxInstancesPerQuery)
        if isinstance(minQuery, list):
            for query in minQuery:
                self.evalQuery(state, s.minQuery, query, s)
        else:
            self.evalQuery(state, s.minQuery, minQuery, s)
        print(">>> Finished time eval MIN constraint", s.getId(), "<<<")
        print("------------------------------------------------------------")

        for q in s.maxQueries:
            print("------------------------------------------------------------")
            maxQuery = self.filteredMaxQuery(s, q.getSparql(), valInst, invInst, maxSplitNumber, maxInstancesPerQuery)
            if isinstance(maxQuery, list):
                for queryStr in maxQuery:
                    self.evalQuery(state, q, queryStr, s)
            else:
                self.evalQuery(state, q, maxQuery, s)
            print(">>> Finished time eval MAX constraint", s.getId(), "<<<")
            print("------------------------------------------------------------")

    def evalQuery(self, state, q, query, s):
        self.logOutput.write("\n\nEvaluating query:\n" + query)
        startQ = time.time()
        eval = self.endpoint.runQuery(q.getId(), query, "JSON")
        endQ = time.time()
        print(">>> Time retrieving from endpoint:", endQ - startQ)
        self.stats.recordQueryExecTime(endQ - startQ)

        bindings = eval["results"]["bindings"]  # list of obtained 'bindingsSet' from the endpoint

        self.logOutput.write("\nNumber of solution mappings: " + str(len(bindings)))
        self.stats.recordNumberOfSolutionMappings(len(bindings))
        self.stats.recordQuery()
        self.logOutput.write("\nGrounding rules ... ")
        startG = time.time()
        for b in bindings:
            self.evalBindingSet(state, b, q.getRulePattern(), s.rulePatterns)
        endG = time.time()
        print(">>> Time grounding:", endG - startG)
        self.stats.recordGroundingTime(endG - startG)
        self.logOutput.write(str(endG - startG) + " seconds")

    def evalBindingSet(self, state, bs, queryRP, shapeRPs):
        bindingVars = bs.keys()
        self._evalBindingSet(state, bs, queryRP, bindingVars)
        for p in shapeRPs:  # for each pattern in the set of rule patterns
            self._evalBindingSet(state, bs, p, bindingVars)

    def _evalBindingSet(self, state, bs, pattern, bindingVars):
        if all(elem in bindingVars for elem in pattern.getVariables()):
            state.ruleMap.addRule(
                pattern.instantiateAtom(pattern.getHead(), bs),
                pattern.instantiateBody(bs)
            )

    def negateUnMatchableHeads(self, state, depth, s):
        '''
        This procedure derives negative information
        For any (possibly negated) atom 'a' that is either a target or appears in some rule, we
        may be able to infer that 'a' cannot hold:
          if 'a' is not in state.assignment
          if the query has already been evaluated,
          and if there is not rule with 'a' as its head.
        Thus, in such case, 'not a' is added to state.assignment.

        :param state:
        :param depth:
        :param s:
        :return:
        '''
        ruleHeads = state.ruleMap.keySet()

        initialAssignmentSize = len(state.assignment)

        # first negate unmatchable body atoms (add not satisfied body atoms)
        state.assignment.update(list({self.getNegatedAtom(a).getStr()
                                      for a in state.ruleMap.getAllBodyAtoms()
                                      if not self.isSatisfiable(a, state, ruleHeads)}
                                     )
                                )

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

        state.assignment.update([t.getNegation().getStr() for t in inValidTargets])

        state.remainingTargets = set(part2["true"])

        return initialAssignmentSize != len(state.assignment)  # False when no new assignments are found

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

    def addVisitedShape(self, s):
        self.visitedShapes.add(s)
