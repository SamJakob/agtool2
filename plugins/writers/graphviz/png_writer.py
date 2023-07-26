import subprocess

from agtool.core import Controller
from agtool.error import AGPluginExternalError
from agtool.interfaces.writer import AGWriter
from agtool.struct.graph import Graph


class AGPNGWriter(AGWriter):
    """
    Writes an account graph to a PNG file.
    """

    @property
    def name(self) -> str:
        return "PNG Writer"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def author(self) -> str:
        return "SamJakob"

    @property
    def license(self) -> str:
        return "MIT"

    @property
    def default_file_extension(self) -> str:
        return "png"

    def __init__(self, controller: Controller):
        super().__init__(controller)

        self.controller = controller
        """
        The application controller. (Overridden to be the specific `Controller` implementation type as this
        plugin interacts with other plugins from the plugin registry.)
        """

    def write_graph(self, graph: Graph, destination_label: str) -> bytes:
        """
        Called to write a graph to a PNG file.
        This uses the GraphViz renderer (i.e., `AGGraphvizWriter`) to render the graph
        as a DOT file and then uses the GraphViz command-line tool to render the
        DOT file as a PNG file.

        :param graph: The graph to write.
        :param destination_label: The name of the output destination
        (e.g., a file name, or a URL). This is a textual label, generally
        intended for error messages.
        :return: The output data (as a string).
        """

        # Use the GraphViz renderer to render the graph as a DOT file.
        dot_renderer = self.controller.writer_for("dot")
        dot_data_str: str = dot_renderer.write_graph(graph,
                                                     destination_label=destination_label)

        dot_data: bytes = dot_data_str.encode("utf-8")

        # Use the GraphViz command-line tool to render the DOT file as a PNG file.
        try:
            self.controller.logger.info("Rendering DOT file as PNG file...")
            result = subprocess.run(['dot', '-Tpng'], capture_output=True, input=dot_data)

            if result.returncode != 0:
                if len(result.stderr) > 0:
                    self.controller.logger.error(result.stderr.decode("utf-8"))

                raise AGPluginExternalError(
                    plugin_id=self.id,
                    description=f"The GraphViz command-line tool exited with a non-zero exit code whilst "
                                f"rendering the output PNG file ({result.returncode}).",
                )

            self.controller.logger.success("Rendering completed successfully.")

            return result.stdout
        except FileNotFoundError:
            raise AGPluginExternalError(
                plugin_id=self.id,
                description="The GraphViz command-line tool was not found. Please install GraphViz and try again.",
            )
