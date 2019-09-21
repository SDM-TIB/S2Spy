from utils import lastStringURL

def query_node():
    query_n_node = '''SELECT DISTINCT ?node
    WHERE {
        ?s rdf:type sh:NodeShape.
        ?s sh:targetNode ?node.
        ?s sh:property ?p.
        ?p sh:path ?path.
        OPTIONAL { ?p sh:class ?c }
    } 
    '''

    query_n_path = '''SELECT DISTINCT ?path
    WHERE {
        ?s rdf:type sh:NodeShape.
        ?s sh:targetNode ?node.
        ?s sh:property ?p.
        ?p sh:path ?path.
    } 
    '''

    return (query_n_node, query_n_path)


def tn_construct_query(subjs, preds):
    subjs = [row[0] for row in subjs]
    preds = [row[0] for row in preds]

    filter = ''
    filter += "FILTER (?s IN ("
    for i, s in enumerate(subjs):
        filter += "<" + s + ">"
        if i < len(subjs) - 1:
            filter += ", "
    filter += "))"

    objs = []
    for row in preds:
        objs.append("?" + lastStringURL(row)[1])

    triples = ""
    for i, elem in enumerate(preds):
        triples += "?s" + " <" + elem + "> " + objs[i] + ".\n"

    query = "CONSTRUCT {\n" + triples + "}\n" + \
            "WHERE {\n" + \
            triples + "\n" + \
            filter + "\n" + \
            "}"

    return query
