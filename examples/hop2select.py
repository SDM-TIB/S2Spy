# -*- coding: utf-8 -*-
from os import path
from pyshacl import validate
from pyshacl import get_construct_query
from SPARQLWrapper import SPARQLWrapper, TURTLE, JSONLD, RDF, JSON
from rdflib import Graph
import re

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
    results =  {'head': {'link': [], 'vars': ['LCPatient', 'numberOfCigarettesPerYear', 'smoking']}, 'results': {'distinct': False, 'ordered': True, 'bindings': [

    {'LCPatient': {'type': 'uri', 'value': 'http://project-iasis.eu/LCPatient/1015121'},
     'numberOfCigarettesPerYear': {'type': 'literal', 'value': '3650'},
     'smoking': {'type': 'literal', 'value': 'former'}},

    {'LCPatient': {'type': 'uri', 'value': 'http://project-iasis.eu/LCPatient/1019115'}, 'numberOfCigarettesPerYear': {'type': 'literal', 'value': '7300'}, 'smoking': {'type': 'literal', 'value': 'former'}},

    {'LCPatient': {'type': 'uri', 'value': 'http://project-iasis.eu/LCPatient/1019206'}, 'numberOfCigarettesPerYear': {'type': 'literal', 'value': '29200'}, 'smoking': {'type': 'literal', 'value': 'former'}}, {'LCPatient': {'type': 'uri', 'value': 'http://project-iasis.eu/LCPatient/101957'}, 'numberOfCigarettesPerYear': {'type': 'literal', 'value': '21900'}, 'smoking': {'type': 'literal', 'value': 'former'}},

    {'LCPatient': {'type': 'uri', 'value': 'http://project-iasis.eu/LCPatient/1022636'}, 'numberOfCigarettesPerYear': {'type': 'literal', 'value': '7300'}, 'smoking': {'type': 'literal', 'value': 'former'}}, {'LCPatient': {'type': 'uri', 'value': 'http://project-iasis.eu/LCPatient/1026200'}, 'numberOfCigarettesPerYear': {'type': 'literal', 'value': '18250'}, 'smoking': {'type': 'literal', 'value': 'former'}}, {'LCPatient': {'type': 'uri', 'value': 'http://project-iasis.eu/LCPatient/1032340'}, 'numberOfCigarettesPerYear': {'type': 'literal', 'value': '29200'}, 'smoking': {'type': 'literal', 'value': 'former'}}, {'LCPatient': {'type': 'uri', 'value': 'http://project-iasis.eu/LCPatient/1035873'}, 'numberOfCigarettesPerYear': {'type': 'literal', 'value': '14600'}, 'smoking': {'type': 'literal', 'value': 'former'}}, {'LCPatient': {'type': 'uri', 'value': 'http://project-iasis.eu/LCPatient/1038502'}, 'numberOfCigarettesPerYear': {'type': 'literal', 'value': '10950'}, 'smoking': {'type': 'literal', 'value': 'former'}}, {'LCPatient': {'type': 'uri', 'value': 'http://project-iasis.eu/LCPatient/1040515'}, 'numberOfCigarettesPerYear': {'type': 'literal', 'value': '7300'}, 'smoking': {'type': 'literal', 'value': 'former'}}, {'LCPatient': {'type': 'uri', 'value': 'http://project-iasis.eu/LCPatient/1040558'}, 'numberOfCigarettesPerYear': {'type': 'literal', 'value': '10950'}, 'smoking': {'type': 'literal', 'value': 'former'}}, {'LCPatient': {'type': 'uri', 'value': 'http://project-iasis.eu/LCPatient/1042887'}, 'numberOfCigarettesPerYear': {'type': 'literal', 'value': '14600'}, 'smoking': {'type': 'literal', 'value': 'former'}}, {'LCPatient': {'type': 'uri', 'value': 'http://project-iasis.eu/LCPatient/1043710'}, 'numberOfCigarettesPerYear': {'type': 'literal', 'value': '7300'}, 'smoking': {'type': 'literal', 'value': 'former'}}, {'LCPatient': {'type': 'uri', 'value': 'http://project-iasis.eu/LCPatient/1044179'}, 'numberOfCigarettesPerYear': {'type': 'literal', 'value': '7300'}, 'smoking': {'type': 'literal', 'value': 'former'}}, {'LCPatient': {'type': 'uri', 'value': 'http://project-iasis.eu/LCPatient/1045694'}, 'numberOfCigarettesPerYear': {'type': 'literal', 'value': '400'}, 'smoking': {'type': 'literal', 'value': 'former'}}, {'LCPatient': {'type': 'uri', 'value': 'http://project-iasis.eu/LCPatient/1046702'}, 'numberOfCigarettesPerYear': {'type': 'literal', 'value': '7300'}, 'smoking': {'type': 'literal', 'value': 'former'}}
    ]}}

    extended_approach = True

    if extended_approach:
        start = time.time()

        '''sparql = SPARQLWrapper("http://node3.research.tib.eu:9003/sparql")
        query = get_construct_query(sg)
        print("Query:\n", query)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()'''

        query = '''SELECT * WHERE {
        ?LCPatient <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>  <http://project-iasis.eu/vocab/LCPatient>.
        ?LCPatient <http://project-iasis.eu/vocab/numberOfCigarettesPerYear>  ?numberOfCigarettesPerYear.
        ?LCPatient <http://project-iasis.eu/vocab/smoking>  ?smoking.
        }'''

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
                # print(key,props["type"], props["value"])
                if props["type"] == "literal":
                    template_copy = re.sub(pattern, '"' + props["value"] + '"', template_copy)
                    #print("alo", template_copy)
                elif props["type"] == "uri":
                    template_copy = re.sub(pattern, '<' + props["value"] + '>', template_copy)
                triples.append(template_copy)

        data_turtle_format = data_turtle_format.join(triples)
        print(data_turtle_format)
        end = time.time()

        print("Runtime: ", end - start)


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
    sg = select_shapes_graph()

    main(sg)
