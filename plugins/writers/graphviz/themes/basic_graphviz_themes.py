from typing import Optional, Final

from agtool.helpers.text import string_contains_any_of
from agtool.struct.graph import Graph
from agtool.struct.vertex import Vertex, VertexEdge
from plugins.writers.graphviz.graphviz_writer import AGGraphvizWriterTheme, AGGraphvizVertexStatistics, AGGraphvizWriter

BASIC_EDGE_COLOR_SCHEME: Final = [
    "black",
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

    def __init__(self, plugin: AGGraphvizWriter, graph: Graph):

        super().__init__(plugin, graph)

        self._counters = {
            'lone': {'normal': 0, 'recovery': 0},         # non-multi-factor (lone)
            'conjunction': {'normal': 0, 'recovery': 0}   # multi-factor
        }
        """Stores the unique counter for each edge type."""

        self._memoized_group_ids = {}
        """
        Memoizes the group IDs for each edge. This is used to ensure that
        groups have the same color for each edge.
        """

    def compute_node_attributes(self, vertex: Vertex, name: str) -> Optional[dict[str, str]]:
        """Color the nodes based on the CHI2022 paper."""
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
            case _:
                pass

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

        # If a color has not yet been assigned, we'll assign one.
        if 'color' not in attributes:
            if edge.unique_group_id in self._memoized_group_ids:
                attributes = attributes | {'color': self._memoized_group_ids[edge.unique_group_id]}
            else:
                # If the edge is a conjunction, we'll use the 'conjunction' counter.
                counter_type_a = 'conjunction' if edge.is_conjunction else 'lone'
                # If the edge is a recovery, we'll use the 'recovery' counter, otherwise
                # we'll use the 'normal' counter.
                counter_type_b = 'recovery' if edge.is_recovery else 'normal'

                # Load the counter for this edge type, and increment it (also mapping it into our range of colors).
                # We avoid the first color (black) as it is used for arrows that are not a part of a conjunction.
                # Then write the counter back to the dictionary (ready for next iteration).
                counter = (self._counters[counter_type_a][counter_type_b] % (len(BASIC_EDGE_COLOR_SCHEME) - 1)) + 1
                self._counters[counter_type_a][counter_type_b] = counter

                # Memoize the group ID.
                self._memoized_group_ids[edge.unique_group_id] = BASIC_EDGE_COLOR_SCHEME[counter]

                # Assign the color to the edge, and increment the counter.
                attributes = attributes | {'color': BASIC_EDGE_COLOR_SCHEME[counter]}

        return attributes
