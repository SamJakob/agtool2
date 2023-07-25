# DO NOT IMPORT THIS FILE DIRECTLY. IMPORT FROM agtool.abstract INSTEAD.

from abc import ABC, abstractmethod
from typing import List, Type

from agtool.abstract import AbstractPlugin, AbstractPluginExtensionGeneric, AbstractPluginGeneric


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
    def load_all_extensions(self,
                            plugin: AbstractPlugin,
                            subclass_of: AbstractPluginExtensionGeneric)\
            -> list[Type[AbstractPluginExtensionGeneric]]:
        """
        Loads all extension _classes_ that are subclasses of the given class.
        This will search the plugin registry's plugin directory recursively for
        all classes that are subclasses of the given class and load them using
        the `load_extension_from_file` method.

        **Unlike with plugins, this method will not instantiate the extensions.**

        Please see the notes on `load_extension_from_file` for caveats on using this
        method.

        :param plugin: The plugin requesting the load. This is used for log
        messages and may be used in future to memoize or cache extensions.
        :param subclass_of: The class that the extensions must be subclasses of.
        """
        pass

    @abstractmethod
    def load_extension_from_file(self,
                                 plugin: AbstractPlugin,
                                 file: str,
                                 subclass_of: AbstractPluginExtensionGeneric)\
            -> list[Type[AbstractPluginExtensionGeneric]]:
        """
        Loads any extensions from the given file (subclasses of the given class).

        Note that this function returns a list of extensions, as a single file
        may contain multiple extensions.

        **Unlike with plugins, this method will not instantiate the extensions.**

        > **Note**: This method is intended to allow you to load plugins in a similar
        > manner to how you would load plugins. There are, however, some caveats to
        > this method, so you may wish to use your own method for loading extensions.
        >
        > If you want subclass_of to resolve any intermediate classes (e.g., you have
        > `A -extends-> B -extends-> C`, and you want to load all subclasses of `A`,
        > you must have `A`, `B`, and `C` loaded before calling this method. This is because
        > the plugin registry relies on Python's type system to determine if a class
        > is a subclass of another class, and if the intermediate classes are not
        > loaded, then the type system will not be able to resolve the inheritance
        > chain. **This is not an issue if you want direct subclasses of a class,** as
        > the type system will be able to resolve the inheritance chain for direct
        > subclasses without issue (they're guaranteed to be loaded because they're
        > passed to this method via the `subclass_of` parameter).

        :param plugin: The plugin requesting the load. This is used for log
        messages and may be used in future to memoize or cache extensions.
        :param file: The file (path) to load extensions from.
        :param subclass_of: The class that the extensions must be subclasses of.
        """
        pass

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
