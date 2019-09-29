# -*- coding: utf-8 -*-
from os import path
from pyshacl import validate

import time

def select_shapes_graph():
    c1 = "./shapes/personexample.test.ttl"

    sg = c1

    sg = path.abspath(sg)

    return sg

def main(sg):
    # We assume we already have the data saved locally
    data_ttl_file = "personcities.ttl"

    conforms, v_graph, v_text = validate(data_ttl_file, shacl_graph=sg, inference='rdfs',
                                         serialize_report_graph=True)

    print(v_text)

if __name__ == '__main__':

    sg = select_shapes_graph()

    start = time.time()
    main(sg)
    end = time.time()

    print("Runtime: ", end - start)