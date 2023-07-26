import os.path
from abc import abstractmethod, ABC
from collections import deque
from typing import Optional, Type, TypeVar, Final

from agtool.core import Controller
from agtool.error import AGPluginExternalError
from agtool.helpers.text import to_upper_camel_case
from agtool.interfaces.writer import AGWriter
from agtool.struct.graph import Graph
from agtool.struct.vertex import Vertex, VertexEdge

_ThemeType = TypeVar('_ThemeType', bound='AGGraphvizWriterTheme')


class AGGraphvizVertexStatistics:
    """
    Stores statistics generated dynamically about vertices which can be used for styling.
    Each vertex, at render time, is given a statistics object which can be used to
    keep track of the next edges to be processed.

    This is useful for styling edges based on their position in the graph (e.g., to style the
    first edge differently to the second edge).

    The statistics can then be retained at the end of a graph rendering pass for calculations.
    """

    @property
    def incoming_edge_index(self) -> int:
        """
        The index of the next in-edge to this vertex to be processed.
        This is with respect to edges that point into the current vertex from
        a dependency.

        The first in-edge pointing into the current vertex will have index 0,
        the next index 1, and so on.
        """
        return self._incoming_edge_index

    @property
    def outgoing_edge_index(self) -> int:
        """
        The index of the next out-edge from this vertex to be processed.
        This is with respect to edges that point out of the current vertex to
        a dependent.

        The first out-edge pointing out of the current vertex will have index 0,
        the next index 1, and so on.
        """
        return self._outgoing_edge_index

    def __init__(self, vertex: Vertex):
        self.vertex = vertex
        """The vertex that these statistics are for."""

        self._incoming_edge_index = 0
        self._outgoing_edge_index = 0


class AGGraphvizWriter(AGWriter):
    """
    Writes an account graph to a Graphviz DOT file.
    """

    DEFAULT_GRAPH_ATTRIBUTES: Final = {
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
    }

    DEFAULT_NODE_ATTRIBUTES: Final = {
        'shape': 'box'
    }

    DEFAULT_EDGE_ATTRIBUTES: Final = {}

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
        self.themes: list[Type[_ThemeType]] = self.load_all_extensions(subclass_of=AGGraphvizWriterTheme)
        """The theme classes for GraphViz writers."""

    def write_graph(self, graph: Graph, destination_label: str) -> str:
        """
        Called to write a graph to a Graphviz DOT file.

        :param graph: The graph to write.
        :param destination_label: The name of the output destination
        (e.g., a file name, or a URL). This is a textual label, generally
        intended for error messages.
        :return: The output data (as a string).
        """

        # Check if the user wants to list the available themes.
        should_list_themes = (self.controller.settings['theme'].strip().lower() in ['-l', '--list', '?', '--help']) \
            if 'theme' in self.controller.settings else False

        requested_theme_name: str = self.controller.settings['theme'].lower().strip() \
            if 'theme' in self.controller.settings else None
        """The normalized name of the theme that the user has requested."""

        # The theme to use for the graph.
        theme: Optional[_ThemeType] = None

        # If at theme has been specified (and is not equal to "false" or "none") and themes should not be listed,
        # locate the theme so it can be applied.
        if 'theme' in self.controller.settings \
                and requested_theme_name \
                and not should_list_themes \
                and requested_theme_name not in ["false", "none"]:
            self.controller.logger.info(f"Searching for theme \"{requested_theme_name}\"...")

            # Search through all the identified theme classes for one with a name that matches the theme specified
            # by the user.
            for theme_class in self.themes:
                if theme_class.name().lower() == requested_theme_name:
                    theme = theme_class(self, graph)
                    self.controller.logger.success(f"Located theme \"{theme_class.name()}\" successfully.")
                    break

            # If we couldn't find a theme, raise an error.
            if not theme:
                raise AGPluginExternalError(
                    plugin_id=self.id,
                    description=f"Could not locate theme \"{requested_theme_name}\"."
                )

        # Otherwise, if a theme has been specified, but it is empty, or equal to "false" or "none", we'll just use the
        # default theme.
        elif not should_list_themes or not requested_theme_name:
            self.controller.logger.warning("No theme specified for graph. "
                                           "No styling (semantic or aesthetic) will be applied.")

        # Finally, if the user wants to list the available themes, we'll do that.
        else:
            self.controller.logger.info("")
            self.controller.logger.info("Listing available themes...")

            if not self.themes:
                self.controller.logger.info("    No themes are available.")
            else:
                longest_theme_name = max([len(theme_class.name()) for theme_class in self.themes])

                self.controller.logger.info("")
                for theme_class in self.themes:
                    theme_entry = f"    {theme_class.name().ljust(longest_theme_name + 4, ' ')}"
                    theme_blank = " " * len(theme_entry)
                    theme_features_dict = theme_class.supported_features() or {}

                    theme_features = ", ".join([
                        f"theme.{feature_name}={{{','.join(feature_values)}}}"
                        for feature_name, feature_values in theme_features_dict.items()
                    ]) if theme_features_dict else "None"

                    theme_description_lines = deque(theme_class.description().split('\n'))
                    self.controller.logger.info(f"{theme_entry} - {theme_description_lines.popleft()}")

                    for line in theme_description_lines:
                        self.controller.logger.info(f"{theme_blank} - {line}")

                    self.controller.logger.info(f"{' ' * len(theme_entry)}   Supported settings: {theme_features}")
                    self.controller.logger.info("")

            # We don't need to do anything else.
            self.controller.shutdown()

        self.controller.logger.debug("Parsing theme settings...")

        # Validate any specified theme settings.
        if theme:
            theme_features_dict = theme.supported_features() or {}
            for feature, value in theme_features_dict.items():
                if f"theme.{feature}" in self.controller.settings:
                    if self.controller.settings[f"theme.{feature}"] not in value:
                        raise AGPluginExternalError(
                            plugin_id=self.id,
                            description=f"Invalid value for theme feature \"{feature}\". "
                                        f"Valid values are: {', '.join(value)}. Value specified: "
                                        f"\"{self.controller.settings[f'theme.{feature}']}\"."
                        )

        self.controller.logger.info("Creating GraphViz DOT file for graph...")

        # Initialize the statistics for each vertex.
        statistics = {
            vertex_name: AGGraphvizVertexStatistics(vertex) for vertex_name, vertex in graph.vertices.items()
        }

        # Generate a graph name from the destination label.
        graph_name = to_upper_camel_case(
            # Get the root file name without the extension.
            os.path.basename(os.path.splitext(destination_label)[0])
        )

        # Compute the Graphviz attributes for rendering the graph.
        graph_attributes = AGGraphvizWriter._compute_graph_attributes(theme)

        # Compute the DOT nodes and edges for the graph, based on those in the
        # agtool graph data structure.
        nodes = AGGraphvizWriter._compute_dot_nodes(graph, theme)
        edges = AGGraphvizWriter._compute_dot_edges(graph,
                                                    statistics=statistics,
                                                    theme=theme)

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
    def _compute_graph_attributes(theme: Optional[_ThemeType] = None) -> str:
        """
        Computes the Graphviz attributes for rendering an account graph as a string
        that can be inserted into a DOT file.

        :return: Graphviz attributes for rendering an account graph.
        """

        graph_attributes = AGGraphvizWriter.DEFAULT_GRAPH_ATTRIBUTES if not theme or theme.retain_defaults else {}
        graph_attributes = graph_attributes | ({} if not theme else (theme.compute_graph_attributes() or {}))

        # Serialize the attributes to a string.
        return AGGraphvizWriter._dict_to_graphviz_attributes(graph_attributes, statements=True)

    @staticmethod
    def _compute_dot_nodes(graph: Optional[Graph], theme: Optional[_ThemeType] = None) -> str:
        """
        Computes the DOT nodes for the given graph.

        :param graph: The graph to compute the DOT nodes for.
        :return: The DOT nodes for the given graph.
        """

        if not graph or not graph.has_vertices:
            return "    // (!) No nodes in graph."

        nodes = []

        for vertex_name, vertex in graph.vertices.items():
            # Compute the node attributes.
            node_attributes = AGGraphvizWriter.DEFAULT_NODE_ATTRIBUTES if not theme or theme.retain_defaults else {}
            node_attributes = node_attributes | (
                {} if not theme else (theme.compute_node_attributes(vertex, vertex_name) or {})
            )

            # Serialize the attributes to a string.
            attributes = AGGraphvizWriter._dict_to_graphviz_attributes(node_attributes)

            nodes.append(f"    {vertex_name} [{attributes}];")

        return "\n".join(nodes)

    @staticmethod
    def _compute_dot_edges(graph: Optional[Graph],
                           statistics: dict[str, AGGraphvizVertexStatistics],
                           theme: Optional[_ThemeType] = None) -> str:
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
                # Compute the edge attributes.
                edge_attributes = AGGraphvizWriter.DEFAULT_EDGE_ATTRIBUTES if not theme or theme.retain_defaults else {}
                edge_attributes = edge_attributes | ({} if not theme else (theme.compute_edge_attributes(
                    from_node=edge.dependency,
                    from_node_statistics=statistics[edge.dependency.name],
                    edge=edge,
                    to_node=graph.vertices[sink_name],
                    to_node_statistics=statistics[sink_name]
                ) or {}))

                # Serialize the attributes to a string.
                attributes = AGGraphvizWriter._dict_to_graphviz_attributes(edge_attributes)

                edges.append(f"    {edge.dependency.name} -> {sink_name} [{attributes}];")

                # Increment the outgoing edge index for the source vertex.
                # noinspection PyProtectedMember
                statistics[edge.dependency.name]._outgoing_edge_index += 1

                # Increment the incoming edge index for the sink vertex.
                # noinspection PyProtectedMember
                statistics[sink_name]._incoming_edge_index += 1

        return "\n".join(edges)

    @staticmethod
    def _dict_to_graphviz_attributes(attributes: dict[str, str], statements: bool = False) -> str:
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

            # Escape any double quotes in the value.
            if '"' in value:
                value = value.replace('"', '\\"')

            # Add the attribute to the output.
            output.append(f"{key}=\"{value}\"{';' if statements else ''}{comment}")

        return join_char.join(output)


class AGGraphvizWriterTheme(ABC):
    """
    Used to theme the output of a GraphViz writer.
    Without a theme, the output is just rendered as a plain graph (i.e., with no
    coloring or other styling, semantic or otherwise).

    To create a theme, create a subclass of this class and override the relevant
    methods. If you place the theme anywhere within the plugins directory, it will
    be automatically loaded by `AGGraphvizWriter`.

    Themes are extensions. Unlike plugins they are instantiated for each graph
    that is written, so they can store state for the graph that they are styling.
    This means `name` must be implemented as a class method, not a property.
    """

    @classmethod
    @abstractmethod
    def name(cls) -> str:
        """
        The name of the theme.
        This should be unique to the theme. It is used to identify the theme
        when specifying it as an option.

        **You must override this property.**

        If you're not sure what to use, feel free to use reverse domain notation
        (e.g., `com.example.my_theme`) or just `your_name.your_theme_name` to
        avoid conflicts with other themes.

        Ideally, single words should be reserved for first-party themes.

        :return: The name of the theme.
        """

    @classmethod
    @abstractmethod
    def description(cls) -> str:
        """
        A description of the theme.
        This is used to describe the theme when listing available themes.

        **You should override this property and provide a meaningful description.**

        :return: A description of the theme.
        """
        return "No description provided."

    @classmethod
    def supported_features(cls) -> Optional[dict[str, set[str]]]:
        """
        An optional set of feature flags that this theme supports.
        These will be shown automatically in the help text for the theme.

        Additionally, if a feature flag is selected and its value is not set to
        one of the items in the set for that flag, an error will be raised.

        The feature flags are specified as a dictionary, where the key is the
        name of the feature flag, and the value is a set of valid values for
        that feature flag.

        **Note**: do not put `theme.` as a prefix on the feature flag names.
        This will be added automatically. So if you want to specify a feature
        flag called `my_feature`, you should specify it as `my_feature` in this
        dictionary, and it will be specified as `theme.my_feature` on the
        command line.
        """
        return None

    @property
    def retain_defaults(self) -> bool:
        """
        Whether to retain the default attributes for the graph and nodes.
        If this is set to `True` (which it is by default), then the default attributes
        will be merged with the attributes returned by the theme (where the theme's
        attributes take precedence).

        If this is set to `False`, then the default attributes will not be set, and only
        the attributes returned by the theme will be used. (That is, you can override
        this and return `False` if you want to completely customize the attributes
        for the graph and nodes).

        :return: Whether to retain the default attributes for the graph and nodes.
        """
        return True

    def get_setting(self, name: str) -> Optional[str]:
        """Fetches the requested setting from the controller. Returns none if the setting is not set."""

        if f'theme.{name}' in self.plugin.controller.settings:
            return self.plugin.controller.settings[f'theme.{name}']

        return None

    def __init__(self, plugin: AGGraphvizWriter, graph: Graph):
        self.plugin = plugin
        """The `AGGraphvizWriter` plugin instance that this theme is for."""

        self.graph = graph
        """The graph that this theme is for."""

    def compute_graph_attributes(self) -> Optional[dict[str, str]]:
        """
        Returns a dictionary of Graphviz attributes for the graph as a whole.

        :return: A dictionary of Graphviz attributes for the graph as a whole.
        Or `None` to not change the attributes.
        """

    def compute_node_attributes(self, vertex: Vertex, name: str) -> Optional[dict[str, str]]:
        """
        Returns a dictionary of Graphviz attributes for the given vertex.

        :param vertex: The vertex to compute the attributes for.
        :param name: The name of the vertex.

        :return: A dictionary of Graphviz attributes for the given vertex.
        Or `None` to not change the attributes.
        """

    def compute_edge_attributes(self,
                                from_node: Vertex,
                                from_node_statistics: AGGraphvizVertexStatistics,
                                edge: VertexEdge,
                                to_node: Vertex,
                                to_node_statistics: AGGraphvizVertexStatistics,
                                ) -> Optional[dict[str, str]]:
        """
        Returns a dictionary of Graphviz attributes for the given edge.
        The edge points from 'source' to 'sink' (i.e., from the dependency to the
        dependent such that the arrow is pointing from the dependency to the
        dependent). (They are named `source` and `sink` because the nodes were
        considered in isolation at the time of naming, they might not be true
        sources and sinks in graph theory terms).

        :param from_node: The vertex that the edge points from. (The same as `edge.dependency`).
        :param edge: The edge to compute the attributes for.
        :param to_node: The vertex that the edge points to. (The same as `graph.vertices[sink_name]`).
        :param from_node_statistics: The statistics for the vertex that the edge points from.
        See `AGGraphvizVertexStatistics` for more information.
        :param to_node_statistics: The statistics for the vertex that the edge points to.
        See `AGGraphvizVertexStatistics` for more information.

        :return: A dictionary of Graphviz attributes for the given edge.
        Or `None` to not change the attributes.
        """
