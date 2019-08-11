def query_s_of():
    return '''SELECT DISTINCT ?s ?c ?path
            WHERE {
                ?s rdf:type sh:NodeShape.
                ?s sh:targetSubjectsOf ?c.
                ?s sh:property ?p.
                ?p sh:path ?path
            }'''

def ts_of_construct_query(target_value):
    query = "CONSTRUCT { ?s <" + target_value + "> ?o. }\n" \
            "WHERE { \n" \
            "?s <" + target_value + "> ?o.\n" \
            "}\n"

    return query