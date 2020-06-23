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

    def generateQuery(self, id, constraints, target, isSelective, graph=None, subquery=None):
        # Only one max constraint per query is allowed, then 'constraints' arg contain only 1 element for the max case

        rp = self.computeRulePattern(constraints, id)

        if id == "template_VALUES":
            return self.targetQuery_VALUES(constraints, target)
        elif id == "template_FILTER_NOT_IN":
            return self.targetQuery_FILTER_NOT_IN(constraints, target)

        builder = QueryBuilder(id, graph, subquery, rp.getVariables(), isSelective, target, constraints)
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

    def targetQuery_VALUES(self, constraint, targetPath):
        includePrefixes = True
        prefixes = getPrefixString() if includePrefixes else ""
        path = constraint[0].path
        focusVar = VariableGenerator.getFocusNodeVar()

        rdfClass = "?" + focusVar + " a " + targetPath + "." if targetPath is not None else ""

        query = prefixes + \
                "SELECT DISTINCT ?" + focusVar + " WHERE {\n" + \
                "VALUES ?inst { $to_be_replaced$ }. \n" + \
                "?" + focusVar + " " + path + " ?inst.\n" + \
                rdfClass + "\n}\n"

        return Query(
                None,
                None,
                query
        )

    def targetQuery_FILTER_NOT_IN(self, constraint, selectivePath):
        includePrefixes = True
        prefixes = getPrefixString() if includePrefixes else ""
        path = constraint[0].path
        focusVar = VariableGenerator.getFocusNodeVar()
        if selectivePath is not None:
            rdfClass = "?" + focusVar + " a " + selectivePath + "."
        else:
            rdfClass = ""

        query = prefixes + \
                "SELECT DISTINCT ?" + focusVar + " WHERE {\n" + \
                "?" + focusVar + " " + path + " ?inst.\n" + \
                rdfClass + "\n" + \
                "FILTER (?inst NOT IN ( $to_be_replaced$ )). }\n"

        return Query(
                None,
                None,
                query
        )

# mutable
    # private class
class QueryBuilder:
    def __init__(self, id, graph, subquery, projectedVariables, isSelective=None, targetPath=None, constraints=None):
        self.id = id
        self.graph = graph
        self.subQuery = subquery
        self.projectedVariables = projectedVariables
        self.filters = []
        self.triples = []

        self.considerSelectivity = isSelective and targetPath is not None
        self.isSelective = isSelective
        self.targetPath = targetPath
        self.constraints = constraints

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
        selectiveClosingBracket = "}}" if self.considerSelectivity else ""
        prefixes = getPrefixString() if includePrefixes else ""

        tempString = ""
        if includePrefixes:
            if "_pos" in self.id or "_max_" in self.id:
                # add VALUES clause to external query
                tempString = "$to_be_replaced$"

        return prefixes + \
                self.getSelective() + \
                self.getProjectionString() + \
                " WHERE {" + \
                (grapNotPresent) + \
                "\n" + \
                tempString + \
                self.getTriplePatterns() + \
                "\n" + \
                ("{\n" + self.subQuery + "\n}\n" if self.subQuery is not None else "") + \
                (grapNotPresent) + \
                "\n}" + selectiveClosingBracket

    def getSelective(self):
        if self.considerSelectivity:
            return "SELECT " + \
                   ", ".join(["?" + v for v in self.projectedVariables]) + " WHERE {\n" + \
                   "?" + VariableGenerator.getFocusNodeVar() + " a " + self.targetPath + " {\n"
        return ""

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
