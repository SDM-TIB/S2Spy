# -*- coding: latin-1 -*-

from pyshacl.validate import validate, Validator
from pyshacl.wrapper.fetch import graph_query_result, get_target
from pyshacl.wrapper.SHACLtoConstructQuery import get_construct_query

# version compliant with https://www.python.org/dev/peps/pep-0440/
__version__ = '0.9.11'

__all__ = ['validate', 'Validator',
           'graph_query_result', 'get_target', 'get_construct_query',
           '__version__']
