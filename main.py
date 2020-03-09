# -*- coding: utf-8 -*-
import argparse
from validation.Eval import *

if __name__ == '__main__':
    '''input example:
    python3 main.py -d ./shapes/nonRec/2/ "http://dbpedia.org/sparql" ./output/'''

    parser = argparse.ArgumentParser(description='SHACL constraint validation')
    parser.add_argument('-d', metavar='schemaDir', type=str, default=None,
                        help='Directory containing shapes')
    parser.add_argument('endpoint', metavar='endpoint', type=str, default=None,
                        help='SPARQL Endpoint')
    parser.add_argument('outputDir', metavar='outputDir', type=str, default=None,
                        help='Name of the directory where results of validation will be saved')

    args = parser.parse_args()

    Eval(args)
