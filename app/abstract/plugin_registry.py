# DO NOT IMPORT THIS FILE DIRECTLY. IMPORT FROM app.abstract INSTEAD.

from abc import ABC, abstractmethod
from typing import List, Type, TypeVar

from app.abstract import AbstractPlugin

AbstractPluginGeneric = TypeVar('AbstractPluginGeneric', bound=AbstractPlugin)


class AbstractPluginRegistry(ABC):
    """
    Abstract class that exposes functionality of a plugin registry.
    """

    @abstractmethod
    def load_all_plugins(self):
        """Load all plugins (recursively) from the plugins directory."""

    @abstractmethod
    def load_plugin_from_file(self, file: str) -> bool:
        """
        Load a plugin from a given path (to a Python file).
        :param file: The path to the plugin file.
        :return: True if the plugin was loaded successfully, False otherwise.
        """

    @abstractmethod
    def register_plugin(self, plugin: AbstractPlugin):
        """
        Register a plugin with the registry.
        :param plugin: The plugin to register.
        """

    @abstractmethod
    def get_plugins_of_type(self, plugin_type: Type[AbstractPluginGeneric]) -> List[AbstractPluginGeneric]:
        """
        Get all plugins that are of (or a subclass of) the specified type.
        :param plugin_type: The type of plugin to get.
        :return: A list of plugins of the given type.
        """

    @abstractmethod
    def get_plugins_of_exact_type(self, plugin_type: Type[AbstractPluginGeneric]) -> List[AbstractPluginGeneric]:
        """
        Get all plugins that are of a specific type.
        :param plugin_type: The type of plugin to get.
        :return: A list of plugins of the given type.
        """

    @abstractmethod
    def get_all_plugins(self) -> List[AbstractPlugin]:
        """
        Get all plugins.
        :return: A list of all plugins.
        """

    @abstractmethod
    def render_plugins_table(self) -> str:
        """
        Renders an ASCII table of all plugins in the registry.
        :return: The ASCII table of plugins, as a string.
        """

    @abstractmethod
    def render_plugins_json(self) -> str:
        """
        Renders a JSON representation of all plugins in the registry.
        :return: The JSON representation of plugins, as a string.
        """
