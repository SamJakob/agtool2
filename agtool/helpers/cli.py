from argparse import ArgumentParser, RawDescriptionHelpFormatter
from typing import List, NamedTuple, Sequence, Optional

import agtool
from agtool.config import AppConfig, AppSupportedLogLevels
from agtool.error import AGError


class AppInfoVersion(NamedTuple):
    name: str
    date: str

    def __str__(self) -> str:
        return f"{self.name} ({self.date})"


class AppInfo(NamedTuple):
    name: str
    version: AppInfoVersion
    description: List[str]


def get_app_info() -> AppInfo:
    name = agtool.__name__
    version = AppInfoVersion(name=agtool.__version__, date=agtool.__updated__)
    description = agtool.__doc__.strip().split("\n")
    return AppInfo(name=name, version=version, description=description)


def get_readable_app_info(with_long_description=False) -> str:
    """
    Returns the human-readable version information string (ready to be
    printed). This is anticipated to be used with the --version flag, but is
    also exposed to other modules that might want to use this for some reason.

    :return: The human-readable version string for the application.
    """
    _, version, description = get_app_info()
    short_description = description[0]

    # Don't bother generating the long description if with_long_description is
    # False.
    long_description = ("\n\n" + "\n".join(description[1:]).strip()) if with_long_description else ""

    # Generate the short description, then append the long description to it
    # if it is requested.
    return f"""{short_description} (v{version.name})
Last Updated: {version.date}""" + long_description


def parse_cli_args(args: Sequence[str], default_settings: Optional[dict[str, str]] = None) -> AppConfig:
    """
    Parses the list of command-line arguments to determine the application
    configuration.

    Requires that the list of arguments be passed in, even if this is just
    sys.argv to facilitate testing and reduce extraneous code paths.

    :return: An AppConfig object containing the CLI arguments passed to the
    application.
    """

    parser = ArgumentParser(description=get_readable_app_info(),
                            formatter_class=RawDescriptionHelpFormatter,
                            # Don't add the help command (we'll do it ourselves
                            # for greater control over the help text).
                            add_help=False)

    # ---
    # Meta flags and actions (print version information, customize logging)
    # ---

    meta = parser.add_argument_group(title="meta options")

    meta.add_argument("-h", '--help', action='help',
                      help="shows this help message, and exits")

    meta.add_argument("-V", '--version', action='version',
                      version=get_readable_app_info(with_long_description=True),
                      help="shows the program's version information, and exits")

    meta.add_argument("-P", "--list-plugins", action="store_const",
                      dest="override_action", const="list_plugins",
                      help="lists available plugins, and exits")

    # (values are ordered lowest log level to highest)
    meta.add_argument("-L", '--level', default='INFO',
                      help="sets the minimum log level that will be printed; [default: %(default)s]",
                      choices=AppSupportedLogLevels)

    # ---
    # Ordinary program arguments
    # ---

    parser.add_argument('--plugins-dir', default='plugins/',
                        action="store", dest="plugins_dir",
                        help="sets the directory in which to search for plugins; [default: %(default)s]")

    # -it and -ot are aliases for --input-type and --output-type, respectively.
    # -if and -of have been avoided to prevent confusion with input and output
    # file arguments.
    parser.add_argument("-it", '--input-type', '--input-format',
                        action="store", dest="input_format",
                        help="sets the expected input format (guessed heuristically by default)")

    parser.add_argument("-ot", '--output-type', '--output-format',
                        action="store", dest="output_format", default='png',
                        help="sets the desired output format (guessed heuristically by default)")

    parser.add_argument('input', help="sets the input file to read from",
                        action="store")

    parser.add_argument('-o', '--output', '--output-file',
                        action="store", default=None,
                        help="sets the output file to write to; [default: <input_file>.png]")

    parser.add_argument('-s', '--set', '--set-option',
                        action="append", dest="options", default=[],
                        help="sets a global option which may be read by agtool or its plugins (e.g., -s key=value)")

    result = parser.parse_args(args)

    return AppConfig(
        override_action=result.override_action,
        verbosity=result.level,
        plugins_dir=result.plugins_dir,
        input_format=result.input_format,
        output_format=result.output_format,
        input_file=result.input,
        output_file=result.output,
        settings=parse_settings(result.options, defaults=default_settings)
    )


def parse_settings(value: list[str], defaults: Optional[dict[str, str]] = None) -> dict[str, str]:
    """
    Parses a list of settings (e.g., from the command-line) into a dictionary
    of key-value pairs.

    The settings should be specified as a list of strings in the format
    "key=value". The value may be omitted, in which case the value will be
    set to an empty string.

    If multiple equals signs are present, the first equals sign will be used
    to delimit the key from the value. All subsequent equals signs will be
    treated as part of the value.

    Optionally, a dictionary of defaults may be specified. The parsed settings
    will be merged into the defaults, with the parsed settings taking
    precedence.

    :param value: The list of settings to parse.
    :param defaults: Optionally, a dictionary of default settings to use if
    a given setting key is not specified.
    :return: A dictionary of key-value pairs.
    """

    settings = {}
    for setting in value:
        # Split the setting into key and value.
        key, *value = setting.split('=')
        value = '='.join(value)

        key = key.strip()
        if not key:
            raise AGError("Invalid setting: key is empty")

        # Set the value to an empty string if it is not specified.
        if not value:
            value = ""

        # Add the key-value pair to the settings dictionary.
        settings[key] = value

    return (defaults or {}) | settings
