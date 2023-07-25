"""
Plugin package for agtool.

This package contains plugins used to extend the functionality of agtool (or to implement
functionality aside from the core of agtool). Some are included with agtool by default,
such as file readers and writers, while others can be obtained from or provided by third
parties.

Once added to the `plugins/` directory, plugins are automatically loaded by agtool at
runtime. The directories are scanned recursively for plugin implementations (which are
Python classes that implement the `agtool.interfaces.plugin.AGPlugin` interface either
directly or indirectly - e.g., via `agtool.interfaces.reader.AGReader` or
`agtool.interfaces.writer.AGWriter`).

If the path to the plugins directory is kept as it is by default, the path to the plugins
directory need not be specified when running agtool. However, if the plugins directory is
moved, or you would like to store plugins elsewhere, you can specify the path to the
plugins directory using the `--plugins-dir` command-line argument.
"""
