import re
from typing import Optional

from agtool.helpers.text import string_contains_any_of
from agtool.struct.vertex import Vertex, VertexEdge
from plugins.writers.graphviz.graphviz_writer import AGGraphvizVertexStatistics
from plugins.writers.graphviz.themes.basic import AGGraphvizThemeMinimal


class AGGraphvizThemeMetis(AGGraphvizThemeMinimal):
    # Use spectral11 color scheme, but remove a few colors that are too similar
    # to others (or which are ugly or too unreadable).
    # Also, we'll shuffle the colors around a bit to make the graph look more
    # interesting.
    scheme = ['2', '10', '3', '11', '4', '9', '5', '8', '7']

    @classmethod
    def name(cls):
        return "metis"

    @classmethod
    def description(cls):
        return "A clean and modern theme."

    def compute_node_attributes(self, vertex: Vertex, name: str, label: str) -> Optional[dict[str, str]]:

        # Set the base attributes for nodes.
        attributes = {
            'style': 'filled',
            'penwidth': '0',
            'fillcolor': 'black',
            'fontcolor': 'white',
            'fontsize': '12',

            # This font requires that "Source Sans 3" (specifically, the "Bold"
            # variant) be installed on the system.
            'fontname': 'Source Sans 3 SemiBold',
        }

        vertex_type = vertex.vertex_type.lower()
        """Retrieve the normalized vertex type name."""

        vertex_name = vertex.name.lower()

        match vertex_type:
            # Password type.
            case _ if string_contains_any_of(vertex_type, 'pw', 'pwd', 'password') \
                      or string_contains_any_of(vertex_name, 'pw', 'pwd', 'password'):
                attributes = attributes | {
                    'fillcolor': '#475569',
                    'shape': 'note'
                }

            # Account type.
            case _ if string_contains_any_of(vertex_type, 'account', 'mail'):
                attributes = attributes | {
                    'fillcolor': '#818cf8',
                    'shape': 'box',
                    'style': 'filled,rounded',
                    'margin': '0.4,0'
                }

                if string_contains_any_of(vertex_name, 'data'):
                    if self.get_setting("labels", global_setting=True) == 'human':
                        # If labels is set to "human" mode, and there exists a node
                        # with the same name but without the "data" prefix/suffix, we can
                        # rewrite the name to "<name> (locked)".
                        stripped_vertex_name = re.sub(r'_?[Dd]ata_?', '', vertex.name)

                        # Check if this node has an incoming node with the stripped name.
                        # (i.e., check if the stripped vertex name relates to a vertex that provides
                        # access to this one).
                        if vertex.is_incoming_name(stripped_vertex_name):
                            # If so, we can rewrite the name.
                            attributes = attributes | {'label': f"{stripped_vertex_name} (data)"}

            # Biometric type.
            case _ if string_contains_any_of(vertex_type, 'finger', 'biometric'):
                attributes = attributes | {
                    'fillcolor': '#34d399',
                    'shape': 'note'
                }

            # Device type.
            case _ if string_contains_any_of(vertex_type, 'device'):
                attributes = attributes | {
                    'shape': 'box',
                    'fontname': 'Source Sans 3 Bold',
                    'fillcolor': '#000000',
                    'fontcolor': '#ffffff',
                }

                # If the device is a "locked" variant, stylize it as such.
                if string_contains_any_of(vertex_name, 'locked'):
                    attributes = attributes | {
                        'style': 'filled',
                        'peripheries': '2',
                        'penwidth': '1',
                    }

                    if self.get_setting("labels", global_setting=True) == 'human':
                        # If labels is set to "human" mode, and there exists a node
                        # with the same name but without the "locked" prefix/suffix, we can
                        # rewrite the name to "<name> (locked)".
                        stripped_vertex_name = re.sub(r'_?[Ll]ocked_?', '', vertex.name)

                        # Check if the graph has a hypothetical vertex without the
                        # "locked" prefix/suffix.
                        if self.graph.has_vertex_with_name(stripped_vertex_name):
                            # If so, check that _that_ vertex has an edge to the
                            # current vertex.
                            for edge in self.graph.vertices[stripped_vertex_name].edges:
                                if edge.dependency.name == vertex.name:
                                    # If it does, rename the label to include the
                                    # "(locked)" suffix.
                                    attributes = attributes | {
                                        'label': f'{stripped_vertex_name} (locked)',
                                    }

        # Get the most up-to-date label.
        # (Either the one directly assigned to the vertex, or the one we just
        # generated).
        label = attributes['label'] if 'label' in attributes else label
        if self.get_setting('labels', global_setting=True) == 'human':
            # Make a human-readable version of the vertex type.
            human_vertex_type = vertex_type.upper().replace('_', ' ')

            # If labels is set to "human" mode, we can add in the vertex type
            # to the label.
            attributes = attributes | {'label': f'<'
                                                f'<TABLE BORDER="0" '
                                                f'  CELLBORDER="0" CELLPADDING="0" CELLSPACING="3">'
                                                f'<TR><TD>'
                                                f'<FONT POINT-SIZE="7"><B>{human_vertex_type}</B></FONT>'
                                                f'</TD></TR>'
                                                f'<TR><TD>{label}</TD></TR>'
                                                f'</TABLE>'
                                                f'>'}

        return attributes

    def compute_edge_attributes(self,
                                from_node: Vertex,
                                from_node_statistics: AGGraphvizVertexStatistics,
                                edge: VertexEdge,
                                to_node: Vertex,
                                to_node_statistics: AGGraphvizVertexStatistics) -> Optional[dict[str, str]]:
        return super().compute_edge_attributes(from_node,
                                               from_node_statistics,
                                               edge,
                                               to_node,
                                               to_node_statistics) | {
            'colorscheme': 'spectral11',
        }
