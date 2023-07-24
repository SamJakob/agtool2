from typing import Final, Optional, TypeVar

_VertexType = TypeVar('_VertexType', bound='Vertex')
"""Workaround for typing.Self on a Vertex in Python < 3.11. Do not use outside of vertex.py"""

_VertexEdgeType = TypeVar('_VertexEdgeType', bound='VertexEdge')
"""Workaround for ordered bindings on constructor parameters. Do not use outside of vertex.py"""


class Vertex:
    """
    A vertex belonging to a graph. This contains metadata about how that vertex
    should be rendered, such as name and color - as well as storing incident
    edges for that vertex.
    """

    @property
    def has_dependencies(self) -> bool:
        """
        Returns true if the vertex depends on other vertices/edges or false if
        it is an orphan (or a source).
        """
        return len(self.edges) > 0

    def __init__(self,
                 name: str,
                 vertex_type: str,
                 edges: Optional[list[_VertexEdgeType]] = None,
                 attributes: Optional[dict[str, any]] = None):
        """
        Initializes a vertex.
        :param name: The (unique) name of the vertex. Vertex names must be
        unique as vertices are considered equal if their names match.
        """
        self.name: Final[str] = name
        """The (unique) name of the vertex."""

        self.vertex_type: Final[str] = vertex_type
        """The type of the vertex."""

        self.edges: list[VertexEdge] = edges if edges is not None else []
        """The incident edges (directed inward) to the vertex."""

        self.attributes: dict[str, any] = attributes if attributes is not None else {}

    def get_incoming(self) -> dict[str, _VertexType]:
        """
        Maps edges to a dictionary of adjacent vertices, keyed by the name of
        each adjacent vertex. This therefore shows all the incident edges
        (directed into) the current one. (The vertices that the current vertex
        is dependent on).
        """
        return {edge.dependency.name: edge.dependency for edge in self.edges}

    def __str__(self, with_edges=False):
        edges_str = ''

        # If we want edges included in the output string, we can compute the
        # string for each edge and precede it with a newline if there are any
        # edges.
        if with_edges and len(self.edges) > 0:
            edges_str = '\n' + ('\n'.join(list(map(lambda edge: f'{self.name} depends on {edge}', self.edges))))

        # Then we can combine all the relevant properties into a human-readable
        # string.
        return f"{self.name}: {self.vertex_type} " \
               f"{f'({self.attributes})' if self.attributes else ''}" \
               f"{edges_str}"


_VertexReferenceType = TypeVar('_VertexReferenceType', str, Vertex)
"""
Placeholder type for use in generics that reference a vertex.
Must be either a string, or a Vertex.
"""


class VertexEdge:
    """
    An edge between multiple vertices. This has a one-to-one relationship
    between the owning vertex (which will be known from context as it will be
    the owning vertex) and its dependency.
    """

    def __init__(self,
                 dependency: _VertexReferenceType,
                 label: str = None,
                 color: str = None):
        """
        Initializes a (directed) vertex edge for an owner node, that holds a
        dependency node. This also allows metadata to be set on this edge, such
        as color or label.

        :param dependency: A dependency node that points into the owner node.
        """

        self.dependency: _VertexReferenceType = dependency
        """A dependency node that points into the owner node via this edge."""

        self.label = label
        self.color = color

    def __str__(self):
        dependency_name = self.dependency if isinstance(self.dependency, str) else self.dependency.name

        human_label = "Recovery Method" if self.label == 'rec' else self.label
        label_str = f' ({human_label})' if (human_label is not None and human_label != '') else ''

        return f"{dependency_name}{label_str}"
