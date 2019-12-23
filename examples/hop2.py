# -*- coding: utf-8 -*-
from os import path
from pyshacl import validate
from pyshacl import get_construct_query
from SPARQLWrapper import SPARQLWrapper, TURTLE, JSONLD, RDF, JSON
from rdflib import Graph, plugin

from utils import lastStringURL
import time

def select_shapes_graph():
    c1 = "./shapes/smoker.ttl"
    c2 = "./shapes/patient_stage.ttl"
    c3 = "./shapes/biomarker.ttl"
    c4 = "./shapes/patient_diagn_tumtype.ttl"

    actor = "./shapes/dbpedia/ActorShape.ttl"
    movie = "./shapes/dbpedia/MovieShape.ttl"

    sg = actor

    sg = path.abspath(sg)

    return sg

def main(sg):
    extended_approach = True
    save_graph = False

    if extended_approach:
        start = time.time()

        sparql = SPARQLWrapper("http://dbpedia.org/sparql")

        query = get_construct_query(sg)
        print("Query:\n", query)

        sparql.setQuery(query)

        sparql.setReturnFormat(JSONLD)
        results = sparql.query().convert()
        #for result in results["results"]["bindings"]:
        #    print(result)
        end = time.time()

        print("Runtime: ", end - start)

        if save_graph:

            filename = lastStringURL(sg)[1]
            file_path = "data/retrieved/" + filename
            file = open(file_path, "wb")
            results.serialize(destination=file, format="json-ld")
            file.flush()
            file.close()

            data_ttl_file = path.abspath(file_path)

            data_graph = data_ttl_file
        else:
            data_graph = results

        #conforms, v_graph, v_text = validate(data_graph, shacl_graph=sg, inference='rdfs', serialize_report_graph=True)
    else:
        # use locally saved data
        data_ttl_file = "data/hop2.ttl"

        conforms, v_graph, v_text = validate(data_ttl_file, shacl_graph=sg, inference='rdfs',
                                         serialize_report_graph=True)

    #print(v_text)

if __name__ == '__main__':

    sg = select_shapes_graph()

    main(sg)
