from pyshacl.wrapper import graph_query_result, get_target

from pyshacl.wrapper.queries.targetClassConstraints import query_class, query_class_inner_nodes, tc_construct_query
from pyshacl.wrapper.queries.targetNodeConstraints import query_node, tn_construct_query
from pyshacl.wrapper.queries.targetSubjectsOfConstraints import query_s_of, ts_of_construct_query
from pyshacl.wrapper.queries.targetObjectsOfConstraints import query_o_of, to_of_construct_query
from pyshacl.wrapper.queries.noTargetConstraints import query_no_target, nt_construct_query

def get_construct_query(sg):
    type, target_value = get_target(sg)
    print("Target: ", type, target_value)

    if (type == "tc"):
        target_query = query_class()
        query_inner_nodes = query_class_inner_nodes()

        qres_base = graph_query_result(sg, target_query)  # data obtained from the evaluated query containing target subjects
                                                          # and predicates that I'm going to use to get the data from the endpoint
        qres_inner_nodes = graph_query_result(sg, query_inner_nodes)

        return tc_construct_query(qres_base, qres_inner_nodes)

    elif (type == "n"):
        node, prop = query_node()
        qres_nodes = graph_query_result(sg, node)
        qres_props = graph_query_result(sg, prop)

        return tn_construct_query(qres_nodes, qres_props)

    elif (type == "s_of"):
        target_query = query_s_of()
        qres = graph_query_result(sg, target_query)

        return ts_of_construct_query(target_value)

    elif (type == "o_of"):
        target_query = query_o_of()
        qres = graph_query_result(sg, target_query)

        return to_of_construct_query(qres, target_value)

    elif (type == "none"):
        query = query_no_target()
        qres = graph_query_result(sg, query)

        return nt_construct_query(qres)
