# -*- coding: utf-8 -*-
from os import path
from pyshacl import validate
from pyshacl import get_construct_query
from SPARQLWrapper import SPARQLWrapper, TURTLE
from rdflib import Graph

from utils import lastStringURL
import time

def select_shapes_graph():
    c1 = "./shapes/smoker.ttl"
    c2 = "./shapes/patient_stage.ttl"
    c3 = "./shapes/biomarker.ttl"
    c4 = "./shapes/patient_diagn_tumtype.ttl"

    actor = "./shapes/dbpedia/ActorShape.ttl"
    movie = "./shapes/dbpedia/MovieShape.ttl"

    sg = c1

    sg = path.abspath(sg)

    return sg

def main(sg):
    extended_approach = True

    if extended_approach:
        sparql = SPARQLWrapper("http://node3.research.tib.eu:9003/sparql")

        construct_query = get_construct_query(sg)
        print("Construct query:\n", construct_query)

        sparql.setQuery(construct_query)

        sparql.setReturnFormat(TURTLE)
        results = sparql.query().convert()
        g = Graph()
        g.parse(data=results, format="turtle")

        conforms, v_graph, v_text = validate(g, shacl_graph=sg, inference='rdfs',
                                         serialize_report_graph=True)
    else:
        # use locally saved data
        data_ttl_file = "data/hop2.ttl"

        conforms, v_graph, v_text = validate(data_ttl_file, shacl_graph=sg, inference='rdfs',
                                         serialize_report_graph=True)

    print(v_text)

if __name__ == '__main__':

    sg = select_shapes_graph()

    start = time.time()
    main(sg)
    end = time.time()

    print("Runtime: ", end - start)