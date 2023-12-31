# DO NOT IMPORT THIS FILE DIRECTLY. IMPORT FROM agtool.abstract INSTEAD.

from abc import ABC, abstractmethod
from typing import TypeVar

AbstractPluginExtensionGeneric = TypeVar('AbstractPluginExtensionGeneric')


class AbstractPlugin(ABC):
    """An abstract base class for all plugins."""

    @property
    def id(self):
        """
        The ID (class name) of the plugin.
        This is checked for uniqueness by the plugin registry. If two plugins
        have the same ID, the plugin registry will raise an exception.

        If your plugin has a class name that is not unique, you should override
        this property to return a READABLE unique ID (e.g., in reverse domain
        name notation).

        Your ID should also be in lowercase.
        """
        return self.__class__.__name__.lower()

    @property
    def name(self) -> str:
        """The name of the plugin"""

        # Returns the id by default.
        return self.id

    @property
    def version(self) -> str:
        """The version of the plugin"""
        return "0.0.0"

    @property
    def author(self) -> str:
        """The author of the plugin"""
        return "Unknown"

    @property
    def license(self) -> str:
        """The license of the plugin"""
        return "Unknown"

    @abstractmethod
    def load_all_extensions(self,
                            subclass_of: AbstractPluginExtensionGeneric) -> list[AbstractPluginExtensionGeneric]:
        """
        See `agtool.abstract.plugin_registry.AbstractPluginRegistry.load_all_extensions`
        """

    @abstractmethod
    def load_extension_from_file(self,
                                 file: str,
                                 subclass_of: AbstractPluginExtensionGeneric) -> list[AbstractPluginExtensionGeneric]:
        """
        See `agtool.abstract.plugin_registry.AbstractPluginRegistry.load_extension_from_file`
        """


AbstractPluginGeneric = TypeVar('AbstractPluginGeneric', bound=AbstractPlugin)
