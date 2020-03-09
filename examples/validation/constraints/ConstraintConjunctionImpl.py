# -*- coding: utf-8 -*-
import itertools
from validation.constraints.MaxOnlyConstraintImpl import MaxOnlyConstraintImpl
from validation.sparql.QueryGenerator import QueryGenerator


class ConstraintConjunctionImpl:

    def __init__(self, id, minConstraints, maxConstraints, localConstraints):
        self.id = id
        self.minConstraints = minConstraints
        self.maxConstraints = maxConstraints
        self.minQueryPredicate = id + "_pos"
        self.localConstraints = localConstraints
        self.maxQueryPredicates = []

        self.minQuery = []
        self.maxQueries = []

        self.maxQueryPredicates = [self.id + "_max_" + str(i) for i in range(1, len(self.maxConstraints) + 1)]

    def getId(self):
        return self.id

    def getMinQuery(self):
        return self.minQuery

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
        return lambda c: c.getShapeRef() is not None and c.getIsPos() and not isinstance(c, MaxOnlyConstraintImpl)

    def negRefFilter(self):
        return lambda c: c.getShapeRef() is not None and (not c.getIsPos() or isinstance(c, MaxOnlyConstraintImpl))

    def getConjuncts(self):
        return self.minConstraints + self.maxConstraints  # *** tbc

    def computeQueries(self, graphName):
        # Create a subquery for all local (i.e. without shape propagation) and positive constraints
        # Every other query for this conjunct will contain this as a subquery.
        # This is unnecessary in theory, but does not compromise soundness, and makes queries more selective.

        queryGenerator = QueryGenerator()
        subquery = queryGenerator.generateLocalSubquery(
                graphName, self.minConstraints + self.localConstraints
        )

        # Build a unique set of triples (+ filter) for all min constraints (note that the local ones are handled by the subquery)
        self.minQuery = queryGenerator.generateQuery(
                self.minQueryPredicate,
                [c for c in self.minConstraints if c.getShapeRef() is not None],
                graphName,
                subquery
        )

        # Build one set of triples (+ filter) for each max constraint
        i = itertools.count()
        self.maxQueries = list(map(lambda c:
                              queryGenerator.generateQuery(
                                  self.maxQueryPredicates[next(i)],
                                  [c],
                                  graphName,
                                  subquery
                                  ), self.maxConstraints
                              ))
