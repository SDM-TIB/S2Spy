# -*- coding: utf-8 -*-
prefixes = {
    "dbo": "<http://dbpedia.org/ontology/>",
    "dbr": "<http://dbpedia.org/resource/>",
    "yago": "<http://dbpedia.org/class/yago/>",
    "foaf": "<http://xmlns.com/foaf/0.1/>",
    "": "<http://example.org/>"
}

prefixString = "\n".join(["".join("PREFIX " + key + ":" + value) for (key, value) in prefixes.items()]) + "\n"

def getPrefixString():
    return prefixString
