# -*- coding: utf-8 -*-
__author__ = "Monica Figuera and Philipp D. Rohde"

import re
from validation.sparql.SPARQLEndpoint import SPARQLEndpoint


class ASKQuery:
    def __init__(self, constraint, target, type):
        self.constraint = constraint
        self.target = target
        self.type = type
        self.query = None

    def evaluate(self):
        return False

        # TODO: use the code below once other query generation issues are fixed
        #results = SPARQLEndpoint.instance.runQuery(None, self.query)  # TODO: generate ID for the query?
        #if re.search("true", results.toxml()):
        #    return True
        #else:
        #    return False


class ASKQueryCardConstraint(ASKQuery):
    def __init__(self, constraint, target, type, operator, cardinality):
        super().__init__(constraint, target, type)
        self.operator = operator
        self.cardinality = cardinality
        self.query = "ASK {\n\
                { SELECT ?s COUNT(?o) AS ?cnt WHERE {\n\
                    ?s a %s.\n\
                    ?s %s ?o.\n\
                }\n\
                GROUP BY(?s)\n\
                }\n\
                FILTER (?cnt %s %s)\n\
                }" % (self.target, self.constraint, operator, str(cardinality))


class ASKQueryMinCardConstraint(ASKQueryCardConstraint):
    def __init__(self, constraint, target, cardinality):
        super().__init__(constraint, target, "min", "<", cardinality)


class ASKQueryMaxCardConstraint(ASKQueryCardConstraint):
    def __init__(self, constraint, target, cardinality):
        super().__init__(constraint, target, "max", ">", cardinality)


class ASKQueryCardRangeConstraint(ASKQuery):
    def __init__(self, constraint, target, min, max):
        super().__init__(constraint, target, "minmax")
        self.min = min
        self.max = max
        self.query = "ASK {\n\
                { SELECT ?s COUNT(?o) AS ?cnt WHERE {\n\
                    ?s a %s.\n\
                    ?s %s ?o.\n\
                }\n\
                GROUP BY(?s)\n\
                }\n\
                FILTER (?cnt < %s OR ?cnt > %s)\n\
                }" % (self.target, self.constraint, str(min), str(max))


class ASKQueryExistsConstraint(ASKQuery):
    def __init__(self, constraint, target):
        super().__init__(constraint, target, "exists")
        self.query = "ASK {\n\
                    ?s a %s\n\
                    FILTER NOT EXISTS {\n\
                    ?s %s ?o.\n\
                    }\n\
                }" % (self.target, self.constraint)
