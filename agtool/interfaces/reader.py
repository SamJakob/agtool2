from abc import abstractmethod
from typing import Optional

from agtool.interfaces.plugin import AGPlugin
from agtool.struct.graph import Graph


class AGReader(AGPlugin):
    """
    Reads and parses an account graph specification, from some provided file or
    source.
    """

    @property
    @abstractmethod
    def default_file_extension(self) -> str:
        """The default file extension that this reader parses."""

    @abstractmethod
    def read_graph(self, input_source_name: str, input_data: str) -> Optional[Graph]:
        """
        Called to parse a graph in the format that this reader implements a
        parser for.

        :param input_source_name: The name of the input source (e.g., a file
        name, or a URL). This is a textual label, generally intended for error
        messages.
        :param input_data: The input data to parse.
        :return: Either the graph, if one could be determined from the
        input, or None if the input was empty.
        """
