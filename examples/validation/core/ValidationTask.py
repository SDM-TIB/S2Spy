# -*- coding: utf-8 -*-
__author__ = "Philipp D. Rohde"

from enum import Enum


class ValidationTask(Enum):
    """This enum is used to specify the task that needs to be performed."""
    GRAPH_VALIDATION = "check wether the whole graph is valid"
    SHAPE_VALIDATION = "check which shapes are valid"
    INSTANCES_VALID = "report the valid instances"
    INSTACES_VIOLATION = "report the instances that violate at least one constraint"
