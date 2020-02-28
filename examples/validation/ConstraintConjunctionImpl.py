# -*- coding: utf-8 -*-
from validation.MaxOnlyConstraintImpl import MaxOnlyConstraintImpl

class ConstraintConjunctionImpl:

    def __init__(self, id, minConstraints, maxConstraints, localConstraints):
        self.id = id
        self.minConstraints = minConstraints
        self.maxConstraints = maxConstraints
        self.minQueryPredicate = id + "_pos"
        self.localConstraints = localConstraints
        self.maxQueryPredicates = []

        self.minQuery = None
        self.maxQueries = None

        self.maxQueryPredicates = [self.id + "_max_" + str(i) for i in range(1, len(self.maxConstraints) + 1)]

    @property
    def getId(self):
        return self.id

    @property
    def getMinQuery(self):
        return self.minQuery

    @property
    def getMaxQueries(self):
        return self.maxQueries

    def getPredicates(self):
        return [self.id, self.minQueryPredicate] + self.maxQueryPredicates

    def getPosShapeRefs(self):
        return self.getShapeRefs(True)

    def getNegShapeRefs(self):
        return self.getShapeRefs(False)

    def getShapeRefs(self, posRefs):
        filterCondidion = self.posRefFilter() if posRefs else self.negRefFilter()
        return [c.getShapeRef() for c in self.getConjuncts() if filterCondidion(c)]

    def posRefFilter(self):
        return lambda c : c.getShapeRef() != None and c.getIsPos() and not isinstance(c, MaxOnlyConstraintImpl)

    def negRefFilter(self):
        return lambda c : c.getShapeRef() != None and (not c.getIsPos() or isinstance(c, MaxOnlyConstraintImpl))

    def getConjuncts(self):
        return self.minConstraints + self.maxConstraints  # *** tbc