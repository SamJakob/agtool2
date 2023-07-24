"""
IMPORTS FOR THIS MODULE SHOULD ALL BE FROM app.abstract, NOT app.abstract.*

The abstract module is used to define abstract base classes that are used
throughout the application. These are used to define interfaces that plugins
must implement, and to define abstract base classes that are used to define
core functionality that is implemented by the application controller.

The abstract module is not used for classes that make up the business-logic -
such as the class for the actual account graph representation, or any kind of
implementations of the interfaces defined in this module. Those belong in
app/struct and app/interfaces, respectively.

The purpose of this module is to define a core abstract layer for classes that
define API interfaces that are mutually dependent on each other. For example,
the AbstractController class is used to define the interface for the
application controller, which is used by plugins. However, the application
controller also needs to manage plugins, which is done with an
AbstractPluginRegistry instance. The application controller AND registry can
both be used by plugins, but the registry is dependent on the controller, and
the controller is dependent on the registry, both are dependent on plugins
which are dependent on one or both. This is a circular dependency that can be
resolved by defining the interfaces in this module, and then implementing them
in their respective modules.
"""

from .plugin import *
from .plugin_registry import *

# Import this last. It depends on the other modules in this package.
from .controller import *
