# -*- coding: utf-8 -*-
from os import path
from SHACLtoConstructQuery import get_construct_query
from SPARQLWrapper import SPARQLWrapper, TURTLE
from rdflib import Graph
from pyshacl import validate

def main():
    retrieveFromEndpoint = False

    if retrieveFromEndpoint:
        sparql = SPARQLWrapper("http://node2.research.tib.eu:18971/sparql")

    sg = "./shapes/smoker.ttl"
    sg = path.abspath(sg)

    data_ttl_file = "./data/smoker_ex.ttl"
    data_ttl_file = path.abspath(data_ttl_file)

    construct_query = get_construct_query(sg)
    print("Construct query:\n", construct_query)

    if retrieveFromEndpoint:
        sparql.setQuery(construct_query)

        ######################################

        print('*** Creating file in Turtle Format ***')
        sparql.setReturnFormat(TURTLE)
        results = sparql.query().convert()
        g = Graph()
        g.parse(data=results, format="turtle")
        g.serialize(format='turtle')

        file_name = "data/output.ttl"
        file = open(file_name, "wb")
        g.serialize(destination=file, format="turtle")
        file.flush()
        file.close()
        #print(g)
        data_ttl_file = path.abspath(file_name)

    conforms, v_graph, v_text = validate(data_ttl_file, shacl_graph=sg, inference='rdfs',
                                         serialize_report_graph=True)

    print(conforms)
    print(v_graph)
    print(v_text)


if __name__ == '__main__':
    main()