# -*- coding: utf-8 -*-
import argparse
from validation.Eval import *

if __name__ == '__main__':
    '''input example:
    python3 main.py -d ./shapes/nonRec/2/ -g "http://dbpedia.org/sparql" ./output/ DFS'''

    parser = argparse.ArgumentParser(description='SHACL Constraint Validation over a SPARQL Endpoint')
    parser.add_argument('-d', metavar='schemaDir', type=str, default=None,
                        help='Directory containing shapes')
    parser.add_argument('endpoint', metavar='endpoint', type=str, default=None,
                        help='SPARQL Endpoint')
    parser.add_argument('outputDir', metavar='outputDir', type=str, default=None,
                        help='Name of the directory where results of validation will be saved')
    parser.add_argument(dest='graphTraversal', type=str, default='DFS', choices=['BFS', 'DFS'],
                        help='The algorithm used for graph traversal (BFS / DFS)')

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-g", action="store_true", help="validate the whole graph")
    group.add_argument("-s", action="store_true", help="validate each shape")
    group.add_argument("-t", action="store_true", help="report valid instances")
    group.add_argument("-v", action="store_true", help="report violating instances")

    args = parser.parse_args()

    Eval(args)
