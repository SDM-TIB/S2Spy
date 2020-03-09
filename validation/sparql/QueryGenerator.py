# -*- coding: utf-8 -*-
from validation.core.RulePattern import RulePattern
from validation.core.Literal import Literal
from validation.core.Query import Query
from validation.VariableGenerator import VariableGenerator
from validation.sparql.SPARQLPrefixHandler import getPrefixString
from validation.constraints.Constraint import Constraint


class QueryGenerator:
    def __init__(self):
        pass

    def generateQuery(self, id, constraints, graph=None, subquery=None):
        # TODO ("Only one max constraint per query is allowed");
        rp = self.computeRulePattern(constraints, id)

        builder = QueryBuilder(id, graph, subquery, rp.getVariables())
        map(lambda c: builder.buildClause(c), constraints)

        return builder.buildQuery(rp)

    @staticmethod
    def computeRulePattern(constraints, id):
        return RulePattern(
                Literal(
                        id,
                        VariableGenerator.getFocusNodeVar(),
                        True
                ),
                [c.computeRulePatternBody() for c in constraints]
        )

    @staticmethod
    def generateLocalSubquery(graphName, posConstraints):
        localPosConstraints = [c for c in posConstraints if c.getShapeRef() is None]

        if len(localPosConstraints) == 0:
            return None  # Optional empty

        builder = QueryBuilder(
                "tmp",
                graphName,
                None,
                VariableGenerator.getFocusNodeVar()
        )

        map(lambda c: builder.buildClause(c), localPosConstraints)

        return builder.getSparql(False)


# mutable
    # private class
class QueryBuilder:
    def __init__(self, id, graph, subquery, projectedVariables):
        self.id = id
        self.graph = graph
        self.projectedVariables = projectedVariables
        self.filters = []
        self.triples = []
        self.subQuery = subquery

    def addTriple(self, path, object):
        self.triples.append(
                "?" + VariableGenerator.getFocusNodeVar() + " " +
                        path + " " +
                        object + "."
        )

    def addDatatypeFilter(self, variable, datatype, isPos):
        s = self.__getDatatypeFilter(variable, datatype)
        self.filters.append(
                s if isPos else "!(" + s + ")"
        )

    def addConstantFilter(self, variable, constant, isPos):
        s = variable + " = " + constant
        self.filters.append(
                s if isPos else "!(" + s + ")"
        )

    def __getDatatypeFilter(self, variable, datatype):
        return "datatype(?" + variable + ") = " + datatype

    def getSparql(self, includePrefixes):  # assuming optional graph
        grapNotPresent = ""  # ***
        return getPrefixString() if includePrefixes else "" + \
                self.getProjectionString() + \
                " WHERE{" + \
                (grapNotPresent) + \
                "\n\n" + \
                self.getTriplePatterns() + \
                "\n" + \
                ("{\n" + self.subQuery.get() + "\n}\n" if self.subQuery is not None else "") + \
                (grapNotPresent) + \
                "\n}"

    def getProjectionString(self):
        return "SELECT DISTINCT " + \
                ", ".join(map(lambda v : "?" + v, self.projectedVariables))

    def getTriplePatterns(self):
        tripleString = "\n".join(self.triples)

        if len(self.filters) == 0:
            return tripleString

        return tripleString + self.generateFilterString()

    def generateFilterString(self):
        if len(self.filters) == 0:
            return ""

        return "\nFILTER(\n" + \
                (self.filters[0] if len(self.filters) == 1 else " AND\n".join(self.filters)
                ) + ")"

    def addCardinalityFilter(self, variables):
        for i in enumerate(variables):
            for j in enumerate(variables):
                self.filters.append("?" + variables.get(i) + " != ?" + variables.get(j))

    def buildClause(self, c):
        variables = c.getVariables()

        if isinstance(c, Constraint):
            path = c.getPath()

            if c.getValue() is not None:
                self.addTriple(path, c.getValue().get())
                return

            map(lambda v: self.addTriple(path, "?" + v), variables)

        elif c.getValue() is not None:
            self.addConstantFilter(
                    variables.iterator().next(),
                    c.getValue().get(),
                    c.getIsPos()
            )

        if c.getDatatype() is not None:
            variables = map(self.addDatatypeFilter(variables, c.getDatatype().get(), c.isPos()), variables)

        if len(variables) > 1:
            self.addCardinalityFilter(variables)

    def buildQuery(self, rulePattern):
        return Query(
                self.id,
                rulePattern,
                self.getSparql(True)
        )
