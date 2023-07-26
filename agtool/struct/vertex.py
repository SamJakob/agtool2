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

    @property
    def is_recovery(self) -> bool:
        """
        Returns true if this edge is a recovery method, or false if it is a
        normal method.
        """
        if self.label is None:
            return False

        return 'rec' in self.label

    @property
    def is_conjunction(self) -> bool:
        """
        Returns true if this edge forms a conjunction with other edges, or
        false if not.
        """
        return self._is_conjunction

    @property
    def is_hidden(self) -> bool:
        """
        Whether the edge should be hidden in the graph. Returns true if it should
        be, or false if it should not be hidden.
        """
        if self.label is None:
            return False

        return 'invis' in self.label

    @property
    def group_id(self) -> Optional[int]:
        """
        Returns the group ID of this edge, or None if it is not in a group.
        This group ID is unique to the sink (target) vertex.

        See also `unique_group_id`.
        """
        return self._group_id

    @property
    def unique_group_id(self) -> Optional[int]:
        """
        Returns the group ID of this edge, or None if it is not in a group.
        The unique group ID is unique to the entire graph, rather than just the
        sink (target) vertex.

        See also `group_id`.
        """
        return self._unique_group_id

    def __init__(self,
                 dependency: _VertexReferenceType,
                 label: str = None,
                 group_id: Optional[int] = None,
                 unique_group_id: Optional[int] = None,
                 is_conjunction: bool = False):
        """
        Initializes a (directed) vertex edge for an owner node, that holds a
        dependency node. This also allows metadata to be set on this edge, such
        as color or label.

        It is expected that `group_id` and `unique_group_id` will be precomputed
        at the reading stage, and that the edges will be instantiated with these
        values already set. Even if the edges are not grouped, they should still
        be given a group ID in sequence as if they were grouped, as it can be used
        to signify the overall access methods that are used to access a given
        vertex.

        `is_conjunction` should instead be set to true if the edge is a
        conjunction. **It is an error for `is_conjunction` to be `False` and
        `unique_group_id` to have a duplicate value between any vertices.**

        :param dependency: A dependency node that points into the owner node.
        :param label: An optional label to be applied to the edge. (This may be
            displayed textually or graphically depending on the theme).
        :param group_id: An optional group ID to be applied to the edge. This
            is used to group conjunctions together.
            For theming reasons, these should ideally be normalized to be consecutive
            integers starting from 0 before the edges are instantiated.
        :param unique_group_id: An optional unique group ID to be applied to the
            edge. This is used to group conjunctions together. This is unique
            across the entire graph, rather than just the sink (target) vertex.
        """

        self.dependency: _VertexReferenceType = dependency
        """A dependency node that points into the owner node via this edge."""

        self.label = label
        """The label for this edge."""

        self._group_id = group_id
        self._unique_group_id = unique_group_id
        self._is_conjunction = is_conjunction

    def __str__(self):
        dependency_name = self.dependency if isinstance(self.dependency, str) else self.dependency.name

        human_label = "Recovery Method" if self.label == 'rec' else self.label
        label_str = f' ({human_label})' if (human_label is not None and human_label != '') else ''

        return f"{dependency_name}{label_str}"
