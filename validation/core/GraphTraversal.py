# -*- coding: utf-8 -*-
__author__ = "Philipp D. Rohde"

from enum import Enum


class GraphTraversal(Enum):
    """This enum is used to specify the algorithm used for graph traversal."""
    BFS = "Breadth-first search"
    DFS = "Depth-first search"

    def traverse_graph(self, dependencies, reversed_dependencies, starting_point):
        visited = []
        if self == GraphTraversal.DFS:
            self.__dfs__(visited, dependencies, reversed_dependencies, starting_point)
        # TODO: implement BFS
        return visited

    def __dfs__(self, visited, dependencies, reversed_dependencies, node):
        """Implementation of depth-first search with the ability to go back
        if the algorithm is in a sink but there are still unvisited nodes."""
        if node not in visited:
            visited.append(node)
            for neighbour in dependencies[node]:
                self.__dfs__(visited, dependencies, reversed_dependencies, neighbour)
            if sorted(visited) != sorted(dependencies.keys()):
                for neighbour in reversed_dependencies[node]:
                    self.__dfs__(visited, dependencies, reversed_dependencies, neighbour)
        elif node in visited and sorted(visited) != sorted(dependencies.keys()):
            for neighbour in dependencies[node]:
                if neighbour not in visited:
                    self.__dfs__(visited, dependencies, reversed_dependencies, neighbour)
            for neighbour in reversed_dependencies[node]:
                self.__dfs__(visited, dependencies, reversed_dependencies, neighbour)
