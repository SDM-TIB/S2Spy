from utils import lastStringURL

def query_class():
    return '''SELECT DISTINCT ?s ?c ?path
    WHERE {
        ?s rdf:type sh:NodeShape.
        ?s sh:targetClass ?c.
        ?s sh:property ?p.
        ?p sh:path ?path
    }'''

def query_class_inner_nodes():
    return '''SELECT DISTINCT ?node ?path ?path2
    WHERE {
        ?s rdf:type sh:NodeShape.
        ?s sh:property ?prop.
        ?prop sh:path ?path.
        ?prop sh:node ?node.

        ?node2 rdf:type sh:NodeShape.
        ?node2 sh:property ?prop2.
        ?prop2 sh:path ?path2.

        FILTER (?node2 = ?node)
    }'''

def tc_construct_query(evaluated_query, inner_nodes):
    prefixes = []
    subjs = []
    attrs = []

    inner_triples = ''
    for row in inner_nodes:
        pred = lastStringURL(row[1])[1]
        obj = lastStringURL(row[2])[1]

        inner_triples += "?" + pred + " <" + str(row[2]) + "> ?" + obj + ".\n"

    for row in evaluated_query:
        node = lastStringURL(row[1])
        obj = lastStringURL(row[2])

        prefixes.append(node[0] + '/')
        subjs.append(node[1])
        attrs.append(obj[1])

    triples = ""
    triples += "?s" + " " + "a" + " <" + prefixes[0] + subjs[0] + ">.\n"

    for i, o in enumerate(attrs):
        triples += "?s" + " <" + prefixes[i] + o + "> " + "?" + o + ".\n"

    query = "CONSTRUCT {\n" + triples + inner_triples + "}\n" + \
                "WHERE {\n" + triples + inner_triples + "}"

    return query