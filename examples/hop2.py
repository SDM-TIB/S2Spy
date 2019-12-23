# -*- coding: utf-8 -*-
from os import path
from pyshacl import validate
from pyshacl import get_query
from SPARQLWrapper import SPARQLWrapper, JSON, TURTLE
import re
import time
import argparse
from rdflib import Graph


def get_shapes_graph():
    c1 = "./shapes/smoker.ttl"
    c2 = "./shapes/patient_stage.ttl"
    c3 = "./shapes/biomarker.ttl"
    c4 = "./shapes/patient_diagn_tumtype.ttl"

    actor = "./shapes/dbpedia/ActorShape.ttl"
    movie = "./shapes/dbpedia/MovieShape.ttl"

    sg = c1

    sg = path.abspath(sg)

    return sg

def get_data_turtle_format(query, results):
    template_for_triples = query
    pattern = '.*\{'
    replace = ''
    string = template_for_triples
    template_for_triples = re.sub(pattern, replace, string)
    pattern = '\}.*'
    replace = ''
    string = template_for_triples
    template_for_triples = re.sub(pattern, replace, string)
    print(template_for_triples)

    data_turtle_format = ''
    triples = []
    for result in results["results"]["bindings"]:
        template_copy = template_for_triples
        for key, props in result.items():
            pattern = r"\?" + re.escape(key) + r"\b"
            print(pattern)
            if props["type"] == "literal":
                template_copy = re.sub(pattern, '"' + props["value"] + '"', template_copy)
            elif props["type"] == "uri":
                template_copy = re.sub(pattern, ' <' + props["value"] + '> ', template_copy)
            triples.append(template_copy)

    return data_turtle_format.join(triples)

def main(sg, option):

    extended_approach = True

    if extended_approach:
        sparql = SPARQLWrapper("http://node3.research.tib.eu:9003/sparql")

        query = get_query(sg, option)
        print("Query:\n", query)

        sparql.setQuery(query)
        if option == "select":
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            data_graph = get_data_turtle_format(query, results)
            #print(data_graph)
        else:
            sparql.setReturnFormat(TURTLE)
            results = sparql.query().convert()
            g = Graph()
            g.parse(data=results, format="turtle")
            data_graph = g

        conforms, v_graph, v_text = validate(data_graph, shacl_graph=sg, inference='rdfs',
                                             serialize_report_graph=True, data_graph_format='turtle')
    else:
        # use locally saved data
        data_ttl_file = "data/hop2.ttl"

        conforms, v_graph, v_text = validate(data_ttl_file, shacl_graph=sg, inference='rdfs',
                                             serialize_report_graph=True)

    print(v_text)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='SHACL constraint evaluation')
    parser.add_argument('retrieve_type', metavar='retrieveType', type=str, default='select',
                        help='Two options available: select / construct')
    args = parser.parse_args()

    option = args.retrieve_type

    sg = get_shapes_graph()

    start = time.time()
    main(sg, option)
    end = time.time()
    time = end - start
    print("Runtime for {o} query is {t}".format(o=option, t=time))