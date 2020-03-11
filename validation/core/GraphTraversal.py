# -*- coding: utf-8 -*-
__author__ = "Philipp D. Rohde"

from enum import Enum


class GraphTraversal(Enum):
    """This enum is used to specify the algorithm used for graph traversal."""
    BFS = "Breadth-first search"
    DFS = "Depth-first search"
