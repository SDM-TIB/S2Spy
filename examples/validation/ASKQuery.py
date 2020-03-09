# -*- coding: utf-8 -*-
import re
from SPARQLWrapper import SPARQLWrapper, XML


class ASKQuery:
    def __init__(self, constraint, target):
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

    def ASKQueryCardinConstraint(self, operator, cardinality):
        return "ASK {\n\
                { SELECT ?s COUNT(?o) AS ?cnt WHERE {\n\
                    ?s a %s.\n\
                    ?s %s ?o.\n\
                }\n\
                GROUP BY(?s)\n\
                }\n\
                FILTER (?cnt %s %s)\n\
                }" % (self.target, self.constraint, operator, str(cardinality))

    def evaluate(self, type, cardinality):
        if type == "min":
            query = self.ASKQueryCardinConstraint("<", cardinality)
        else:
            query = self.ASKQueryCardinConstraint(">", cardinality)

        sparql = SPARQLWrapper("http://dbpedia.org/sparql")  # TODO: get URL from parameters
        sparql.setQuery(query)
        sparql.setReturnFormat(XML)
        results = sparql.query().convert()
        if re.search("true", results.toxml()):
            return True
        else:
            return False
