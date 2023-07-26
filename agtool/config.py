from typing import Literal, Optional, get_args

# Represents a selected log level from a list of possible (supported) log
# levels by the logger (that have associated log level values).
AppLogLevel = Literal[
    "TRACE",
    "DEBUG",
    "INFO",
    "SUCCESS",
    "WARNING",
    "ERROR",
    "CRITICAL"
]

# The list of supported log levels.
AppSupportedLogLevels = get_args(AppLogLevel)


class AppConfig:

    def __init__(self,
                 input_file: str,
                 output_file: str = None,
                 override_action: Optional[str] = None,
                 verbosity: AppLogLevel = "INFO",
                 plugins_dir: str = "plugins/",
                 input_format: Optional[str] = None,
                 output_format: Optional[str] = None,
                 settings: Optional[dict[str, str]] = None):
        self.override_action = override_action
        """
        If specified, this will override the action that would otherwise be
        taken by the application. The application will exit after performing
        the specified action.
        
        For example, this is used by --list-plugins to override the default
        action to simply list the plugins and exit.
        """

        self.verbosity: AppLogLevel = verbosity
        """
        The minimum verbosity of a given log message.
        For example, if this is set to "INFO", only messages with a log level
        of "INFO" or greater will be displayed (i.e., not "TRACE" or
        "DEBUG").

        See "The severity levels" in the loguru manual for further details.
        https://buildmedia.readthedocs.org/media/pdf/loguru/stable/loguru.pdf
        (archived Dec 28, 2022):
        https://web.archive.org/web/20221228161553/https://buildmedia.readthedocs.org/media/pdf/loguru/stable/loguru.pdf
        """

        self.plugins_dir: str = plugins_dir
        """
        The directory in which to search for plugins.
        
        This is relative to the repository root.
        (i.e., the parent of the bin/ directory).
        """

        self.input_format: Optional[str] = input_format
        """The input format that should be expected."""

        self.output_format: Optional[str] = output_format
        """The requested (desired) output format."""

        self.input_file: str = input_file
        """The path to the input file that should be read."""

        self.output_file: Optional[str] = output_file
        """The path to the output file that should be written."""

        self.settings: dict[str, str] = settings or {}
        """
        A dictionary of settings that may be read by the application or its plugins.
        
        Settings are global, so they are not associated with any particular
        plugin or the application itself. As such, if you would like to implement a
        plugin-specific setting, you should prefix the setting name with the
        plugin's name (e.g., "my_plugin.my_setting") - or some scheme that otherwise
        uniquely identifies the plugin.
        
        You may alternatively use your plugin name as the key and take some arbitrary
        value (e.g., a JSON string) if you would prefer greater flexibility. 
        """
