from utils import lastStringURL

def query_no_target():
    return '''SELECT DISTINCT ?s ?c ?path
        WHERE {
            ?s rdf:type sh:NodeShape.
            ?s sh:property ?p.
            ?p sh:path ?path
        }'''

def nt_construct_query(evaluated_query, option='select'):
    subjs = set()
    props = []
    vars = set()

    for row in evaluated_query:
        if row[1] is not None:  # since there is no targetClass related
            node = lastStringURL(row[1])
            subj_var = "?" + node[1]
            subjs.add(subj_var + " <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> " + " <" + str(row[1]) + ">.\n")
        else:
            subj_var = "?s"

        vars.add(subj_var)

        prop = lastStringURL(row[2])
        props.append({"subj_var": subj_var,
                      "prop": "<" + str(row[2]) + ">",
                      "var_name": "?" + prop[1]})

    triples = ""

    for s in subjs:
        triples += s

    for i, p in enumerate(props):
        triples += ' '.join([p["subj_var"], p["prop"], p["var_name"], ".\n"])

    if option == 'construct':
        return "CONSTRUCT {\n" + triples + "}\n" + \
                "WHERE {\n" + triples + "}"
    else:
        return "SELECT " + ' '.join(vars) + \
               " WHERE {\n" + triples + "}\n"