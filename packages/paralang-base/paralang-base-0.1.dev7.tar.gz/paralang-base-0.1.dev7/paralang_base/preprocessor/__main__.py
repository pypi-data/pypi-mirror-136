# coding=utf-8
"""
File containing the functions and class for the Pre-Processor parsing process
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Dict

import antlr4

from .error_handler import PreProcessorErrorListener
from .parser.ParaPreProcessorLexer import ParaPreProcessorLexer
from .parser.ParaPreProcessorParser import ParaPreProcessorParser
from ..exceptions import ParaSyntaxErrorCollection

if TYPE_CHECKING:
    from .ctx import ProgramPreProcessorContext, FilePreProcessorContext

__all__ = [
    'PreProcessor',
    'PreProcessorProcessResult'
]

logger = logging.getLogger(__name__)


class PreProcessorProcessResult:
    """
    The result of a Pre-Processor Execution for a Program. Contains the
    modified files, pragmas and general information collected by the
    Pre-Processor
    """

    def __init__(
            self,
            origin: ProgramPreProcessorContext
    ):
        self.origin = origin

    def generated_files(self) -> Dict[str, Dict[str, FilePreProcessorContext]]:
        """
        Returns the generated files, which are represented in a dictionary.

        :returns:
          (
            str - Name of the file (Relative name),
            (
              str - The code-string,
              FilePreProcessorContext - The context of the file
            )
          )
        """

        # TODO! Return the generated files and properly process
        ...


class PreProcessor:
    """
    The Pre-Processor, which handles directives in a Para file.

    The incoming files will be tokenized and parsed using Antlr4. The generated
    parse tree will be used by the Pre-Processor listener to generate a
    FilePreProcessorContext instance for the file and then process everything
    appropriately with the ProgramPreProcessorContext. After generation, the
    preprocessor will walk through and modify the file based on the directives
    contained in the logic stream.

    The output will be a file-stream / str, which can be used to write to a
    file or parsed to the main Para compiler for further processing.
    """

    @staticmethod
    async def parse(
            input_stream: antlr4.InputStream,
            prefer_logging: bool = True
    ) -> ParaPreProcessorParser.CompilationUnitContext:
        """
        Parses the passed input_stream using antlr4 and returns the
        compilation unit context which can be used with the listener to
        process the file and generate a logic stream

        :param input_stream: The token stream of the file
        :param prefer_logging: If set to True errors, warnings and
         info will be logged onto the console using the local logger instance.
         If an exception is raised or error is encountered, it will be reraised
         with the FailedToProcessError.
        :returns: The compilationUnit (file) context
        """
        # Error handler which uses the default error strategy to handle the
        # incoming antlr4 errors
        error_listener = PreProcessorErrorListener()

        # Initialising the lexer, which will tokenize the input_stream and
        # raise basic errors if needed
        lexer = ParaPreProcessorLexer(input_stream)
        lexer.removeErrorListeners()
        lexer.addErrorListener(error_listener)

        logger.debug("Lexing file and generating tokens")

        # Parsing the lexer and generating a token stream
        stream = antlr4.CommonTokenStream(lexer)

        logger.debug("Parsing the tokens and generating the parse tree")
        # Parser which generates based on the top entry rule the parse tree
        parser = ParaPreProcessorParser(stream)
        parser.removeErrorListeners()
        parser.addErrorListener(error_listener)
        logger.debug("Finished generation of compilationUnit for the file")

        # Parsing from the entry - compilationUnit
        cu = parser.compilationUnit()

        # Raise one or multiple errors if they were caught during the parsing
        if len(error_listener.errors) > 0:
            raise ParaSyntaxErrorCollection(
                error_listener.errors,
                prefer_logging
            )  # Raising the syntax error/s

        return cu

    @staticmethod
    async def process_directives(
            ctx: ProgramPreProcessorContext,
            prefer_logging: bool = True
    ) -> PreProcessorProcessResult:
        """
        Processing the directives in the passed ctx and generate an altered
        PreProcessorProcessResult. This function will process the directives
        of all PreProcessorContext files and alter the files appropriately.

        :param ctx: The context instance containing the context instances for
         the directives.
        :param prefer_logging: If set to True errors, warnings and
         info will be logged onto the console using the local logger instance.
         If an exception is raised or error is encountered, it will be reraised
         with the FailedToProcessError.
        :returns: A result that is represented in a PreProcessorProcessResult,
         containing the altered files.
        """
        # TODO! Add proper logic to process the directives from the
        #  logic-stream - ctx.process_directives()

        return PreProcessorProcessResult(ctx)
