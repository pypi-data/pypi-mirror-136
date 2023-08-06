# coding=utf-8
"""
Para Compiler class, which is the main location, which stores functions
for parsing, compiling and handling files.
"""
from . import compile_ctx
from . import compiler
from . import error_handler
from . import parse_stream
from . import optimiser
from . import parser
from . import process
from .compile_ctx import *
from .compiler import *
from .process import *

__all__ = [
    *compiler.__all__,
    *compile_ctx.__all__,
    *process.__all__,
    *compile_ctx.__all__,
    'optimiser',
    'parser',
    'error_handler',
    'parse_stream',
    'compiler'
]

# Main-Class
ParaCompiler = compiler.ParaCompiler
