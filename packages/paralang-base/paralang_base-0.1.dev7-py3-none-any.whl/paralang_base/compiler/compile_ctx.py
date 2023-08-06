# coding=utf-8
"""
File containing the classes which will be used to track and run a compilation.
The context classes will track variables, stack, logic and general compiling
information.
"""
from __future__ import annotations

import logging
from pathlib import Path
from os import PathLike
from typing import Dict, Union, List, Optional

import antlr4

from .parse_stream import ParaQualifiedParseStream
from .parser import ParaParser, Listener
from ..abc import FileRunContext, ProgramRunContext
from ..util import get_input_stream

__all__ = [
    'FileCompilationContext',
    'ProgramCompilationContext'
]

logger = logging.getLogger(__name__)


class FileCompilationContext(FileRunContext):
    """
    Class used inside the listener for managing the context of a single file,
    which will keep track of variables, the stack, logic and
    general compiling information which is only related to the specified file.

    Note that unknown identifiers will not count as an error, since they
    might be from another file that is included.

    Dependencies will be managed using the CompilationContext, which will keep
    track of all files and in the end process the resulting dependencies and
    whether they work. (-> Linker and Semantic Analysis)
    """

    def __init__(
            self,
            antlr4_file_ctx: ParaParser.CompilationUnitContext,
            program_ctx: ProgramCompilationContext,
            relative_file_name: str
    ):
        listener = Listener(antlr4_file_ctx)
        super().__init__(
            antlr4_file_ctx=antlr4_file_ctx,
            listener=listener,
            program_ctx=program_ctx,
            relative_file_name=relative_file_name
        )

    @property
    def antlr4_file_ctx(self) -> ParaParser.CompilationUnitContext:
        """
        The antlr4 file ctx, which represents the entire file in a logic
        tree made up of tokens
        """
        return self._antlr4_file_ctx

    @property
    def listener(self) -> Listener:
        """
        The listener for this class responsible for walking through all code
        items and properly generating a logic stream, where all items may be
        compiled
        """
        return self._listener

    @property
    def program_ctx(self) -> ProgramCompilationContext:
        """
        The program context that is owner of this file and contains the overall
        project configuration.
        """
        return self._program_ctx

    @property
    def relative_file_name(self) -> str:
        """
        Returns the relative file name, which goes out from the entry file
        and has a relative path to every file imported and used.
        """
        return self._relative_file_name

    @property
    def parse_stream(self) -> Optional[ParaQualifiedParseStream]:
        """
        Returns the logic stream for this file ctx.

        For this getter to work, it has to be generated first using
        'await get_parse_stream()', which will per default automatically
        set a cache variable for the logic stream.

        If it has not been run yet, it will return None.
        """
        return super().parse_stream

    async def get_parse_stream(
            self, prefer_logging: bool
    ) -> ParaQualifiedParseStream:
        """
        Runs the listener assigned of this instance and walks through all
        items in the parse tree to generate a parse stream, which contains the
        most vital items for the compilation. This stream may then be used
        to properly compile a program.

        :param prefer_logging: If set to True errors, warnings and
         info will be logged onto the console using the local logger instance.
         If an exception is raised or error is encountered, it will be reraised
         with the FailedToProcessError.
        """
        self._parse_stream = await self.listener.walk(prefer_logging)
        return self._parse_stream


class ProgramCompilationContext(ProgramRunContext):
    """
    Program Compilation Context, which serves as the base for the compilation
    of an entire program containing possibly more than one file. Holds the
    entire context of the program and is used in the linker and last step of
    semantic analysis to validate the program.
    """

    def __init__(
            self,
            files: List[Union[str, bytes, PathLike, Path]],
            project_root: Union[str, bytes, PathLike, Path],
            encoding: str
    ):
        super().__init__(files, project_root, encoding)
        self._context_dict: Dict[
            Union[str, bytes, PathLike, Path], FileCompilationContext
        ] = {}

    @property
    def files(self) -> List[Path]:
        """ Returns the source files for the process """
        return self._files

    @property
    def project_root(self) -> Path:
        """
        Returns the working directory / base-path for the program. If the entry
        file path was relative, then the working directory where the compiler
        is run is used as the working directory.
        """
        return self._project_root

    @property
    def encoding(self) -> str:
        """ Returns the encoding of the project """
        return super().encoding

    @property
    def context_dict(self) -> Dict[
        Union[str, bytes, PathLike, Path], FileCompilationContext
    ]:
        """
        Returns a list for all context instances. The key is a relative path
        name to the FileContext
        """
        return self._context_dict

    def add_file_ctx(
            self,
            ctx: FileCompilationContext,
            relative_file_name: str
    ) -> None:
        """
        Adds a FileCompilationContext to the list of file ctx instances.
        The context instance should only be created using this class
        """
        self._context_dict[relative_file_name] = ctx

    async def gen_source(self) -> Dict[str, Dict[str, FileCompilationContext]]:
        """
        Generates the source C-code from the tokens stored inside the class.

        :returns: If the dict is returned, the items will be as followed: Name
         of the file (Relative name), The code-string, The compilation context
         of the file.
        """
        raise NotImplementedError()

    async def process_program(self, prefer_logging: bool) -> None:
        """
        Processes this instance and generates the Parse Stream required
        for generating the finished code.

        :param prefer_logging: If set to True errors, warnings and
         info will be logged onto the console using the local logger instance.
         If an exception is raised or error is encountered, it will be reraised
         with the FailedToProcessError.
        """
        raise NotImplementedError()
        # TODO! Run listener for every file

    async def parse_file(
            self,
            file_path: Union[str, PathLike, Path],
            prefer_logging: bool
    ) -> FileCompilationContext:
        """
        Gets a FileStream, converts it to a string stream and parses it
        returning the resulting FilePreProcessorContext

        :param file_path: Path to the file
        :param prefer_logging: If set to True errors, warnings and
         info will be logged onto the console using the local logger instance.
         If an exception is raised or error is encountered, it will be reraised
         with the FailedToProcessError.
        :returns: The FilePreProcessorContext instance for the file
        """
        from .compiler import ParaCompiler
        from ..util import (get_file_stream, get_relative_file_name)

        if type(file_path) is not Path:
            file_path: Path = Path(str(file_path)).resolve()

        file_stream: antlr4.FileStream = get_file_stream(
            file_path, self.encoding
        )
        relative_file_name: str = get_relative_file_name(
            file_name=file_stream.name,
            file_path=file_stream.fileName,
            base_path=self.project_root
        )
        stream: antlr4.InputStream = get_input_stream(
            # rm comments
            ParaCompiler.remove_comments_from_str(file_stream.strdata),
            name=file_stream.name
        )
        return await self.parse_stream(
            stream, relative_file_name, prefer_logging
        )

    async def parse_stream(
            self,
            stream: antlr4.InputStream,
            relative_file_name: str,
            prefer_logging: bool,
    ) -> FileCompilationContext:
        """
        Parses a single file based on the passed stream and
        generates the FilePreProcessorContext

        :param stream: The Antlr4 InputStream which represents a string stream
        :param relative_file_name: Relative name of the file (fetch-able using
         get_relative_file_name)
        :param prefer_logging: If set to True errors, warnings and
         info will be logged onto the console using the local logger instance.
         If an exception is raised or error is encountered, it will be reraised
         with the FailedToProcessError.
        :returns: The generated FilePreProcessorContext instance
        """
        from .compiler import ParaCompiler

        logger.debug(f"Parsing file ({relative_file_name})")
        antlr4_file_ctx = await ParaCompiler.parse(
            stream, prefer_logging
        )

        file_ctx = FileCompilationContext(
            antlr4_file_ctx, self, relative_file_name
        )
        await file_ctx.get_parse_stream(prefer_logging)
        return file_ctx

    async def parse_all_files(
            self, prefer_logging: bool
    ) -> List[FileCompilationContext]:
        """
        Parses all files, and generates the Parse Stream for them

        :param prefer_logging: If set to True errors, warnings and
         info will be logged onto the console using the local logger instance.
         If an exception is raised or error is encountered, it will be reraised
         with the FailedToProcessError.
        """
        return list(
            await self.parse_file(
                str(file.absolute()), prefer_logging
            ) for file in self.files
        )
