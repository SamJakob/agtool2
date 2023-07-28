"""
These are two legacy themes (with color variants) from the original agtool.
Specifically, the "simple" and "classic" themes. These themes are very simple
and only format edges based on whether they are grouped, and/or recovery edges.
Nodes are not colored at all.

These themes are superseded by the "basic" theme.

They do not seem to have been used much, even in the original agtool and had to be
patched in the original agtool to function properly. They are included here for
completeness and backwards compatibility, but you'll probably enjoy some of the newer
themes more!

One feature added here, is the ability to colorize the edges based on a globally
unique group ID. This color codes all conjunctions on the access method graph in
distinct colors - which identifies the total set of access methods a user has on their
graph. Or, perhaps more importantly, would highlight a lack of two-factor access
methods (if everything is colored uniquely, then there are no conjunctions).
"""

from typing import Optional, Final

from agtool.struct.vertex import Vertex, VertexEdge
from plugins.writers.graphviz.graphviz_writer import AGGraphvizWriterTheme, AGGraphvizVertexStatistics

# The legacy color scheme is a list of colors that are used to colorize the
# vertices in the graph. The colors are used in order, and then wrap around
# to the beginning of the list (with a warning).
LEGACY_EDGE_COLOR_SCHEME = [
    {"color": "black"},
    {"color": "blue"},
    {"color": "red"},
    {"color": "green"},
    {"color": "forestgreen"},
    {"color": "cyan"},
    {"color": "deeppink"},
    {"color": "yellow"},
    {"color": "darkorange"},
    {"color": "darksalmon"},
    {"color": "aquamarine"},
    {"color": "bisque"},
    {"color": "gold"},
    {"color": "darkslategrey"},
    {"color": "brown"},
    {"color": "turquoise"},
    {"color": "purple"},
    {"color": "grey"},
]

# The legacy color scheme is a list of colors that are used to colorize the
# vertices in the graph. The colors are used in order, and then wrap around
# to the beginning of the list (with a warning).
LEGACY_EDGE_GRAYSCALE_SCHEME: Final = [
    {"color": "black", "style": "solid"},
    {"color": "black", "style": "dashed"},
    {"color": "black", "style": "dotted"},
    {"color": "gray", "style": "solid"},
    {"color": "gray", "style": "dashed"},
    {"color": "gray", "style": "dotted"},
    {"color": "darkslategray", "style": "solid"},
    {"color": "darkslategray", "style": "dashed"},
    {"color": "darkslategray", "style": "dotted"},
    {"color": "black", "style": "solid", "arrowhead": "empty"},
    {"color": "black", "style": "dashed", "arrowhead": "empty"},
    {"color": "black", "style": "dotted", "arrowhead": "empty"},
    {"color": "gray", "style": "solid", "arrowhead": "empty"},
    {"color": "gray", "style": "dashed", "arrowhead": "empty"},
    {"color": "gray", "style": "dotted", "arrowhead": "empty"},
    {"color": "darkslategray", "style": "solid", "arrowhead": "empty"},
    {"color": "darkslategray", "style": "dashed", "arrowhead": "empty"},
    {"color": "darkslategray", "style": "dotted", "arrowhead": "empty"},
]


class AGGraphvizThemeSimple(AGGraphvizWriterTheme):
    """
    A simple theme that does not do any special formatting.
    Edges are colorized based on the target vertex.
    """

    scheme = LEGACY_EDGE_GRAYSCALE_SCHEME
    """The color scheme to use for coloring edges."""

    @classmethod
    def name(cls) -> str: return "simple"

    @classmethod
    def description(cls) -> str: return "Simple theme. " \
                                        "No special formatting. Edges are colored in grayscale."

    @classmethod
    def supported_features(cls) -> Optional[dict[str, set[str]]]:
        return {"grouping": {"default", "unique"}}

    def compute_node_attributes(self, vertex: Vertex, name: str, label: str) -> Optional[dict[str, str]]:
        if vertex.vertex_type == "pattern":
            return {"shape": "box3d", "fillcolor": "gray", "style": "filled"}

    def compute_edge_attributes(self,
                                from_node: Vertex,
                                from_node_statistics: AGGraphvizVertexStatistics,
                                edge: VertexEdge,
                                to_node: Vertex,
                                to_node_statistics: AGGraphvizVertexStatistics) -> Optional[dict[str, str]]:

        group_id = edge.unique_group_id if self.get_setting('grouping') == 'unique' else edge.group_id

        if int(group_id / len(self.scheme)) > 0:
            # TODO: should this raise an error instead?

            self.plugin.controller.logger.warning(f"There were more groups than colors in the color scheme. "
                                                  f"The color scheme has wrapped around. This may cause confusion.")

            # This message will repeat every time we call this function after we're out of colors.
            self.plugin.controller.logger.warning(f"Consider using a different theme, or increasing the number of "
                                                  f"colors in the color scheme. There are currently "
                                                  f"{len(self.scheme)} colors in the color scheme, but we needed "
                                                  f"{group_id + 1}.")

        return self.scheme[group_id % len(self.scheme)]


class AGGraphvizThemeClassic(AGGraphvizThemeSimple):
    """
    The classic agtool theme.

    Outputs edges where recovery methods are dashed and normal methods are solid.
    """

    scheme = LEGACY_EDGE_GRAYSCALE_SCHEME

    @classmethod
    def name(cls) -> str: return "classic"

    @classmethod
    def description(cls) -> str: return "The classic agtool theme. " \
                                        "Dashed edges are recovery methods. Edges are colored in grayscale."

    def compute_edge_attributes(self,
                                from_node: Vertex,
                                from_node_statistics: AGGraphvizVertexStatistics,
                                edge: VertexEdge,
                                to_node: Vertex,
                                to_node_statistics: AGGraphvizVertexStatistics) -> Optional[dict[str, str]]:
        # Inherit the edge attributes from the 'simple' theme (if there are any).
        attributes = super().compute_edge_attributes(from_node,
                                                     from_node_statistics,
                                                     edge,
                                                     to_node,
                                                     to_node_statistics) or {}

        # Additionally, if the edge is a recovery method, make it dashed.
        if edge.is_recovery:
            attributes = attributes | {'style': 'dashed'}

        return attributes


class AGGraphvizThemeSimpleColor(AGGraphvizThemeSimple):
    """
    See `AGGraphvizThemeSimple`.
    """

    scheme = LEGACY_EDGE_COLOR_SCHEME

    @classmethod
    def name(cls) -> str: return "simple-color"

    @classmethod
    def description(cls) -> str: return "Same as 'simple' but colorized."


class AGGraphvizThemeClassicColor(AGGraphvizThemeClassic):
    """
    See `AGGraphvizThemeClassic`.
    """

    scheme = LEGACY_EDGE_COLOR_SCHEME

    @classmethod
    def name(cls) -> str: return "classic-color"

    @classmethod
    def description(cls) -> str: return "Same as 'classic' but colorized."
