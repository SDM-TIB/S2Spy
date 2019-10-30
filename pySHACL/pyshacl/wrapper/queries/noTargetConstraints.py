from utils import lastStringURL

def query_no_target():
    return '''SELECT DISTINCT ?s ?c ?path
        WHERE {
            ?s rdf:type sh:NodeShape.
            ?s sh:property ?p.
            ?p sh:path ?path
        }'''

def nt_construct_query(evaluated_query):
    subjs = []
    props = []

    for row in evaluated_query:
        if row[1] is not None:
            node = lastStringURL(row[1])
            subjs.append({"sub": "<" + str(row[1]) + ">", "var_name": "?" + node[1]})
        else:
            subjs.append({"sub": None, "var_name": "?s"})

        prop = lastStringURL(row[2])
        props.append({"prop": "<" + str(row[2]) + ">", "var_name": "?" + prop[1]})

    triples = ""

    for i, s in enumerate(subjs):
        if s["sub"] is not None:
            triples += s["var_name"] + " a " + s["sub"] + ".\n"

    for i, p in enumerate(props):
        triples += subjs[i]["var_name"] + p["prop"] + p["var_name"] + ".\n"

    query = "CONSTRUCT {\n" + triples + "}\n" + \
                "WHERE {\n" + triples + "}"

    return query
