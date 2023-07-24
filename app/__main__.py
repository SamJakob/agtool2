import os
import sys
from typing import Optional

from app.core import Controller
from app.error import AGError
from app.helpers.cli import get_app_info, parse_cli_args


# Welcome to the main executable file for this project. This launches the CLI
# application in agtool's "default form factor" (as opposed to being a web or
# desktop application, or part of another application.)

# Package information is retained in app/__init__.py (relatively to project
# root). For more information, please refer to README.md at the root of the
# repository.


def main(argv=None):
    controller: Optional[Controller] = None

    try:
        # Process the specified arguments by including the system arguments, or
        # just fall back to retrieving the system arguments.
        argv = [*sys.argv[1:], *argv] if argv is not None else sys.argv[1:]
        config = parse_cli_args(argv)

        # Read information about the CLI application.
        app_info = get_app_info()

        # Start the controller for dependency injection.
        controller = Controller(
            name=app_info.name,
            config=config,
            standalone=True,
            root_path=os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        )

        # Execute the relevant commands.

        # First, check if an override_action is set and handle it.
        if config.override_action:
            # List all plugins.
            if config.override_action == 'list_plugins':
                if config.output_format == 'json':
                    print(controller.plugins.render_plugins_json())
                else:
                    print()
                    print(controller.plugins.render_plugins_table())

            # Exit after handling the override action.
            exit(0)

        # Now, process the given input file.

        # If input_format is not specified, try to infer it from the file
        # extension.
        input_format = config.input_format if config.input_format else \
            os.path.splitext(config.input_file)[1][len(os.extsep):]
        # Get the file extension (e.g., '.txt') splitExt[1] (arg0 is the filename
        # without the extension). Then, remove the leading extension separator
        # by slicing the string after len(os.extsep).

        # Identify the relevant AGReader for the file format.
        reader = controller.reader_for(input_format)
        controller.logger.info(
            f"Using reader \"{reader.name}\" ({reader.version}) for "
            f"input file \"{os.path.basename(config.input_file)}\" (kind: {input_format})."
        )
    except AGError as error:
        if controller is not None:
            controller.logger.error("A fatal error occurred, halting...")
            controller.logger.error(error)
        else:
            print(f"A fatal error occurred.\n\n{error}", file=sys.stderr)


if __name__ == '__main__':
    main()
