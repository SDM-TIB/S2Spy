# -*- coding: utf-8 -*-
class ShapeImpl:

    def __init__(self, id, targetQuery, disjuncts):
        self.id = id
        self.targetQuery = targetQuery
        self.disjuncts = disjuncts
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
