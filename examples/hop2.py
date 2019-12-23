# -*- coding: utf-8 -*-
from os import path
from pyshacl import validate
from pyshacl import get_query
from SPARQLWrapper import SPARQLWrapper, JSON
import re
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


def main(sg, option):

    extended_approach = True

    if extended_approach:
        sparql = SPARQLWrapper("http://node3.research.tib.eu:9003/sparql")
        query = get_query(sg, option)
        print("Query:\n", query)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

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
                pattern = "\?" + key
                if props["type"] == "literal":
                    template_copy = re.sub(pattern, '"' + props["value"] + '"', template_copy)
                elif props["type"] == "uri":
                    template_copy = re.sub(pattern, '<' + props["value"] + '>', template_copy)
                triples.append(template_copy)

        data_turtle_format = data_turtle_format.join(triples)
        data_graph = data_turtle_format

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
    parser.add_argument('retrieve_type', metavar='R', type=str, default='select',
                        help='Two options available: select / construct')
    args = parser.parse_args()

    option = args.retrieve_type

    sg = select_shapes_graph()

    start = time.time()
    main(sg, option)
    end = time.time()
    print("Runtime for %s: %d", (option, end - start))
