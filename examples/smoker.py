# -*- coding: utf-8 -*-
from os import path
from SHACLtoConstructQuery import get_construct_query
from SPARQLWrapper import SPARQLWrapper, TURTLE
from rdflib import Graph
from pyshacl import validate
from utils import lastStringURL

def main():
    sparql = SPARQLWrapper("http://node2.research.tib.eu:18971/sparql")

    sg = "./shapes/smoker.ttl"
    sg = path.abspath(sg)

    construct_query = get_construct_query(sg)
    #print("Construct query:\n", construct_query)

    sparql.setQuery(construct_query)

    ######################################

    #print('*** Creating file in Turtle Format ***')
    sparql.setReturnFormat(TURTLE)
    results = sparql.query().convert()
    g = Graph()
    g.parse(data=results, format="turtle")
    g.serialize(format='turtle')

    filename = lastStringURL(sg)[1]
    file_path = "data/" + filename
    file = open(file_path, "wb")
    g.serialize(destination=file, format="turtle")
    file.flush()
    file.close()

    data_ttl_file = path.abspath(file_path)

    conforms, v_graph, v_text = validate(data_ttl_file, shacl_graph=sg, inference='rdfs',
                                         serialize_report_graph=True)

    #print(v_graph)
    print(v_text)


if __name__ == '__main__':
    main()