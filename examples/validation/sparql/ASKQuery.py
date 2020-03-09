# -*- coding: utf-8 -*-
__author__ = "Monica Figuera and Philipp D. Rohde"

import re
from validation.sparql import SPARQLEndpoint


class ASKQuery:

    def __init__(self, constraint, target, type):
        self.constraint = constraint
        self.target = target
        self.type = type

    def ASKQueryExistsConstraint(self):
        return "ASK {\n\
                    ?s a %s\n\
                    FILTER NOT EXISTS {\n\
                    ?s %s ?o.\n\
                    }\n\
                }" % (self.target, self.constraint)

    def ASKQueryCardConstraint(self, operator, cardinality):
        return "ASK {\n\
                { SELECT ?s COUNT(?o) AS ?cnt WHERE {\n\
                    ?s a %s.\n\
                    ?s %s ?o.\n\
                }\n\
                GROUP BY(?s)\n\
                }\n\
                FILTER (?cnt %s %s)\n\
                }" % (self.target, self.constraint, operator, str(cardinality))

    def ASKQueryCardRangeConstraint(self, minCard, maxCard):
        return "ASK {\n\
                { SELECT ?s COUNT(?o) AS ?cnt WHERE {\n\
                    ?s a %s.\n\
                    ?s %s ?o.\n\
                }\n\
                GROUP BY(?s)\n\
                }\n\
                FILTER (?cnt < %s OR ?cnt > %s)\n\
                }" % (self.target, self.constraint, str(minCard), str(maxCard))

    def evaluate(self, type, cardinality=None, minCard=None, maxCard=None):
        if type == "min":
            query = self.ASKQueryCardConstraint("<", cardinality)
        elif type == "max":
            query = self.ASKQueryCardConstraint(">", cardinality)
        else:
            query = self.ASKQueryCardRangeConstraint(minCard, maxCard)

        #sparql = SPARQLWrapper("http://dbpedia.org/sparql")  # TODO: get URL from parameters / use sparql.SPARQLEndpoint
        #sparql.setQuery(query)
        #sparql.setReturnFormat(XML)
        #results = sparql.query().convert()
        results = SPARQLEndpoint.runQuery(None, query)  # TODO: generate ID for the query?
        if re.search("true", results.toxml()):
            return True
        else:
            return False
