from typing import TypeVar

from agtool.abstract import AbstractPlugin, AbstractController

PluginExtensionGeneric = TypeVar('PluginExtensionGeneric')
"""
An extension of a plugin. This can be any class type, as defined by the plugin.
This TypeVar is used to specify the type of the extension when loading it with
one of the plugin extension loading methods so the correct type can be returned.
"""


class AGPlugin(AbstractPlugin):
    """
    Base class for all plugins.
    """

    def __init__(self, controller: AbstractController):
        """
        The initializer for the plugin. This is called by the plugin registry
        when the plugin is loaded.

        Note that a plugin has only one instance per application, so this
        initializer is only called once per application run. You can use it to
        initialize any global state that the plugin needs.

        If you would prefer an instance per graph, you can simply implement
        a class for processing an individual graph and then use the plugin as
        a factory for creating instances of that class when a request is made
        to your plugin.

        :param controller: The application controller.
        """

        self.controller: AbstractController = controller
        """The application controller"""

    def load_all_extensions(self,
                            subclass_of: PluginExtensionGeneric) -> list[PluginExtensionGeneric]:
        """
        See `agtool.abstract.plugin_registry.AbstractPluginRegistry.load_all_extensions`
        """
        return self.controller.plugins.load_all_extensions(self, subclass_of)

    def load_extension_from_file(self,
                                 file: str,
                                 subclass_of: PluginExtensionGeneric) -> list[PluginExtensionGeneric]:
        """
        See `agtool.abstract.plugin_registry.AbstractPluginRegistry.load_extension_from_file`
        """
        return self.controller.plugins.load_extension_from_file(self, file, subclass_of)
