import os.path
from typing import Optional

from agtool.core import Controller
from agtool.helpers.text import to_upper_camel_case
from agtool.interfaces.writer import AGWriter
from agtool.struct.graph import Graph


class AGGraphvizWriter(AGWriter):
    """
    Writes an account graph to a Graphviz DOT file.
    """

    @property
    def name(self) -> str:
        return "GraphViz Writer (dot)"

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
        return "dot"

    def __init__(self, controller: Controller):
        # Initialize the plugin.
        super().__init__(controller)

        # Locate any themes for this plugin.
        self.themes = self.load_all_extensions(subclass_of=AGGraphvizWriterTheme)

    def write_graph(self, graph: Graph, destination_label: str, options: Optional[dict[str, str]] = None) -> str:
        """
        Called to write a graph to a Graphviz DOT file.

        :param graph: The graph to write.
        :param destination_label: The name of the output destination
        (e.g., a file name, or a URL). This is a textual label, generally
        intended for error messages.
        :param options: An optional set of parameters to pass to the writer
        (e.g., for specifying theming options).
        :return: The output data (as a string).
        """

        self.controller.logger.info("Creating GraphViz DOT file for graph...")

        # Generate a graph name from the destination label.
        graph_name = to_upper_camel_case(
            # Get the root file name without the extension.
            os.path.basename(os.path.splitext(destination_label)[0])
        )

        # Compute the Graphviz attributes for rendering the graph.
        graph_attributes = AGGraphvizWriter._compute_graph_attributes()

        # Compute the DOT nodes and edges for the graph, based on those in the
        # agtool graph data structure.
        nodes = AGGraphvizWriter._compute_dot_nodes(graph)
        edges = AGGraphvizWriter._compute_dot_edges(graph)

        if not graph:
            self.controller.logger.warning("The graph is empty, so an empty DOT graph has been generated.")

        self.controller.logger.success("GraphViz DOT representation created successfully.")

        return f"""
// GraphViz .dot file generated by agtool {self.controller.version}
// on {self.controller.timestamp}.
        
digraph {graph_name} {{
    {graph_attributes.strip()}
    
    // -----------------------------------------------------------------------
    // Nodes
    // -----------------------------------------------------------------------

    // Declare the set of nodes in the graph with attributes.
    {nodes.strip()}

    // -----------------------------------------------------------------------
    // Edges
    // -----------------------------------------------------------------------

    // Specify the set of edges from the graph.
    {edges.strip()}
}}

""".lstrip()  # Leave a blank line at the end, but strip any leading whitespace.

    @staticmethod
    def _compute_graph_attributes() -> str:
        """
        Computes the Graphviz attributes for rendering an account graph as a string
        that can be inserted into a DOT file.

        :return: Graphviz attributes for rendering an account graph.
        """

        return '\n'.join([
            AGGraphvizWriter._dict_to_graphviz_attributes({
                # Render the graph dependencies from bottom to top.
                'rankdir': 'BT',
                # Use orthogonal splines (i.e., edges are drawn as a series of
                # axis-aligned segments - that is, parallel or perpendicular to
                # each other).
                'splines': 'ortho',
                # Use a minimum rank separation of 3/4 inches.
                # Formerly, 1.5in.
                'ranksep': '.75',
                # Use a minimum node separation of 1/2 inches.
                'nodesep': '.5',
                # Constrain the ordering of incoming edges to be left-to-right
                # in the order defined in the input file.
                'ordering': 'in',
                # Use the new ranking algorithm.
                'newrank': 'true',
                # Use the Prism algorithm to resolve edge overlaps.
                # 'prism1000' is the default number of attempts to mitigate
                # overlaps.
                'overlap': 'prism1000',
                # Use a scaling factor of -1.1 to increase the amount of space
                # between nodes.
                'overlap_scaling': '-1.1',
                # Use the circuit resistance model to resolve the distance
                # matrix for the graph.
                'model': 'circuit',
                'fontname': 'Times-Roman',
            }, statements=True)
        ])

    @staticmethod
    def _compute_dot_nodes(graph: Optional[Graph]) -> str:
        """
        Computes the DOT nodes for the given graph.

        :param graph: The graph to compute the DOT nodes for.
        :return: The DOT nodes for the given graph.
        """

        if not graph or not graph.has_vertices:
            return "    // (!) No nodes in graph."

        nodes = []

        for vertex_name, vertex in graph.vertices.items():
            attributes = AGGraphvizWriter._dict_to_graphviz_attributes({
                'shape': 'box',
            })

            nodes.append(f"    {vertex_name} [{attributes}];")

        return "\n".join(nodes)

    @staticmethod
    def _compute_dot_edges(graph: Optional[Graph]) -> str:
        """
        Computes the DOT edges for the given graph.

        :param graph: The graph to compute the DOT edges for.
        :return: The DOT edges for the given graph.
        """

        # If the graph is empty, we'll show that there are no nodes in the graph.
        # (and thus no edges).
        if not graph or not graph.has_vertices:
            return "    // (!) No nodes in graph (and thus no edges!)."

        # If the graph has no edges, but does have nodes, we'll show that there
        # are no edges in the graph.
        if not graph.has_edges:
            return "    // (!) No edges in graph."

        edges = []

        for sink_name, sink_edges in graph.mappings.items():
            for edge in sink_edges:
                edges.append(f"    {edge.dependency.name} -> {sink_name};")

        return "\n".join(edges)

    @staticmethod
    def _dict_to_graphviz_attributes(attributes: dict, statements: bool = False) -> str:
        """
        Converts a dictionary of attributes to a Graphviz attribute string.

        :param attributes: The attributes to convert.
        :param statements: Whether to use statements (i.e., semicolons) or not.
            Statements are used for the top-level attributes (e.g., for the graph as a whole),
            but not for attributes within the graph (e.g., for nodes).
        :return: The Graphviz attribute string.
        """
        join_char = "\n    " if statements else ", "

        output = []
        for key, value in attributes.items():
            # Add a comment with a link to the Graphviz documentation for the
            # attribute if we're generating statements (it would be a bit awkward
            # to have a comment in the middle of a list of attributes).
            comment = f" // https://graphviz.org/docs/attrs/{key}/" if statements else ""

            # Add the attribute to the output.
            output.append(f"{key}=\"{value}\"{';' if statements else ''}{comment}")

        return join_char.join(output)


class AGGraphvizWriterTheme:

    def __init__(self, plugin: AGGraphvizWriter):
        self.plugin = plugin
        """The `AGGraphvizWriter` plugin instance that this theme is for."""