# -*- coding: utf-8 -*-
__author__ = "Philipp D. Rohde"

from validation.core.ValidationTask import ValidationTask
from validation.ShapeParser import ShapeParser
from validation.sparql.SPARQLEndpoint import SPARQLEndpoint


class ShapeNetwork:

    def __init__(self, schemaDir, schemaFormat, endpointURL, graphTraversal, validationTask, workInParallel=False):
        self.shapes = ShapeParser().parseShapesFromDir(schemaDir, schemaFormat)
        self.shapesDict = {shape.getId(): shape for shape in self.shapes}  # TODO: use only the dict?
        self.endpoint = SPARQLEndpoint(endpointURL)
        self.graphTraversal = graphTraversal
        self.validationTask = validationTask
        self.parallel = workInParallel
        self.dependencies, self.reverse_dependencies = self.computeEdges()
        self.computeInAndOutDegree()

    def getStartingPoint(self):
        """Use heuristics to determine the first shape for evaluation of the constraints."""
        # TODO
        return

    def validate(self):
        """Execute one of the validation tasks in validation.core.ValidationTask."""
        # TODO: reports
        start = self.getStartingPoint()
        node_order = self.graphTraversal.traverse_graph(self.dependencies, self.reverse_dependencies, start)
        if self.validationTask == ValidationTask.GRAPH_VALIDATION:
            isSatisfied = self.isSatisfied(node_order)
            return
        elif self.validationTask == ValidationTask.SHAPE_VALIDATION:
            shapeReport = self.shapesSatisfiable(node_order)
            return
        elif self.validationTask == ValidationTask.INSTANCES_VALID:
            # TODO
            return
        elif self.validationTask == ValidationTask.INSTACES_VIOLATION:
            # TODO
            return
        else:
            raise TypeError("Invalid validation task: " + self.validationTask)

    def computeInAndOutDegree(self):
        """Computes the in- and outdegree of each shape."""
        for s in self.shapes:
            s.outDegree = len(self.dependencies[s.getId()]) if s.getId() in self.dependencies.keys() else 0
            s.inDegree = 0
            for node in self.dependencies.keys():
                edges = self.dependencies[node]
                if s.getId() in edges:
                    s.inDegree += 1
        # TODO: is there a better/easier way to compute the indegree?
        return

    def computeEdges(self):
        """Computes the edges in the network."""
        dependencies = {s.getId(): [] for s in self.shapes}
        reverse_dependencies = {s.getId(): [] for s in self.shapes}
        for s in self.shapes:
            refs = s.getShapeRefs()
            if refs:
                name = s.getId()
                dependencies[name] = refs
                for ref in refs:
                    reverse_dependencies[ref].append(name)
        return dependencies, reverse_dependencies

    def isSatisfied(self, nodes):
        """Checks whether the graph is satisfiable or not."""
        for node in nodes:
            if not self.shapesDict[node].isSatisfied():
                return False
        return True

    def shapesSatisfiable(self, nodes):
        """Reports for each shape if it is satisfiable or not."""
        report = {}
        for node in nodes:
            report[node] = self.shapesDict[node].isSatisfied()
        return report

    def getValidInstances(self):
        """Reports all instances that validate the constraints of the graph."""
        # TODO
        return

    def getViolations(self):
        """Reports all instances that violate the constraints of the graph."""
        # TODO
        return
