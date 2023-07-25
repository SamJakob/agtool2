"""
This module is for organizational purposes only. The contents of the entire plugin
directory are automatically loaded recursively.

`agtool.interfaces.writer.AGWriter`s in this directory use the Graphviz application
to render a visual graph based on the application (input) graph. This is done by
using the `AGGraphvizWriter` to render the graph as a DOT file, essentially
converting the representation of the graph to one understood by Graphviz.

For image formats, such as PNG, or PDF, writers first call the
`plugins.writers.graphviz.graphviz_writer.AGGraphvizWriter` to create a DOT
representation of the graph, and then pass it to the Graphviz command-line
tool to render the graph as the requested image format.
"""
