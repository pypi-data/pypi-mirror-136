# coding=utf-8
""" Logic Stream for Pre-Processor Items """
from typing import List, Any
from cached_property import cached_property

from .abc import PreProcessorParseToken
from .parse_tokens import NonPreProcessorItem
from ..abc import ParseStream


class PreProcessorParseStream(ParseStream):
    """
    Pre-Processor Stream, which represents a list of PreProcessorParseToken
    which may contain NonPreProcessorItem as their children, e.g.:

    #if defined(M)
    // Associated NonPreProcessorItem Block for the above Selection Directive
    #endif

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def content(self) -> List[PreProcessorParseToken]:
        """
        Returns the content of the list. Type-hinted alias for list(self).

        Only contains the pure content
        """
        return list(self)

    def get_start(self) -> PreProcessorParseToken:
        """ Gets the first item of the stream """
        return self[0]

    def get_end(self) -> PreProcessorParseToken:
        """ Gets the last item of the stream """
        return self[-1]

    def append_antlr_ctx(self, _ctx: Any) -> None:
        """ Appends a new ctx instance to the stream """
        super().append_antlr_ctx(_ctx)


class ProcessedFileStream(ParseStream):
    """
    Processed File Stream representing a file that was already processed and
    does not contain directives anymore, but only processed code
    (NonPreProcessorItem).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @cached_property
    def file_string(self) -> str:
        """
        File-string, which is the merged version of the content of this stream
        """
        ...

        return str()

    @property
    def content(self) -> List[NonPreProcessorItem]:
        """
        Returns the content of the list. Type-hinted alias for list(self).

        Only contains the pure content
        """
        return list(self)

    def get_start(self) -> NonPreProcessorItem:
        """ Gets the first item of the stream """
        return self[0]

    def get_end(self) -> NonPreProcessorItem:
        """ Gets the last item of the stream """
        return self[-1]

    def append_antlr_ctx(self, _ctx: Any) -> None:
        """ Appends a new ctx instance to the stream """
        super().append_antlr_ctx(_ctx)
