# -*- coding: utf-8 -*-
__author__ = "Monica Figuera and Philipp D. Rohde"

import collections
import json
import os
from itertools import islice
from urllib.parse import urlparse

import rdflib.term
from rdflib import Graph

from SHACL2SPARQLpy.Shape import Shape
from SHACL2SPARQLpy.VariableGenerator import VariableGenerator
from SHACL2SPARQLpy.constraints.MaxOnlyConstraint import MaxOnlyConstraint
from SHACL2SPARQLpy.constraints.MinOnlyConstraint import MinOnlyConstraint
from SHACL2SPARQLpy.utils.globals import PARSING_ORDER

QUERY_TARGET_QUERY = '''SELECT ?query WHERE {{
  <{shape}> a <http://www.w3.org/ns/shacl#NodeShape> ;
      <http://www.w3.org/ns/shacl#targetQuery> ?query .
}}'''


class ShapeParser:

    def __init__(self):
        return

    def parseShapesFromDir(self, path, shapeFormat, useSelectiveQueries, maxSplitSize, ORDERBYinQueries):
        fileExtension = self.getFileExtension(shapeFormat)
        filesAbsPaths = []
        # r=root, d=directories, f = files
        for r, d, f in os.walk(path):
            for file in f:
                if fileExtension in file:
                    filesAbsPaths.append(os.path.join(r, file))

        if not filesAbsPaths:
            raise FileNotFoundError(path + " does not contain any shapes of the format " + shapeFormat)

        if shapeFormat == "JSON":
            return [self.parseJson(p, useSelectiveQueries, maxSplitSize, ORDERBYinQueries) for p in filesAbsPaths]
        elif shapeFormat == "SHACL":
            shapes = []
            [shapes.extend(self.parseTtl(p, useSelectiveQueries, maxSplitSize, ORDERBYinQueries)) for p in filesAbsPaths]
            return shapes
        else:
            print("Unexpected format: " + shapeFormat)

    def getFileExtension(self, shapeFormat):
        if shapeFormat == "SHACL":
            return ".ttl"
        else:
            return ".json"  # dot added for convenience

    def parseJson(self, path, useSelectiveQueries, maxSplitSize, ORDERBYinQueries):
        targetQuery = None

        file = open(path, "r")
        obj = json.load(file)
        targetDef = obj.get("targetDef")

        name = obj["name"]
        PARSING_ORDER.append(name)
        id = name + "_d1"  # str(i + 1) but there is only one set of conjunctions
        constraints = self.parseConstraints(name, obj["constraintDef"]["conjunctions"], targetDef, id)

        includeSPARQLPrefixes = self.abbreviatedSyntaxUsed(constraints)
        prefixes = None
        if "prefix" in obj.keys():
            prefixes = obj["prefix"]
        prefix_string = ''
        if prefixes:
            prefix_string = "\n".join(["".join("PREFIX " + key + ": " + value) for (key, value) in prefixes.items()]) + "\n"
        referencedShapes = self.shapeReferences(obj["constraintDef"]["conjunctions"][0])

        if targetDef is not None:
            query = targetDef["query"]
            if query is not None:
                targetQuery = ''.join([prefix_string if includeSPARQLPrefixes else '', query])
            if urlparse(targetDef["class"]).netloc != '':  # if the target class is a url, add '<>' to it
                targetDef = '<' + targetDef["class"] + '>'
            else:
                targetDef = targetDef["class"]

        return Shape(name, targetDef, targetQuery, constraints, id, referencedShapes,
                     useSelectiveQueries, maxSplitSize, ORDERBYinQueries, includeSPARQLPrefixes, prefix_string)

    def parseTtl(self, path, useSelectiveQueries, maxSplitSize, ORDERBYinQueries):
        # This is a copy of the TTL shape parser of Trav-SHACL
        g_file = Graph()  # create graph instance
        g_file.parse(path)

        queries = self.get_QUERY()
        shapes = []

        names = [str(row[0]) for row in g_file.query(queries[0])]

        for name in names:
            id_ = name + '_d1'  # str(i + 1) but there is only one set of conjunctions

            # to get the target_ref and target_type
            target_def = None
            target_type = None
            if len(g_file.query(queries[1].format(shape=name))) != 0:
                for res in g_file.query(queries[1].format(shape=name)):
                    target_def = str(res[0])
                    target_type = 'class'
                    break
            elif len(g_file.query(queries[2].format(shape=name))) != 0:
                for res in g_file.query(queries[2].format(shape=name)):
                    target_def = str(res[0])
                    target_type = 'node'
                    break

            target_query = None
            if target_def is not None and target_type == 'class':
                for res in g_file.query(QUERY_TARGET_QUERY.format(shape=name)):
                    target_query = str(res[0])
                if target_query is None:
                    target_query = 'SELECT ?x WHERE { ?x a <' + target_def + '> }'  # come up with a query for this
                    if urlparse(target_def).netloc != '':  # if the target node is a url, add '<>' to it
                        target_def = '<' + target_def + '>'

            cons_dict = self.parse_all_const(g_file, name=name, target_def=target_def,
                                             target_type=target_type, query=queries)

            const_array = list(cons_dict.values())  # change the format to an array
            constraints = self.parse_constraints_ttl(const_array, target_def, id_)

            include_sparql_prefixes = False
            prefixes = ''
            referenced_shapes = self.shapeReferences(const_array)

            # helps to navigate the shape.__compute_target_queries function
            referenced_shape = {'<' + key + '>': '<' + referenced_shapes[key] + '>'
                                for key in referenced_shapes.keys()
                                if urlparse(referenced_shapes[key]).netloc != ''}

            # to helps to navigate the ShapeSchema.compute_edges function
            if urlparse(name).netloc != '':
                name_ = '<' + name + '>'
            else:
                name_ = name

            PARSING_ORDER.append(name_)
            shapes.append(Shape(name_, target_def, target_query, constraints, id_, referenced_shape,
                                useSelectiveQueries, maxSplitSize, ORDERBYinQueries, include_sparql_prefixes, prefixes))

        return shapes

    def abbreviatedSyntaxUsed(self, constraints):
        """
        Run after parsingConstraints.
        Returns false if the constraints' predicates are using absolute paths instead of abbreviated ones
        :param constraints: all shape constraints
        :return:
        """
        for c in constraints:
            if c.path.startswith("<") and c.path.endswith(">"):
                return False
        return True

    def shapeReferences(self, constraints):
        return {c.get("shape"): c.get("path") for c in constraints if c.get("shape") is not None}

    @staticmethod
    def get_QUERY():
        QUERY_SHAPES = '''SELECT DISTINCT ?shape WHERE {
                ?shape a <http://www.w3.org/ns/shacl#NodeShape> .
                }'''

        QUERY_TARGET_1 = '''SELECT ?target WHERE {{
                <{shape}> a <http://www.w3.org/ns/shacl#NodeShape> .
                <{shape}> <http://www.w3.org/ns/shacl#targetClass> ?target .
            }}
            '''

        QUERY_TARGET_2 = '''SELECT ?target WHERE {{
                        <{shape}> a <http://www.w3.org/ns/shacl#NodeShape> .
                        <{shape}> <http://www.w3.org/ns/shacl#targetNode> ?target .
                    }}
                    '''

        QUERY_CONSTRAINTS = '''SELECT ?constraint WHERE {{
              <{shape}> a <http://www.w3.org/ns/shacl#NodeShape> .
              <{shape}> <http://www.w3.org/ns/shacl#property> ?constraint .
            }}
            '''

        QUERY_CONSTRAINT_DETAILS = '''SELECT ?p ?o WHERE {{
              ?s ?p ?o .
              FILTER( str(?s) = "{constraint}" )
            }}'''

        QUERY_QVS_REF_1 = '''SELECT ?shape_ref WHERE {{
                  ?s <http://www.w3.org/ns/shacl#node> ?shape_ref .
                  FILTER ( str(?s) = "{qvs}" )
                }}'''

        QUERY_QVS_REF_2 = '''SELECT ?shape_ref WHERE {{
                      ?s <http://www.w3.org/ns/shacl#value> ?shape_ref .
                      FILTER ( str(?s) = "{qvs}" )
                    }}'''

        QUERY_SPARQL_CONSTRAINTS = '''SELECT ?constraint ?query WHERE {{
              <{shape}> a <http://www.w3.org/ns/shacl#NodeShape> .
              <{shape}> <http://www.w3.org/ns/shacl#sparql> ?constraint .
              ?constraint <http://www.w3.org/ns/shacl#select> ?query .
            }}
            '''
        return QUERY_SHAPES, QUERY_TARGET_1, QUERY_TARGET_2, QUERY_CONSTRAINTS, QUERY_CONSTRAINT_DETAILS, QUERY_QVS_REF_1, QUERY_QVS_REF_2, QUERY_SPARQL_CONSTRAINTS

    def parse_all_const(self, filename, name, target_def, target_type, query):
        def get_res(filename, name, query):
            exp_dict = collections.defaultdict(list)
            for constraint in filename.query(query[3].format(shape=name)):
                constraint_id = constraint[0]

                for detail in filename.query(query[4].format(constraint=constraint_id)):

                    if isinstance(detail.asdict()['o'], rdflib.term.BNode):
                        qv_type = detail.asdict()['p']
                        qvs = detail.asdict()['o']
                        if len(filename.query(query[5].format(qvs=qvs))) != 0:
                            for shape_ref in filename.query(query[5].format(qvs=qvs)):
                                # dict_1 = [qv_type, ['shape', str(shape_ref.asdict()['shape_ref'])]]
                                dict_1 = [qv_type, str(shape_ref.asdict()['shape_ref'])]
                            exp_dict[str(constraint_id)].append(dict_1.copy())
                        else:
                            for shape_ref in filename.query(query[6].format(qvs=qvs)):
                                dict_1 = [qv_type, ['value', str(shape_ref.asdict()['shape_ref'])]]
                            exp_dict[str(constraint_id)].append(dict_1.copy())
                    else:
                        # detail_dict = detail.asdict()
                        dict_2 = [str(detail['p']), str(detail['o'])]
                        exp_dict[str(constraint_id)].append(dict_2.copy())

            return exp_dict

        def chunks(datei, SIZE):
            it = iter(datei)
            for i in range(0, len(datei), SIZE):
                yield {k: datei[k] for k in islice(it, SIZE)}

        cons_dict = get_res(filename, name, query)
        trav_dict = {}
        exp_dict = {}

        trav_dict['name'] = name
        trav_dict['target_def'] = target_def
        trav_dict['target_type'] = target_type

        # SPARQL constraints first
        for result in filename.query(query[7].format(shape=name)):
            trav_dict['sparql'] = result['query'].toPython()
            exp_dict[str(result['constraint'].toPython())] = trav_dict.copy()

        for item in chunks({i: j for i, j in cons_dict.items()}, 1):
            for dk, dv in item.items():
                if type(dk) is not tuple:

                    trav_dict['min'] = None
                    trav_dict['max'] = None
                    trav_dict['value'] = None
                    trav_dict['path'] = None
                    trav_dict['shape'] = None
                    trav_dict['datatype'] = None
                    trav_dict['negated'] = None

                    for i in dv:
                        if 'path' in str(i[0]).lower():
                            trav_dict['path'] = str(i[1])

                        if 'min' in str(i[0]).lower():
                            trav_dict['min'] = str(i[1])

                        if 'max' in str(i[0]).lower():
                            trav_dict['max'] = str(i[1])

                        if 'datatype' in str(i[0]).lower():
                            trav_dict['datatype'] = str(i[1])

                        if 'valueshape' in str(i[0]).lower():
                            trav_dict['shape'] = str(i[1])

                        if 'not' in str(i[0]).lower():
                            trav_dict['negated'] = str(i[1])

                exp_dict[str(dk)] = trav_dict.copy()

        return exp_dict

    def parse_constraints_ttl(self, array, target_def, constraints_id):
        var_generator = VariableGenerator()
        constraints = []
        [constraints.extend(self.parseConstraint(var_generator, array[i], constraints_id + '_c' + str(i + 1), target_def)) for i in range(len(array))]
        return constraints

    def parseConstraints(self, shapeName, array, targetDef, constraintsId):
        varGenerator = VariableGenerator()
        constraints = []
        [constraints.extend(self.parseConstraint(varGenerator, array[0][i], constraintsId + "_c" + str(i + 1), targetDef)) for i in range(len(array[0]))]
        return constraints

    def parseConstraint(self, varGenerator, obj, id, targetDef):
        min = obj.get("min")
        max = obj.get("max")
        shapeRef = obj.get("shape")
        datatype = obj.get("datatype")
        value = obj.get("value")
        path = obj.get("path")
        negated = obj.get("negated")

        oMin = None if (min is None) else int(min)
        oMax = None if (max is None) else int(max)
        oShapeRef = None if (shapeRef is None) else str(shapeRef)
        oDatatype = None if (datatype is None) else str(datatype)
        oValue = None if (value is None) else str(value)
        oPath = None if (path is None) else str(path)
        oNeg = True if (negated is None) else not negated  # True means it is a positive constraint

        if path is not None and urlparse(path).netloc != '':  # if the predicate is a URL, add '<>' to it
            oPath = '<' + path + '>'

        if shapeRef is not None and urlparse(shapeRef).netloc != '':  # if the shape reference is a URL, add '<>' to it
            oShapeRef = '<' + shapeRef + '>'

        if value is not None and urlparse(value).netloc != '':  # if the value reference is a URL, add '<>' to it
            oValue = '<' + value + '>'

        if datatype is not None and urlparse(datatype).netloc != '':  # if the data type is a URL, add '<>' to it
            oDatatype = '<' + datatype + '>'

        if oPath is not None:
            if oMin is not None:
                if oMax is not None:
                    # return MinMaxConstraint(varGenerator, id, oPath, oMin, oMax, oNeg, oDatatype, oValue, oShapeRef, targetDef)
                    return [
                        MinOnlyConstraint(varGenerator, id, oPath, oMin, oNeg, oDatatype, oValue, oShapeRef, targetDef),
                        MaxOnlyConstraint(varGenerator, id, oPath, oMax, oNeg, oDatatype, oValue, oShapeRef, targetDef)
                    ]
                return [MinOnlyConstraint(varGenerator, id, oPath, oMin, oNeg, oDatatype, oValue, oShapeRef, targetDef)]
            if oMax is not None:
                return [MaxOnlyConstraint(varGenerator, id, oPath, oMax, oNeg, oDatatype, oValue, oShapeRef, targetDef)]
