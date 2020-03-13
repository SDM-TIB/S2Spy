# -*- coding: utf-8 -*-
__author__ = "Philipp D. Rohde and Monica Figuera"

import re
from validation.sparql.ASKQuery import ASKQuery
from validation.VariableGenerator import VariableGenerator
from validation.core.Literal import Literal
from validation.core.RulePattern import RulePattern
from validation.utils.SourceDescription import SourceDescription


class Shape:

    def __init__(self, id, targetDef, targetQuery, constraints):
        self.id = id
        self.constraints = constraints
        self.predicates = self.computePredicateSet()
        self.targetDef = targetDef if targetDef is not None else self.computeTargetDef()
        self.targetQuery = targetQuery  # Might be None
        self.rulePatterns = ()
        self.satisfied = None
        self.inDegree = None
        self.outDegree = None

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
        return targets

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

#    def computeConstraintQueries(self, schema, graph):
#        for c in self.disjuncts:
#            c.computeQueries(graph)
#
#        self.rulePatterns = self.computeRulePatterns()

#    def computeRulePatterns(self):
#        focusNodeVar = VariableGenerator.getFocusNodeVar()
#        head = Literal(self.id, focusNodeVar, True)
#
#        return [RulePattern(head, self.getDisjunctRPBody(d)) for d in self.disjuncts]

#    def getDisjunctRPBody(self, d):
#        focusNodeVar = VariableGenerator.getFocusNodeVar()
#        maxQueries = [Literal(s, focusNodeVar, False) for s in [q.getId() for q in d.getMaxQueries()]]
#
#        return [Literal(d.getMinQuery().getId(),
#                        focusNodeVar,
#                        True
#                        )] + \
#            maxQueries
