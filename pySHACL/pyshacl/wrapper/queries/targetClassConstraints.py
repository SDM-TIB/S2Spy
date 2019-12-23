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

def tc_query(evaluated_query, inner_nodes, option='select'):
    subjs = set()
    props = []

    inner_triples = ''
    for row in inner_nodes:
        pred = lastStringURL(row[1])[1]
        obj = lastStringURL(row[2])[1]

        inner_triples += "?" + pred + " <" + str(row[2]) + "> ?" + obj + ".\n"

    for row in evaluated_query:
        node = lastStringURL(row[1])
        subjs.add("?" + node[1] + " <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> " + " <" + str(row[1]) + ">.\n")

        prop = lastStringURL(row[2])
        props.append({"subj_var": "?" + node[1], "prop": " <" + str(row[2]) + "> ", "var": " ?" + prop[1]})


    triples = ""

    for s in subjs:
        triples += s

    for i, p in enumerate(props):
        triples += p["subj_var"] + p["prop"] + p["var"] + ".\n"

    if option == 'construct':
        return "CONSTRUCT {\n" + triples + inner_triples + "}\n" + \
                "WHERE {\n" + triples + inner_triples + "}"
    else:
        return "SELECT * WHERE {\n" + triples + inner_triples + "}\n"