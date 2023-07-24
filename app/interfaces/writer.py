from abc import abstractmethod
from typing import Union

from app.abstract import AbstractController
from app.interfaces.plugin import AGPlugin
from app.struct.graph import Graph


class AGWriter(AGPlugin):
    """
    Writes an account graph to some output destination.
    """

    @property
    @abstractmethod
    def default_file_extension(self) -> str:
        """The default file extension that this writer writes to."""

    def __init__(self, controller: AbstractController):
        super().__init__(controller)

    @abstractmethod
    def write_graph(self, graph: Graph, output_destination_name: str) -> Union[str, bytes]:
        """
        Called to write a graph to the format that this writer implements a
        writer for.

        :param graph: The graph to write.
        :param output_destination_name: The name of the output destination
        (e.g., a file name, or a URL). This is a textual label, generally
        intended for error messages.
        :return: The output data (either as a string, in the case of plain text
        formats, or as bytes, in the case of binary formats).
        """
