# -*- coding: utf-8 -*-
from sys import stderr
import logging

from pyshacl.shacl_graph import SHACLGraph
from pyshacl.rdfutil import load_from_source

log_handler = logging.StreamHandler(stderr)
log = logging.getLogger(__name__)
for h in log.handlers:
    log.removeHandler(h)  # pragma:no cover
log.addHandler(log_handler)
log.setLevel(logging.INFO)
log_handler.setLevel(logging.INFO)


def graph_query_result(shacl_graph, query, **kwargs):
    shacl_graph_format = kwargs.pop('shacl_graph_format', None)
    do_owl_imports = kwargs.pop('do_owl_imports', False)

    if shacl_graph is not None:
        shacl_graph = load_from_source(shacl_graph,
                                       rdf_format=shacl_graph_format,
                                       do_owl_imports=do_owl_imports)
    qres = shacl_graph.query(query)

    return qres


def get_target(shacl_graph, **kwargs):
    shacl_graph_format = kwargs.pop('shacl_graph_format', None)
    do_owl_imports = kwargs.pop('do_owl_imports', False)

    if shacl_graph is not None:
        shacl_graph = load_from_source(shacl_graph,
                                       rdf_format=shacl_graph_format,
                                       do_owl_imports=do_owl_imports)
    sg = SHACLGraph(shacl_graph)

    for s in sg.shapes:
        (target_nodes, target_classes, implicit_classes,
         target_objects_of, target_subjects_of) = s.target()

        for n in iter(target_nodes):
            return ("n", n)

        for tc in iter(target_classes):
            return ("tc", tc)

        for s_of in iter(target_subjects_of):
            return ("s_of", s_of)

        for o_of in iter(target_objects_of):
            return ("o_of", o_of)

    return ''