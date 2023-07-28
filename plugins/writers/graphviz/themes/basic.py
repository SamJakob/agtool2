"""
These are basic, modern, themes for the graphviz writer.
The 'basic' theme supersedes the 'global' theme in the old agtool, and the 'minimal' theme supersedes
the former 'minimal' theme.

`AGGraphvizThemeBasic` colors the edges and vertices by type. Vertex types are as specified in the input.
Edges are colored uniquely within each type out of the following matrix:

|                            | Lone (Single method permits access) | Conjunction (multi-factor access)    |
|----------------------------|-------------------------------------|--------------------------------------|
| **Normal Access Method**   | Lone (not multi-factor), Normal     | Conjunction (multi-factor), Normal   |
| **Recovery Access Method** | Lone (not multi-factor), Recovery   | Conjunction (multi-factor), Recovery |

See the documentation on `AGGraphvizThemeBasic.compute_edge_attributes` for further details.

"""

from typing import Optional, Final

from agtool.helpers.text import string_contains_any_of
from agtool.struct.graph import Graph
from agtool.struct.vertex import Vertex, VertexEdge
from plugins.writers.graphviz.graphviz_writer import AGGraphvizWriterTheme, AGGraphvizVertexStatistics, AGGraphvizWriter

BASIC_EDGE_COLOR_SCHEME: Final = [
    "blue",
    "red",
    "green",
    "forestgreen",
    "deeppink",
    "gold",
    "brown",
    "purple",
    "cyan2",
    "yellow",
    "darkorange",
    "aquamarine",
    "bisque",
    "darkolivegreen2",
    "turquoise",
    "cornflowerblue",
    "cadetblue",
    "grey",
]


class AGGraphvizThemeBasic(AGGraphvizWriterTheme):

    scheme = BASIC_EDGE_COLOR_SCHEME
    """The color scheme to use for coloring edges."""

    @classmethod
    def name(cls) -> str:
        return "basic"

    @classmethod
    def description(cls) -> str:
        return "A theme that colors edges and vertices by type. " \
               "Vertex types are as specified in the input.\n" \
               "Edges are colored uniquely within each type.\n" \
               "Edge types are: " \
               "'normal', 'recovery', 'multi-factor', 'multi-factor recovery'.\n" \
               "See the manual for more information on edge types."

    def __init__(self, plugin: AGGraphvizWriter, graph: Graph, skip_color_computation: bool = False):

        super().__init__(plugin, graph)

        self._counters = {
            'lone': {'normal': 0, 'recovery': 0},  # non-multi-factor (lone)
            'conjunction': {'normal': 0, 'recovery': 0}  # multi-factor
        }
        """Stores the unique counter for each edge type."""

        self._memoized_group_ids = {}
        """
        Memoizes the group IDs for each edge. This is used to ensure that
        groups have the same color for each edge.
        """

        self._skip_color_computation = skip_color_computation
        """
        Whether to skip memoization of edge colors. This is useful for themes
        that want to use a different identifier for memoization (e.g., the edge
        label, or the per-vertex group ID instead of the unique group ID).
        
        See `compute_edge_attributes` for more information.
        """

    def compute_node_attributes(self, vertex: Vertex, name: str, label: str) -> Optional[dict[str, str]]:
        """Colors nodes based on the coloring used in the CHI2022 paper."""

        attributes = {
            'colorscheme': 'pastel19',
            'style': 'filled',
            'penwidth': '0',
            'fillcolor': '9'
        }

        vertex_type = vertex.vertex_type.lower()
        """Retrieve the normalized vertex type name."""

        vertex_name = vertex.name.lower()

        match vertex_type:
            # Password type.
            case _ if string_contains_any_of(vertex_type, 'pw', 'pwd', 'password') \
                      or string_contains_any_of(vertex_name, 'pw', 'pwd', 'password'):
                attributes = attributes | {'fillcolor': '1'}
            # Account type.
            case _ if string_contains_any_of(vertex_type, 'account', 'mail'):
                attributes = attributes | {'fillcolor': '2'}
            # Biometric type.
            case _ if string_contains_any_of(vertex_type, 'finger', 'biometric'):
                attributes = attributes | {'fillcolor': '3'}
            # Password Manager.
            case _ if string_contains_any_of(vertex_type, 'password manager'):
                attributes = attributes | {'fillcolor': '4'}
            # Device type.
            case _ if string_contains_any_of(vertex_type, 'device'):
                attributes = attributes | {'fillcolor': '5'}

                # If the device is locked, render diagonals.
                if string_contains_any_of(vertex_name, 'locked'):
                    attributes = attributes | {'penwidth': '1', 'style': 'filled, diagonals'}

            # Account Manager type. (CyberGuard)
            case _ if string_contains_any_of(vertex_type, 'account manager', 'cyberguard') \
                      or string_contains_any_of(vertex_name, 'cyberguard'):
                attributes = attributes | {
                    'fillcolor': '#8E61F0',
                    'fontcolor': 'white',
                    'fontname': 'Source Sans 3 SemiBold',
                    'fontsize': '10',
                }

        # In addition to the above, if the vertex type includes pattern,
        # render it as a 3D box.
        if string_contains_any_of(vertex_type, 'pattern'):
            attributes = attributes | {'shape': 'box3d', 'penwidth': '0.8'}

        return attributes

    def compute_edge_attributes(self,
                                from_node: Vertex,
                                from_node_statistics: AGGraphvizVertexStatistics,
                                edge: VertexEdge,
                                to_node: Vertex,
                                to_node_statistics: AGGraphvizVertexStatistics,
                                ) -> Optional[dict[str, str]]:
        """
        Colors edges based on access method type (see documentation for
        `plugins.writers.graphviz.themes.basic`).

        - Recovery methods are dashed.
        - Conjunctions are colored uniquely to indicate when multiple access methods (factors) are required to access a
          resource and have a filled arrowhead.
        - Single-access (lone) edges are colored black with an empty arrowhead.
        - Edges may also be 'hidden' (i.e., not rendered). This is done by ensuring the label contains `"invis"`.

        Edge colors are memoized based on their unique group ID. This ensures that each conjunction of access methods
        have edges colored the same (unless `skip_color_computation` is set to `True` on the constructor).

        This is to allow themes to memoize colors based on a different identifier (e.g., the edge label, or the
        per-vertex group ID instead of the unique group ID) but to re-use all of the other node/edge attributes
        computed by this theme.
        """

        attributes = {'arrowhead': 'normal'}

        if edge.is_recovery:
            attributes = attributes | {'style': 'dashed'}

        # If the edge is a 'lone' edge (i.e., not part of a conjunction),
        # then we want to make the arrowhead empty. We'll also set the
        # color to black.
        if not edge.is_conjunction:
            attributes = attributes | {'arrowhead': 'empty', 'color': 'black'}

        if edge.is_hidden:
            attributes = attributes | {'color': 'white'}

        # Finally, augment the attributes with the edge color, provided we're not skipping color computation.
        if not self._skip_color_computation:
            attributes = self.compute_edge_color_by_id(attributes, edge, edge.unique_group_id)

        return attributes

    def compute_edge_color_by_id(self,
                                 attributes: Optional[dict[str, str]],
                                 edge: VertexEdge,
                                 edge_id: int,
                                 with_memoization: bool = True):
        """Colors an edge by its unique ID. This is used to colorize conjunctions."""
        if attributes is None:
            attributes = {}

        # If a color has not yet been assigned, we'll assign one.
        if 'color' not in attributes:
            if edge_id in self._memoized_group_ids and with_memoization:
                attributes = attributes | {'color': self._memoized_group_ids[edge_id]}
            else:
                # If the edge is a conjunction, we'll use the 'conjunction' counter.
                counter_type_a = 'conjunction' if edge.is_conjunction else 'lone'
                # If the edge is a recovery, we'll use the 'recovery' counter, otherwise
                # we'll use the 'normal' counter.
                counter_type_b = 'recovery' if edge.is_recovery else 'normal'

                # Load the counter for this edge type, and increment it (also mapping it into our range of colors).
                # We avoid the first color (black) as it is used for arrows that are not a part of a conjunction.
                # Then write the counter back to the dictionary (ready for next iteration).
                counter = (self._counters[counter_type_a][counter_type_b] % len(self.scheme))
                self._counters[counter_type_a][counter_type_b] = counter + 1

                if with_memoization:
                    # Memoize the group ID.
                    self._memoized_group_ids[edge_id] = self.scheme[counter]

                # Assign the color to the edge, and increment the counter.
                attributes = attributes | {'color': self.scheme[counter]}

        return attributes


class AGGraphvizThemeMinimal(AGGraphvizThemeBasic):

    @classmethod
    def name(cls):
        return "minimal"

    @classmethod
    def description(cls):
        return "Similar to the 'basic' theme but uses a minimal set of colors for edges."

    def __init__(self, plugin: AGGraphvizWriter, graph: Graph):
        # Disable the color computation on the superclass, to allow for a
        # custom scheme.
        super().__init__(plugin, graph, skip_color_computation=True)

    def compute_edge_attributes(self,
                                from_node: Vertex,
                                from_node_statistics: AGGraphvizVertexStatistics,
                                edge: VertexEdge,
                                to_node: Vertex,
                                to_node_statistics: AGGraphvizVertexStatistics,
                                ) -> Optional[dict[str, str]]:

        # Compute the attributes as normal.
        attributes = super().compute_edge_attributes(from_node,
                                                     from_node_statistics,
                                                     edge,
                                                     to_node,
                                                     to_node_statistics)

        # Additionally, check for 'comp' and 'gen' in the edge label (if there is one).
        # comp => dashed line, gen => dotted line.
        #
        # It appears that these were only used by the 'swiss' style, but as it was possible
        # for these to be used in other styles, we'll support them here.
        if edge.label:
            if 'comp' in edge.label:
                attributes = attributes | {'style': 'dashed'}
            elif 'gen' in edge.label:
                attributes = attributes | {'style': 'dotted'}

        # Then, augment the attributes with the alternative edge colors.
        return self.compute_edge_color_by_id(attributes, edge, edge.group_id)
