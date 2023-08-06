"""
Mathematical morphology
"""

from .se import make_structuring_element_2d
from .soperations import *
from .component_tree import maxtree, tos, ComponentTree
from .watershed import watershed

__all__ = [
    "make_structuring_element_2d",
    "erosion",
    "dilation",
    "opening",
    "closing",
    "gradient",
    "maxtree",
    "ComponentTree",
    "tos",
    "watershed",
]
