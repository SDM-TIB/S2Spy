# -*- coding: utf-8 -*-
import re
from validation.ASKQuery import ASKQuery

class ShapeImpl:

    def __init__(self, id, targetDef, targetQuery, disjuncts):
        self.id = id
        self.targetDef = targetDef.get("query") if targetDef != None else None
        self.targetQuery = targetQuery
        self.disjuncts = disjuncts  # conjunctions
        self.rulePatterns = ()
        self.predicates = ()

        self.computePredicateSet()

        # e.g., [ActorShape, ActorShape_d1, ActorShape_d1_pos]
        # e.g., [MovieShape, MovieShape_d1, MovieShape_d1_pos, MovieShape_d1_max_1]

    def getId(self):
        return self.id

    def computePredicateSet(self):
        disjuncts = [d.getPredicates() for d in self.disjuncts]
        predicates = [self.id] + disjuncts[0]
        return predicates

    def getPosShapeRefs(self):
        return [d.getPosShapeRefs() for d in self.disjuncts]

    def getNegShapeRefs(self):
        return [d.getNegShapeRefs() for d in self.disjuncts]

    def askViolations(self):
        if self.targetDef != None:  # not checking violations on shapes without target definitions
            triple = re.findall(r'{.*}', self.targetDef)[0]  # *** considering only one target def
            triple = triple[1:len(triple)-1]  # removed curly braces
            triple = triple.strip().split()
            target = triple[2]

            minConstraints = self.disjuncts[0].minConstraints
            for c in minConstraints:
                c.violated = ASKQuery(c.path, target).evaluate("min", c.min)

            maxConstraints = self.disjuncts[0].maxConstraints
            for c in maxConstraints:
                c.violated = ASKQuery(c.path, target).evaluate("max", c.max)
