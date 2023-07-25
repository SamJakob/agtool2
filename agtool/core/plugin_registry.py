import importlib
import importlib.util
import inspect
import json
import os
import pkgutil
import sys
from ast import ClassDef as AstClassDef, parse as parse_ast
from typing import Dict, List, Type, cast

from tabulate import tabulate

import agtool.interfaces
from agtool.abstract import AbstractPluginGeneric, AbstractPluginRegistry, AbstractPluginExtensionGeneric
from agtool.core import Controller
from agtool.error import AGPluginConflictError, AGPluginError
from agtool.interfaces.plugin import AGPlugin


class _AGPluginRegistryEntry:
    """An entry in the registry for an AGPlugin."""

    def __init__(self,
                 plugin: AGPlugin,
                 interface: Type[AGPlugin]):
        self._plugin = plugin
        """The plugin itself."""

        self._interface = interface
        """The interface that the plugin implements."""

    @property
    def plugin(self) -> AGPlugin:
        return self._plugin

    @property
    def interface(self) -> Type[AGPlugin]:
        return self._interface


class AGPluginRegistry(AbstractPluginRegistry):
    """A loader and registry for plugins for agtool."""

    def __init__(self,
                 controller: Controller,
                 plugins_dir: str):
        self.controller = controller
        """The application controller"""

        self.plugins_dir = plugins_dir
        """
        The (absolute) path to the directory containing plugins for agtool.
        """

        self._plugins: Dict[str, _AGPluginRegistryEntry] = {}
        """
        The map of registered plugins.
        The key is the unique identifier of the plugin. The value is an entry
        object containing the plugin itself and additional metadata, such as
        the plugin interface that it implements.
        """

        # Ensure all the possible plugin interfaces are loaded
        self._load_submodules(agtool.interfaces)
        _plugin_interfaces = {}

        # Iterate over all the modules in agtool.interfaces, and find all the
        # classes that inherit from AGPlugin
        submodules = [submodule.name for submodule in pkgutil.iter_modules(agtool.interfaces.__path__)]
        for submodule_name in submodules:
            # For each class, if is AGPlugin itself or a subclass of
            # AGPlugin, add it to the set of interfaces.
            members = inspect.getmembers(sys.modules['agtool.interfaces.' + submodule_name], inspect.isclass)
            for member_name, member in members:
                if issubclass(member, AGPlugin):
                    _plugin_interfaces[member_name] = member

        # Register the set of interfaces.
        self._plugin_interfaces = _plugin_interfaces
        """The set of interfaces that plugins can implement."""

    def load_all_extensions(self,
                            plugin: AGPlugin,
                            subclass_of: AbstractPluginExtensionGeneric) -> List[AbstractPluginExtensionGeneric]:
        self.controller.logger.info(f"Scanning for extensions for \"{plugin.name}\" in {self.plugins_dir}...")

        extensions = []

        # Load all extensions from the plugins directory
        for root, dirs, filenames in os.walk(self.plugins_dir):
            for filename in filenames:
                if filename.endswith(".py") \
                        and not filename.endswith("-disabled") \
                        and not filename.startswith("_"):

                    # Add the extensions from the file to the list of extensions discovered.
                    extensions.extend(self.load_extension_from_file(plugin, os.path.join(root, filename),
                                                                    subclass_of=subclass_of))

        if len(extensions) > 0:
            self.controller.logger.success(
                f"Finished loading extensions for \"{plugin.name}\". "
                f"{len(extensions)} extension{'s are' if len(extensions) != 1 else ' is'} ready."
            )
        else:
            self.controller.logger.info(
                f"No extensions for \"{plugin.name}\" were found."
            )

        return extensions

    def load_extension_from_file(self,
                                 plugin: AGPlugin,
                                 file: str,
                                 subclass_of: AbstractPluginExtensionGeneric) -> list[AbstractPluginExtensionGeneric]:

        extensions = []

        self.controller.logger.trace(f"Looking for extensions for \"{plugin.name}\" in {file}...")

        # Attempt to derive a spec and module from the file
        spec = importlib.util.spec_from_file_location(os.path.basename(file), file)
        file_module = importlib.util.module_from_spec(spec)

        # Find the list of valid superclasses for the extension.
        valid_superclasses = [subclass_of.__name__]
        valid_superclasses.extend([clazz.__name__ for clazz in subclass_of.__subclasses__()])

        try:
            file_source = parse_ast(inspect.getsource(file_module))
            file_imported = False
            """Whether the file has been imported into the runtime yet."""

            for node in file_source.body:
                # If the node is a class definition, check if one of its bases is
                # subclass_of or a subclass of subclass_of.
                if isinstance(node, AstClassDef):
                    # Get the list of base classes.
                    bases = [base.id for base in cast(any, node.bases)]

                    if subclass_of.__name__ in bases:
                        # Load the plugin module. If it has already been loaded,
                        # we can skip it. If file_imported is False, we can
                        # assume that the plugin module has not been loaded yet.
                        if not file_imported:
                            spec.loader.exec_module(file_module)

                            # Mark that the file has been imported.
                            file_imported = True

                        # Then, add the extension to the list of extensions.
                        extensions.append(getattr(file_module, node.name)(plugin=plugin))

        except OSError:
            # Do nothing if the source cannot be obtained.
            pass

        return extensions

    def load_all_plugins(self):
        self.controller.logger.info(f"Scanning for plugins in {self.plugins_dir}...")

        # Load all plugins from the plugins directory
        for root, dirs, filenames in os.walk(self.plugins_dir):
            for filename in filenames:
                if filename.endswith(".py") \
                        and not filename.endswith("-disabled") \
                        and not filename.startswith("_"):
                    # Load the plugin
                    self.load_plugin_from_file(os.path.join(root, filename))

        self.controller.logger.success(
            f"Finished loading plugins. "
            f"{len(self._plugins)} plugin{'s are' if len(self._plugins) != 1 else ' is'} ready."
        )

    def load_plugin_from_file(self, file: str) -> bool:
        self.controller.logger.trace(f"Looking for plugins in {file}...")

        # Attempt to derive a spec and module from the file
        spec = importlib.util.spec_from_file_location(os.path.basename(file), file)
        file_module = importlib.util.module_from_spec(spec)

        # Load the plugin module by parsing the AST of the file to determine
        # if it contains a class that extends AGPlugin
        file_has_plugin = False

        loaded_plugins = 0
        """The number of plugins loaded from the file"""

        try:
            file_source = parse_ast(inspect.getsource(file_module))

            for node in file_source.body:
                # If the node is a class definition, check if one of its bases is
                # AGPlugin or a subclass of AGPlugin.
                if isinstance(node, AstClassDef):
                    is_plugin = False

                    bases = [base.id for base in cast(any, node.bases)]
                    plugin_type = None

                    if "AGPlugin" in bases:
                        plugin_type = AGPlugin
                        is_plugin = True
                    else:
                        # Search for a subclass of AGPlugin
                        for base in bases:
                            if self._is_plugin_superclass(base):
                                plugin_type = self._plugin_interfaces[base]
                                is_plugin = True
                                break

                    if is_plugin:
                        # Load the plugin module. If it has already been loaded,
                        # we can skip it. If file_has_plugin is False, we can
                        # assume that the plugin module has not been loaded yet.
                        if not file_has_plugin:
                            spec.loader.exec_module(file_module)

                            # Mark that the file contains a plugin (and has thus
                            # been loaded)
                            file_has_plugin = True

                        # Register and instantiate the plugin.
                        plugin_type_str = f' {plugin_type.__name__}' if plugin_type is not None else ""
                        self.controller.logger.info(
                            f"Attempting to initialize class {node.name} as a(n){plugin_type_str} plugin..."
                        )

                        # Instantiate the plugin
                        plugin_class: Type[AGPlugin] = getattr(file_module, node.name)
                        plugin: AGPlugin = plugin_class(controller=self.controller)

                        # Register the plugin
                        self.register_plugin(plugin)
                        loaded_plugins += 1

        except OSError:
            # Do nothing if the source cannot be obtained.
            pass

        if file_has_plugin:
            self.controller.logger.success(
                f"Successfully registered {loaded_plugins} plugin{'s' if loaded_plugins != 1 else ''} from "
                f"{os.path.basename(file)}"
            )
        else:
            self.controller.logger.trace(
                f"File {os.path.basename(file)} does not contain a class that extends AGPlugin, skipping..."
            )

        return file_has_plugin

    def register_plugin(self, plugin: AGPlugin):
        if plugin.id in self._plugins:
            existing_plugin = self._plugins[plugin.id].plugin

            self.controller.logger.error(
                f"Duplicate plugin ID '{plugin.id}' found. If this is the same "
                f"plugin, please remove the duplicate. If this is a different "
                f"plugin, please change the plugin ID."
            )
            self.controller.logger.error(
                f"Ideally, you should change the class name such that it is "
                f"unique, but if you cannot do that, you can override the ID "
                f"property of the plugin class to define a custom ID."
            )
            raise AGPluginConflictError(plugin_id=plugin.id,
                                        description=f"The plugin {plugin.id} is already in use by {existing_plugin.id} "
                                                    f"({existing_plugin.name}). It cannot be registered again.")

        # Determine which interface the plugin implements
        plugin_interface = None

        # We compare the plugin's base classes to the plugin interfaces
        # to determine which interface the plugin implements.
        #
        # This is done by name instead of with isinstance to ensure that the
        # plugin interface is not a subclass of the plugin's base class.
        for base in plugin.__class__.__bases__:
            if base.__name__ in self._plugin_interfaces:
                plugin_interface = self._plugin_interfaces[base.__name__]
                break

        if plugin_interface is None:
            raise AGPluginError(
                plugin_id=plugin.id,
                description=f"The plugin {plugin.id} does not implement any of the known plugin interfaces. "
                            f"Please ensure that the plugin extends one of the following classes: "
                            f"{', '.join(self._plugin_interfaces.keys())}"
            )

        self._plugins[plugin.id] = _AGPluginRegistryEntry(
            plugin=plugin,
            interface=plugin_interface,
        )

        plugin_type_str = f' {plugin_interface.__name__}' if plugin_interface is not AGPlugin else ""
        self.controller.logger.info(
            f"Registered{plugin_type_str} plugin '{plugin.name}' (version {plugin.version}) "
            f"by {plugin.author} ({plugin.license} license)"
        )

    def get_plugins_of_type(self, plugin_type: Type[AbstractPluginGeneric]) -> List[AbstractPluginGeneric]:
        return [entry.plugin for entry in self._plugins.values() if isinstance(entry.plugin, plugin_type)]

    def get_plugins_of_exact_type(self, plugin_type: Type[AbstractPluginGeneric]) -> List[AbstractPluginGeneric]:
        return [entry.plugin for entry in self._plugins.values() if entry.interface is plugin_type]

    def get_all_plugins(self) -> List[AGPlugin]:
        return [entry.plugin for entry in self._plugins.values()]

    def render_plugins_table(self) -> str:
        registry_entries = self._get_all_registry_entries()

        result = f"Registered plugins ({len(registry_entries)}):\n"

        table = [
            # Table Header Row
            ['ID', 'Type', 'Name', 'Version', 'Author', 'License']
        ]

        # Loop over each plugin, and add a row to the table for each one.
        for entry in registry_entries:
            # The plugin instance itself (we can fetch the metadata from this)
            plugin = entry.plugin
            # The plugin type name (e.g., 'AGPlugin', 'AGReader', etc.,)
            plugin_type = entry.interface.__name__

            table.append([
                plugin.id, plugin_type,
                plugin.name, plugin.version, plugin.author, plugin.license
            ])

        return (result +
                tabulate(table, headers='firstrow', tablefmt='rounded_outline'))

    def render_plugins_json(self) -> str:
        plugins = {}

        for entry in self._get_all_registry_entries():
            # Ensure there is a list for the plugin type.
            if entry.interface.__name__ not in plugins:
                plugins[entry.interface.__name__] = []

            # Now add the plugin to the list.
            plugins[entry.interface.__name__].append({
                'id': entry.plugin.id,
                'name': entry.plugin.name,
                'version': entry.plugin.version,
                'author': entry.plugin.author,
                'license': entry.plugin.license,
            })

        # Return the JSON string.
        return json.dumps(plugins, indent=4)

    def _get_all_registry_entries(self) -> List[_AGPluginRegistryEntry]:
        return list(self._plugins.values())

    def _is_plugin_superclass(self, class_name) -> bool:
        """Check if a class (by name) is a known subclass of AGPlugin."""
        return class_name in self._plugin_interfaces

    @staticmethod
    def _load_submodules(module):
        """Import all submodules of a module, recursively."""
        for loader, module_name, is_pkg in pkgutil.walk_packages(
                module.__path__, module.__name__ + '.'):
            importlib.import_module(module_name)
