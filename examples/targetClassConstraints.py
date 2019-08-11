from utils import lastStringURL

def query_class():
    return '''SELECT DISTINCT ?s ?c ?path
    WHERE {
        ?s rdf:type sh:NodeShape.
        ?s sh:targetClass ?c.
        ?s sh:property ?p.
        ?p sh:path ?path
    }'''


def tc_construct_query(evaluated_query):
    prefixes = []
    subjs = []
    attrs = []

    for row in evaluated_query:
        node = lastStringURL(row[1])
        attr = lastStringURL(row[2])

        prefixes.append(node[0] + '/')
        subjs.append(node[1])
        attrs.append(attr[1])

    triples = ""
    triples += "?s" + " " + "a" + " <" + prefixes[0] + subjs[0] + ">.\n"

    for i, o in enumerate(attrs):
        triples += "?s" + " <" + prefixes[i] + o + "> " + "?" + o + ".\n"

    query = "CONSTRUCT {\n" + triples + "}\n" + \
                "WHERE {\n" + triples + "}"

    return query


# Example queries

'''
CONSTRUCT 
{
    ?s a <http://project-iasis.eu/vocab/LCPatient>.
	?s <http://project-iasis.eu/vocab/smoking> ?smoker.
	?s <http://project-iasis.eu/vocab/numberOfCigarettesPerYear> ?numbCigarettes.
}

WHERE {
    ?s a <http://project-iasis.eu/vocab/LCPatient>.
	?s <http://project-iasis.eu/vocab/smoking> ?smoker.
    ?s <http://project-iasis.eu/vocab/numberOfCigarettesPerYear> ?numbCigarettes.
}
'''

'''
CONSTRUCT 
{
	?s <http://project-iasis.eu/vocab/smoking> ?smoker.
	?s <http://project-iasis.eu/vocab/numberOfCigarettesPerYear> ?numbCigarettes.
}

WHERE {
	?s <http://project-iasis.eu/vocab/smoking> ?smoker.
    ?s <http://project-iasis.eu/vocab/numberOfCigarettesPerYear> ?numbCigarettes.

	FILTER (?s IN (<http://project-iasis.eu/LCPatient/1007602>, <http://project-iasis.eu/LCPatient/1022857>))
}
'''


######## targetObjectsOf ########

'''
CONSTRUCT {
    ?s ?p ?o.
}

WHERE {
    ?x <http://project-iasis.eu/vocab/hasOncologicalTreatmentLine> ?s.
    ?s ?p ?o.
}
'''