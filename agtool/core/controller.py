import inspect
import os.path
import sys
from datetime import datetime
from typing import Optional
from loguru import logger as loguru

from agtool.abstract import AbstractController, AbstractPluginRegistry
from agtool.config import AppConfig, AppSupportedLogLevels
from agtool.error import AGMissingPluginError
from agtool.helpers.cli import AppInfo, AppInfoVersion
from agtool.helpers.logger import LoggerType
from agtool.interfaces.plugin import AGPlugin
from agtool.interfaces.reader import AGReader
from agtool.interfaces.writer import AGWriter


class Controller(AbstractController):
    """
    The application controller.
    """

    @property
    def logger(self) -> LoggerType:
        """
        The application logger.

        This is a copy of loguru that has had the application name and metadata
        bound to it.

        If this is called from within a plugin, the logger will be automatically
        bound to the plugin's ID.
        """

        # Read the previous stack frame and fetch the locals from it.
        stack_frame = inspect.currentframe()

        prev_stack_frame = stack_frame.f_back
        while prev_stack_frame is not None:
            prev_stack_locals = prev_stack_frame.f_locals

            # If there's a 'self' in the previous stack frame, and it's an
            # AGPlugin, then we'll use its ID as the logger name (i.e., a
            # plugin-specific logger).
            if 'self' in prev_stack_locals:
                caller = prev_stack_frame.f_locals['self']
                if issubclass(caller.__class__, AGPlugin):
                    # Render up to 20 characters of the plugin ID.
                    # The name field in the logger is limited to 30 characters, so
                    # we'll limit the plugin ID to 20 characters to leave room for
                    # the "(plugin)" suffix.
                    name = f"{caller.id[:20]} (plugin)"
                    return loguru.bind(name=name)

            prev_stack_frame = prev_stack_frame.f_back

        # Otherwise, we'll just use the application name (i.e., the
        # application-wide logger).
        return self._logger

    @property
    def debug(self) -> bool:
        return AppSupportedLogLevels.index(self.config.verbosity) <= AppSupportedLogLevels.index("DEBUG")

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> AppInfoVersion:
        return self._version

    @property
    def description(self) -> list[str]:
        return self._description

    @property
    def timestamp(self) -> str:
        return datetime.now().strftime("%b/%d/%Y %-I:%M:%S %p")

    @property
    def config(self) -> AppConfig:
        return self._config

    @property
    def standalone(self) -> bool:
        return self._standalone

    @property
    def plugins(self) -> AbstractPluginRegistry:
        return self._plugins

    def __init__(self,
                 app_info: AppInfo,
                 config: AppConfig,
                 standalone: bool = False,
                 base_path: Optional[str] = None):

        self._name = app_info.name
        self._version = app_info.version
        self._description = app_info.description

        self._config = config
        """The application's current configuration"""

        self._standalone = standalone
        """
        Whether the application should run in standalone mode (e.g.,
        initializing its own logger, etc.,)
        """

        self.base_path = base_path
        """
        The base path that should be used to resolve relative paths for
        files and services used by the application.
        """

        # Resolve the path to the plugins directory.
        # If root_path is specified, it is assumed to be the path to the
        # repository root (i.e., the parent of the bin/ directory).
        # Otherwise, we'll resolve relative to the current working directory.
        plugins_dir = os.path.abspath(f"{base_path}/{config.plugins_dir}"
                                      if base_path
                                      else config.plugins_dir)

        # Initialize the plugin registry.
        from agtool.core.plugin_registry import AGPluginRegistry
        self._plugins = AGPluginRegistry(self, plugins_dir)
        """The application's plugin registry"""

        # If we're running in standalone mode, start up the application
        # components.
        if standalone:
            # Start up logging (colored console logging goes to standard error
            # per convention). Logging can also be set up to go to a file.
            loguru.remove()
            loguru.add(sys.stderr,
                       level=config.verbosity,
                       colorize=True,
                       format="<green>{time:MMM/DD/YYYY h:mm:ss A}</green>"
                              " | <cyan>{extra[name]: <30}</cyan>"
                              " | <level>{level: <8}</level>"
                              " | <level>{message}</level>")

            self._logger = loguru.bind(name=self._name)
            self._logger.info(f"Starting {self._name} {self._version}...")

            # Load plugins.
            self.plugins.load_all_plugins()

    def reader_for(self, format_name: str):
        """
        Get a reader for the specified file extension or format name.
        e.g., 'txt', 'json', etc.,

        For now, this is trivially found by searching through the list of
        plugins implementing AGReader fetched from the plugin registry for one where
        its `default_file_extension` property matches the given `format_name`.
        :param format_name: The name of the format (typically the file
        extension) that the reader should support.
        :return: The AGReader instance of a reader that supports the specified
        file name, or an `AGMissingPluginError` if no such reader could be
        found.
        """

        # Fetch the reader plugins from the plugin registry.
        readers = self.plugins.get_plugins_of_type(AGReader)

        # Search through the readers for one that supports the specified
        # format.
        for reader in readers:
            if reader.default_file_extension == format_name:
                return reader

        # If we get here, we didn't find a reader for the specified format.
        raise AGMissingPluginError(f"No reader found for format '{format_name}'")

    def writer_for(self, format_name: str):
        """
        Get a writer for the specified file extension or format name.
        e.g., 'dot', 'png', etc.,

        For now, this is trivially found by searching through the list of
        plugins implementing AGWriter fetched from the plugin registry for one where
        its `default_file_extension` property matches the given `format_name`.
        :param format_name: The name of the format (typically the file
        extension) that the writer should support.
        :return: The AGWriter instance of a writer that supports the specified
        file name, or an `AGMissingPluginError` if no such writer could be
        found.
        """

        # Fetch the writer plugins from the plugin registry.
        writers = self.plugins.get_plugins_of_type(AGWriter)

        # Search through the writers for one that supports the specified
        # format.
        for writer in writers:
            if writer.default_file_extension == format_name:
                return writer

        # If we get here, we didn't find a writer for the specified format.
        raise AGMissingPluginError(f"No writer found for format '{format_name}'")
