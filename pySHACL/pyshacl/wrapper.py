# -*- coding: utf-8 -*-

from pyshacl.rdfutil import load_from_source

def graph_query_result(shacl_graph, query, **kwargs):
    shacl_graph_format = kwargs.pop('shacl_graph_format', None)
    do_owl_imports = kwargs.pop('do_owl_imports', False)

    if shacl_graph is not None:
        shacl_graph = load_from_source(shacl_graph,
                                       rdf_format=shacl_graph_format,
                                       do_owl_imports=do_owl_imports)
    qres = shacl_graph.query(query)

    return qres