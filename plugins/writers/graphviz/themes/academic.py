from typing import Optional

from agtool.helpers.text import string_contains_any_of
from agtool.struct.vertex import Vertex
from plugins.writers.graphviz.themes.basic import AGGraphvizThemeMinimal


class AGGraphvizThemeCHI(AGGraphvizThemeMinimal):
    """
    An alias for the 'minimal' theme.

    This is left here for posterity, and to allow for future modifications to the
    theme for CHI without modifying the underlying 'minimal' theme.
    """

    @classmethod
    def name(cls):
        return "chi"

    @classmethod
    def description(cls):
        return "The theme used in the CHI2022 paper. (Alias for 'minimal')."


class AGGraphvizThemeSwiss(AGGraphvizThemeMinimal):
    """
    The theme used in the Swiss paper.

    The same edge coloring as the 'minimal' theme is used, but nodes are colored
    by types specific to the theme.
    """

    @classmethod
    def name(cls):
        return "swiss"

    @classmethod
    def description(cls):
        return "The theme used in the Swiss paper. Colors vertices by its own types."

    def compute_node_attributes(self, vertex: Vertex, name: str, label: str) -> Optional[dict[str, str]]:
        """Colors nodes based on the coloring used in the Swiss paper."""

        attributes = {
            'colorscheme': 'pastel19',
            'style': 'filled',
            'penwidth': '0',
            'fillcolor': '9'
        }

        vertex_type = vertex.vertex_type.lower()
        """Retrieve the normalized vertex type name."""

        match vertex_type:
            case _ if string_contains_any_of(vertex_type, 'secretKey'):
                attributes = attributes | {'fillcolor': '1'}
            case _ if string_contains_any_of(vertex_type, 'public'):
                attributes = attributes | {'fillcolor': '2'}
            case _ if string_contains_any_of(vertex_type, 'publicKey'):
                attributes = attributes | {'fillcolor': '3'}
            case _ if string_contains_any_of(vertex_type, 'privateKey'):
                attributes = attributes | {'fillcolor': '4'}
            case _ if string_contains_any_of(vertex_type, 'algorithm'):
                attributes = attributes | {'fillcolor': '5'}
            case _ if string_contains_any_of(vertex_type, 'comms'):
                attributes = attributes | {'fillcolor': '6'}
            case _ if string_contains_any_of(vertex_type, 'entity'):
                attributes = attributes | {'fillcolor': '7'}
            case _ if string_contains_any_of(vertex_type, 'secret', 'secretVec'):
                attributes = attributes | {'fillcolor': '8'}

        if string_contains_any_of(vertex_type, 'vec'):
            attributes = attributes | {'shape': 'box', 'penwidth': '1', 'style': 'filled, diagonals'}

        return attributes
