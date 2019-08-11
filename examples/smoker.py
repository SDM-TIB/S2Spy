# -*- coding: utf-8 -*-
from os import path
from SHACLtoConstructQuery import get_construct_query
from SPARQLWrapper import SPARQLWrapper, TURTLE
from rdflib import Graph
from pyshacl import validate

sparql = SPARQLWrapper("http://node2.research.tib.eu:18971/sparql")

def main():
    sg = './shapes/smoker.ttl'
    sg = path.abspath(sg)

    construct_query = get_construct_query(sg)

    sparql.setQuery(construct_query)
    print("Construct query:\n", construct_query)

    ######################################

    print('*** Creating file in Turtle Format ***')
    sparql.setReturnFormat(TURTLE)
    results = sparql.query().convert()
    g = Graph()
    g.parse(data=results, format="turtle")
    g.serialize(format='turtle')

    file = open("data/output.ttl", "wb")
    g.serialize(destination=file, format="turtle")
    file.flush()
    file.close()
    print(g)

    conforms, v_graph, v_text = validate("data/output.ttl", shacl_graph=sg, inference='rdfs',
                                         serialize_report_graph=True)

    print(conforms)
    print(v_graph)
    print(v_text)


if __name__ == '__main__':
    main()