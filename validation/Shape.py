# -*- coding: utf-8 -*-
__author__ = "Philipp D. Rohde and Monica Figuera"

import re
import itertools
from validation.sparql.ASKQuery import ASKQuery
from validation.VariableGenerator import VariableGenerator
from validation.core.Literal import Literal
from validation.core.RulePattern import RulePattern
from validation.utils.SourceDescription import SourceDescription
from validation.sparql.QueryGenerator import QueryGenerator

class Shape:

    def __init__(self, id, targetDef, targetQuery, constraints, constraintsId):
        self.id = id
        self.constraints = constraints
        self.constraintsId = constraintsId
        self.predicates = self.computePredicateSet()
        self.targetDef = targetDef if targetDef is not None else self.computeTargetDef()
        self.targetQuery = targetQuery  # Might be None
        self.rulePatterns = ()
        self.satisfied = None
        self.inDegree = None
        self.outDegree = None

        self.minQuery = ""
        self.maxQueries = ""

    def getId(self):
        return self.id

    def setDegree(self, inDegree, outDegree):
        self.inDegree = inDegree
        self.outDegree = outDegree

    def computePredicateSet(self):
        predicates = set()
        for c in self.constraints:
            pred = c.path
            if not pred.startswith("^"):
                predicates.add(pred)
        return predicates

    def computeTargetDef(self):
        targets = SourceDescription.instance.get_classes(self.predicates)
        for c in self.constraints:
            c.target = targets
        # fix: set target for constraints only (needed for the queries)
        # but not for the shape since it will interfere with the heuristics
        return None

#    def getPosShapeRefs(self):
#        return [d.getPosShapeRefs() for d in self.disjuncts]

#    def getNegShapeRefs(self):
#        return [d.getNegShapeRefs() for d in self.disjuncts]

#    def askViolations(self):
#        if self.targetDef is not None:  # not checking violations on shapes without target definitions
#            triple = re.findall(r'{.*}', self.targetDef)[0]  # *** considering only one target def
#            triple = triple[1:len(triple)-1]  # removed curly braces
#            triple = triple.strip().split()
#            target = triple[2]
#
#            minConstraints = self.disjuncts[0].minConstraints
#            for c in minConstraints:
#                c.violated = ASKQuery(c.path, target).evaluate("min", c.min)
#
#            maxConstraints = self.disjuncts[0].maxConstraints
#            for c in maxConstraints:
#                c.violated = ASKQuery(c.path, target).evaluate("max", c.max)

    def getTargetQuery(self):
        return self.targetQuery

    def getConstraints(self):
        return self.constraints

    def getShapeRefs(self):
        return [c.getShapeRef() for c in self.constraints if c.getShapeRef() is not None]

    def isSatisfied(self):
        if self.satisfied is None:
            for c in self.constraints:  # TODO: heuristics for the constraints within a shape?
                if not c.isSatisfied():
                    self.satisfied = False
                    return self.satisfied
            self.satisfied = True
        return self.satisfied

    def getValidInstances(self):
        return  # TODO

    def getViolations(self):
        return  # TODO

    def computeConstraintQueries(self):

        minConstraints = [c for c in self.constraints if c.min != -1]
        maxConstraints = [c for c in self.constraints if c.max != -1]
        queryGenerator = QueryGenerator()

        subquery = queryGenerator.generateLocalSubquery(None, minConstraints)

        # Build a unique set of triples (+ filter) for all min constraints
        minId = self.constraintsId + "_pos"
        self.minQuery = queryGenerator.generateQuery(
                minId,
                [c for c in minConstraints if c.getShapeRef() is not None],
                None,
                subquery
        )

        # Build one set of triples (+ filter) for each max constraint
        maxIds = [self.constraintsId + "_max_" + str(i) for i in range(1, len(maxConstraints) + 1)]
        i = itertools.count()
        self.maxQueries = [queryGenerator.generateQuery(
                                        maxIds[next(i)],
                                        [c],
                                        None,
                                        subquery) for c in maxConstraints]

        self.rulePatterns = self.computeRulePatterns()

    def computeRulePatterns(self):
        focusNodeVar = VariableGenerator.getFocusNodeVar()
        head = Literal(self.id, focusNodeVar, True)

        return [RulePattern(head, self.getDisjunctRPBody())]

    def getDisjunctRPBody(self):
        focusNodeVar = VariableGenerator.getFocusNodeVar()
        maxQueries = [Literal(s, focusNodeVar, False) for s in [q.getId() for q in self.maxQueries]]

        return [Literal(self.minQuery.id,
                        focusNodeVar,
                        True
                        )] + \
                maxQueries
