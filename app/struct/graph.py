from typing import Dict, Optional, Union

from app.struct.vertex import Vertex

VertexDictionary = Dict[str, Vertex]
"""
A dictionary of vertices, as held within a graph.
The key is the name of the vertex and the value is the vertex itself.
"""


class Graph:
    """
    An implementation of the graph data structure. This stores a collection of
    related Vertex classes.
    """

    def __init__(self, known_vertices: Optional[Union[VertexDictionary, list[Vertex]]] = None):
        """
        Initializes a graph. Optionally, a set of known vertices may
        be specified to skip computation of their relationship with other
        vertices in the graph.

        :param known_vertices: Optionally, a set of already known vertices for
        the graph either in the form of a dictionary with key as vertex nam
        and value as vertex OR in the form of a list (where this conversion
        will be done automatically within the constructor).
        """

        if isinstance(known_vertices, list):
            known_vertices = Graph.__vertex_list_to_dict(known_vertices)

        self.vertices: VertexDictionary = {} if known_vertices is None else known_vertices
        """
        The dictionary of vertices in the graph, keyed by the (unique) name of
        the vertex."""

    def add_vertex(self, vertex):
        """Add a given vertex to the graph."""
        if vertex not in self.vertices:
            self.vertices[vertex.name] = vertex
        else:
            raise KeyError(f"Vertex, {vertex.name}, already exists in the graph.")

    @staticmethod
    def __vertex_list_to_dict(vertices: list[Vertex]):
        # Use dictionary comprehension to automatically map a vertices into a
        # dictionary keyed by vertex.name.
        return {vertex.name: vertex for vertex in vertices}
