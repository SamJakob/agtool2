"""
Interfaces are stubs (abstract interface classes) that are implemented by
plugins. The agtool core (in agtool/) will attempt to load plugins and will
interact with them based on their implementation of one of the interfaces in
this module.

In other words, to extend the functionality of agtool, create a plugin (in
plugins/) that implements one of the interfaces in this module.

This module MUST NOT be used for classes that make up the business-logic - such
as the class for the actual account graph representation. Those belong in
agtool/struct.
"""
