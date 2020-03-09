# -*- coding: utf-8 -*-
from os import path
from pyshacl import validate
from pyshacl import get_query
from SPARQLWrapper import SPARQLWrapper, TURTLE
from rdflib import Graph

from utils import lastStringURL
import time

def select_shapes_graph():
    c1 = "./shapes/smoker.ttl"
    c2 = "./shapes/patient_stage.ttl"
    c3 = "./shapes/biomarker.ttl"

    sg = c1

    sg = path.abspath(sg)

    return sg

def main(sg):
    retrieve_all_data = False

    sparql = SPARQLWrapper("http://node2.research.tib.eu:18971/sparql")

    construct_query = '''CONSTRUCT {
                      ?s ?p ?o.
                  }
                  WHERE {
                      ?s ?p ?o.
                  }'''

    if not retrieve_all_data:

        construct_query = get_query(sg)
        print("Construct query:\n", construct_query)

    sparql.setQuery(construct_query)

    ######################################

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

    print(v_text)

if __name__ == '__main__':

    sg = select_shapes_graph()

    start = time.time()
    main(sg)
    end = time.time()

    print("Runtime: ", end - start)