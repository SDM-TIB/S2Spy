# -*- coding: utf-8 -*-
import argparse
from validation.Eval import *
import time

if __name__ == '__main__':
    '''input example:
    python3 main.py -d ./shapes/nonRec/2/ -g "http://dbpedia.org/sparql" ./output/ DFS --heuristics TARGET IN BIG'''
    # add the optional flag '--selective' in the command line to use configuration of more selective queries

    start = time.time()

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
    group.add_argument("-a", action="store_true", help="report both valid and violating instances")

    parser.add_argument("--heuristics", nargs="*", type=str, default=[],
                        help="TARGET if shapes with target definition should be prioritized\n"
                             "[IN / OUT / INOUT / OUTIN] if a higher in- or outdegree should be prioritized\n"
                             "[SMALL / BIG] if small or big shapes should be prioritized", required=True)

    parser.add_argument("--selective", action='store_true', default=False,
                        help="Use more selective queries")

    args = parser.parse_args()

    Eval(args)

    end = time.time()
    print("Total runtime: ", end - start)
