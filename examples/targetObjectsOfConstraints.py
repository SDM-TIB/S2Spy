from utils import lastStringURL

def query_o_of():
    return '''SELECT DISTINCT ?s ?c ?path
    WHERE {
        ?s rdf:type sh:NodeShape.
        ?s sh:targetObjectsOf ?c.
        ?s sh:property ?p.
        ?p sh:path ?path
    }'''

def to_of_construct_query(evaluated_query, target_value):
    objs = []
    preds = []
    for row in evaluated_query:
        objs.append("?" + lastStringURL(row[2])[1])
        preds.append(row[2])

    triples = ""
    for i, o in enumerate(objs):
        triples += "?o" + " <" +  preds[i] + "> " + o + ".\n"


    query = "CONSTRUCT {\n" + \
                triples + "}\n" + \
            "WHERE { \n" \
                "?s <" + target_value + "> ?o.\n" + \
                triples + "\n" + \
            "}\n"

    return query