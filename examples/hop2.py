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

    sg = actor

    sg = path.abspath(sg)

    return sg

def get_data_turtle_format(query, results):
    template_for_triples = query
    pattern = r'.*\{\n'
    replace = ''
    string = template_for_triples
    template_for_triples = re.sub(pattern, replace, string)
    pattern = r'\}.*'
    replace = ''
    string = template_for_triples
    template_for_triples = re.sub(pattern, replace, string)
    print("Template:\n", template_for_triples)

    triples = ''
    for i, result in enumerate(results["results"]["bindings"]):
        template_copy = template_for_triples
        for key, props in result.items():
            pattern = r"\?" + re.escape(key) + r"\b"   # current key pattern
            subj_pattern = r"\?" + key + r"[ <]+"
            match_subj = re.match(subj_pattern, template_copy)

            # remove duplicate triples
            if props["value"] == results["results"]["bindings"][i-1][key]["value"] and not match_subj:
                patternLine = r".*\?" + re.escape(key) + r"[ ]*(.)\n"
                template_copy = re.sub(patternLine, '', template_copy)
                continue

            # replace triple variables with their correspondent URIs or literals
            if props["type"] == "literal":
                template_copy = re.sub(pattern,
                                       ''.join([' "', props["value"], '"']),
                                       template_copy)
            elif props["type"] == "uri":
                template_copy = re.sub(pattern,
                                       ''.join([' <', props["value"], '>']),
                                       template_copy)
            elif props["type"] == "typed-literal":
                dtype = props["datatype"]
                template_copy = re.sub(pattern,
                                       ''.join([' "', props["value"], '"', "^^<", dtype, ">"]),
                                       template_copy)
            else:
                print(props["type"], props)
        triples += template_copy

    return triples

def main(sg, option):

    extended_approach = True

    if extended_approach:
        start = time.time()

        #sparql = SPARQLWrapper("http://node4.research.tib.eu:9090/sparql")
        sparql = SPARQLWrapper("http://dbpedia.org/sparql")

        query = get_query(sg, option)
        print("Query:\n", query)

        sparql.setQuery(query)
        if option == "select":
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            end = time.time()

            data_graph = get_data_turtle_format(query, results)
            end2 = time.time()

        else:
            sparql.setReturnFormat(TURTLE)
            results = sparql.query().convert()
            end = time.time()

            g = Graph()
            g.parse(data=results, format="turtle")
            data_graph = g
            end2 = time.time()

        print(data_graph)

        total = end - start
        print("Runtime (retrieving from endpoint) for {o} query is {t}".format(o=option, t=total))

        total2 = end2 - start
        print("Runtime 2 (Turtle file creation) for {o} query is {t}".format(o=option, t=total2))

        if data_graph != '':
            conforms, v_graph, v_text = validate(data_graph, shacl_graph=sg, inference='rdfs',
                                                 serialize_report_graph=True, data_graph_format='turtle')
            end3 = time.time()
            total3 = end3 - start
            print("Runtime 3 (constraints validation) for {o} query is {t}".format(o=option, t=total3))
        else:
            print("Error: Empty data graph")
    else:
        # use locally saved data
        data_ttl_file = "data/hop2.ttl"

        #conforms, v_graph, v_text = validate(data_ttl_file, shacl_graph=sg, inference='rdfs',
        #                                     serialize_report_graph=True)

    #print(v_text)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='SHACL constraint evaluation')
    parser.add_argument('retrieve_type', metavar='retrieveType', type=str, default='select',
                        help='Two options available: select / construct')
    args = parser.parse_args()

    option = args.retrieve_type

    sg = get_shapes_graph()


    main(sg, option)

