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
        for c in constraints:
            builder.buildClause(c)

        return builder.buildQuery(rp)

    @staticmethod
    def computeRulePattern(constraints, id):
        body = []
        for c in constraints:
            body = body + c.computeRulePatternBody()

        return RulePattern(
                Literal(
                        id,
                        VariableGenerator.getFocusNodeVar(),
                        True
                ),
                body
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

        for c in localPosConstraints:
            builder.buildClause(c)

        return builder.getSparql(False)


# mutable
    # private class
class QueryBuilder:
    def __init__(self, id, graph, subquery, projectedVariables):
        self.id = id
        self.graph = graph
        self.subQuery = subquery
        self.projectedVariables = projectedVariables
        self.filters = []
        self.triples = []

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
        prefixes = getPrefixString() if includePrefixes else ""
        return prefixes + \
                self.getProjectionString() + \
                " WHERE {" + \
                (grapNotPresent) + \
                "\n" + \
                self.getTriplePatterns() + \
                "\n" + \
                ("{\n" + self.subQuery + "\n}\n" if self.subQuery is not None else "") + \
                (grapNotPresent) + \
                "\n}"

    def getProjectionString(self):
        return "SELECT DISTINCT " + \
                ", ".join(["?" + v for v in self.projectedVariables])

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
        for i in range(0, len(variables)):
            for j in range(i + 1, len(variables)):
                self.filters.append("?" + variables[i] + " != ?" + variables[j])

    def buildClause(self, c):
        variables = c.getVariables()

        if isinstance(c, Constraint):
            path = c.path

            if c.getValue() is not None:        # means there is a existing reference to another shape
                self.addTriple(path, c.getValue())
                return

            for v in variables:
                self.addTriple(path, "?" + v)

        if c.getValue() is not None:
            self.addConstantFilter(
                    variables.iterator().next(),
                    c.getValue().get(),
                    c.getIsPos()
            )

        if c.getDatatype() is not None:
            for v in variables:
                self.addDatatypeFilter(v, c.getDatatype(), c.isPos())

        if len(variables) > 1:
            self.addCardinalityFilter(variables)

    def buildQuery(self, rulePattern):
        return Query(
                self.id,
                rulePattern,
                self.getSparql(True)
        )
