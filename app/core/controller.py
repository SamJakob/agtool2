import os.path
import sys
from typing import List, Optional

from loguru import logger as _logger

from app.abstract import AbstractController, AbstractPluginRegistry
from app.config import AppConfig, AppSupportedLogLevels
from app.error import AGMissingPluginError
from app.interfaces.reader import AGReader


class Controller(AbstractController):
    """
    The application controller.
    """

    logger: _logger
    """
    The application logger.

    This is a copy of loguru that has had the application name and metadata
    bound to it.
    """

    @property
    def debug(self) -> bool:
        return AppSupportedLogLevels.index(self.config.verbosity) <= AppSupportedLogLevels.index("DEBUG")

    @property
    def name(self) -> str:
        return self._name

    @property
    def config(self) -> AppConfig:
        return self._config

    @property
    def standalone(self) -> bool:
        return self._standalone

    @property
    def plugins(self) -> AbstractPluginRegistry:
        return self._plugins

    @property
    def account_graph_readers(self) -> List[AGReader]:
        """
        Convenience property for accessing a list of account graph readers,
        from the plugin registry.
        :return: A list of all registered account graph readers (`AGReader`).
        """
        return self.plugins.get_plugins_of_type(AGReader)

    def __init__(self,
                 name: str,
                 config: AppConfig,
                 standalone: bool = False,
                 root_path: Optional[str] = None):

        self._name = name

        self._config = config
        """The application's current configuration"""

        self._standalone = standalone
        """Whether the application should run in standalone mode (e.g.,
        initializing its own logger, etc.,)"""

        # Resolve the path to the plugins directory.
        # If root_path is specified, it is assumed to be the path to the
        # repository root (i.e., the parent of the bin/ directory).
        # Otherwise, we'll resolve relative to the current working directory.
        plugins_dir = os.path.abspath(f"{root_path}/{config.plugins_dir}"
                                      if root_path
                                      else config.plugins_dir)

        # Initialize the plugin registry.
        from app.core.plugin_registry import AGPluginRegistry
        self._plugins = AGPluginRegistry(self, plugins_dir)
        """The application's plugin registry"""

        # If we're running in standalone mode, start up the application
        # components.
        if standalone:
            # Start up logging (colored console logging goes to standard error
            # per convention). Logging can also be set up to go to a file.
            _logger.remove()
            _logger.add(sys.stderr,
                        level=config.verbosity,
                        colorize=True,
                        format="<green>{time:MMM/DD/YYYY HH:mm:ss}</green>"
                               " | <cyan>{extra[name]}</cyan>"
                               " | <level>{level: <8}</level>"
                               " | <level>{message}</level>")

            self.logger = _logger.bind(name=name)
            self.logger.info(f"Starting {name}...")

            # Load plugins.
            self.plugins.load_all_plugins()

    def reader_for(self, format_name: str):
        """
        Get a reader for the specified file extension or format name.
        e.g., 'txt', 'json', etc.,

        For now, this is trivially found by searching through the list of
        `account_graph_readers` fetched from the plugin registry for one where
        its `default_file_extension` property matches the given `format_name`.
        :param format_name: The name of the format (typically the file
        extension) that the reader should support.
        :return: The AGReader instance of a reader that supports the specified
        file name, or an `AGMissingPluginError` if no such reader could be
        found.
        """

        # Fetch the reader plugins from the plugin registry.
        readers = self.account_graph_readers

        # Search through the readers for one that supports the specified
        # format.
        for reader in readers:
            if reader.default_file_extension == format_name:
                return reader

        # If we get here, we didn't find a reader for the specified format.
        raise AGMissingPluginError(f"No reader found for format '{format_name}'")
