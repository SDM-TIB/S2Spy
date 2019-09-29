# -*- coding: utf-8 -*-
import sys
from os import path
from pyshacl import validate
from pyshacl import get_construct_query
from SPARQLWrapper import SPARQLWrapper, TURTLE
from rdflib import Graph

from utils import lastStringURL
import time


def shapes_graph_to_test():
    constraints = []
    constraints.append("./shapes/smoker.ttl")
    constraints.append("./shapes/patient_stage.ttl")
    constraints.append("./shapes/biomarker.ttl")

    return constraints

def get_reduced_data_from_endpoint(sg):
    sparql = SPARQLWrapper("http://node3.research.tib.eu:9002/sparql")

    construct_query = get_construct_query(sg)
    print("Construct query:\n", construct_query)

    sparql.setQuery(construct_query)

    sparql.setReturnFormat(TURTLE)
    results = sparql.query().convert()
    g = Graph()
    g.parse(data=results, format="turtle")
    g.serialize(format='turtle')

    filename = lastStringURL(sg)[1]
    file_path = "data/retrieved/" + filename
    file = open(file_path, "wb")
    g.serialize(destination=file, format="turtle")
    file.flush()
    file.close()

    return path.abspath(file_path)


def main(sg, extended_approach):
    loading_time_start = time.time()
    if extended_approach:
        data_ttl_file = get_reduced_data_from_endpoint(sg)
    else:
        # use locally saved data
        data_ttl_file = "data/hop2.ttl"
    loading_time_end = time.time()

    validation_time_start = time.time()
    conforms, v_graph, v_text = validate(data_ttl_file, shacl_graph=sg, inference='rdfs',
                                         serialize_report_graph=True)
    validation_time_end = time.time()

    print(v_text)
    print("Loading time: ", loading_time_end - loading_time_start)
    print("Validation time: ", validation_time_end - validation_time_start)

if __name__ == '__main__':
    extended_approach = False

    if len(sys.argv) == 2:
        if sys.argv[1] == "wrapper":
            extended_approach = True

    constraints = shapes_graph_to_test()

    for x in constraints:
        print("\n# File: ", x, "\n")

        sg = x
        sg = path.abspath(sg)

        start = time.time()
        main(sg, extended_approach)
        end = time.time()

        print("Total runtime", x, ": ", end - start)