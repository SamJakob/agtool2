import os
import sys
from typing import Optional

from agtool.core import Controller
from agtool.error import AGError
from agtool.helpers.cli import get_app_info, parse_cli_args
from agtool.helpers.file import read_file_as_string, replace_file_extension, write_file_from_data, \
    write_stdout_from_data


# Welcome to the main executable file for this project. This launches the CLI
# application in agtool's "default form factor" (as opposed to being a web or
# desktop application, or part of another application.)

# Package information is retained in agtool/__init__.py (relatively to project
# root). For more information, please refer to README.md at the root of the
# repository.


def main(argv=None):
    controller: Optional[Controller] = None

    try:
        # Process the specified arguments by including the system arguments, or
        # just fall back to retrieving the system arguments.
        argv = [*sys.argv[1:], *argv] if argv is not None else sys.argv[1:]
        config = parse_cli_args(argv, default_settings={
            'theme': 'simple',
        })

        # Read information about the CLI application.
        app_info = get_app_info()

        # Start the controller for dependency injection.
        controller = Controller(
            app_info=app_info,
            config=config,
            standalone=True,
            base_path=os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
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

        # Check if the input file exists.
        if not os.path.exists(config.input_file):
            raise AGError(f"Input file \"{config.input_file}\" does not exist.")

        # Now, process the given input file.

        # If input_format is not specified, try to infer it from the file
        # extension.
        config.input_format = config.input_format if config.input_format else \
            os.path.splitext(config.input_file)[1][len(os.extsep):]
        # Get the file extension (e.g., '.txt') splitExt[1] (arg0 is the filename
        # without the extension). Then, remove the leading extension separator
        # by slicing the string after len(os.extsep).

        # Identify the relevant AGReader for the file format.
        reader = controller.reader_for(config.input_format)
        controller.logger.info(
            f"Using reader \"{reader.name}\" ({reader.version}) for "
            f"input file \"{os.path.basename(config.input_file)}\" (kind: {config.input_format})."
        )

        # Read the graph from the input file.
        graph = reader.read_graph(config.input_file, read_file_as_string(
            config.input_file,
            working_dir=controller.base_path
        ))

        # Identify the output file extension (if one was specified).
        output_file_ext = os.path.splitext(config.output_file)[1][len(os.extsep):] \
            if config.output_file else ""

        # Normalize the output file and format.
        if config.output_format and config.output_file:
            # If the output_file is specified (i.e., not empty) but does not have
            # a file extension, then we'll append the output_format to the
            # output_file (provided it is not a URI).
            if len(output_file_ext) == 0 and ('://' not in config.output_file):
                config.output_file = replace_file_extension(config.output_file, config.output_format)

            # If we have both the output_format and the output_file, then we'll
            # use the output_file as-is, but provide a warning to the user if the
            # output_format doesn't match the file extension.
            if config.output_format != output_file_ext:
                controller.logger.warning(
                    f"Output file \"{config.output_file}\" does not match the "
                    f"output format \"{config.output_format}\"."
                )

                controller.logger.warning(
                    f"We'll use the output file name as-is ({config.output_file}) and produce a file"
                    f"with the specified format ({config.output_format}), but this may be unexpected."
                )
        elif config.output_format and not config.output_file:
            # If the output_format is specified, but the output_file is not, then
            # we'll just use the input_file with the output_format as the
            # output_file extension.
            config.output_file = replace_file_extension(config.input_file, config.output_format)
        elif not config.output_format:
            # If output_format is not specified, try to infer it from the file
            # extension.
            config.output_format = config.output_format if config.output_format else output_file_ext

            # If there is no output_format, we'll throw an error.
            if len(config.output_format) == 0:
                raise AGError("No output format specified (and the output filename does not have an extension).")
        else:
            # If we get here, then we have neither the output_format nor the
            # output_file, so we'll throw an error. (This shouldn't happen because
            # a valid output format should be specified by the CLI parser.)
            # But, if the user is using the API, or the parser is changed, this
            # could happen, so we'll handle it.
            raise AGError("No output format specified (and no output filename was specified so none could be"
                          "inferred).")

        # Identify the relevant AGWriter for the file format.
        writer = controller.writer_for(config.output_format)
        controller.logger.info(
            f"Using writer \"{writer.name}\" ({writer.version}) for "
            f"output file \"{os.path.basename(config.output_file)}\" (kind: {config.output_format})."
        )

        # Produce the output data.
        output_data = writer.write_graph(graph, destination_label=config.output_file)

        # Attempt to write the output data to the output file.
        try:
            if config.output_file.startswith("stdout://"):
                # If the output file is stdout://, then we'll write to standard
                # output.
                write_stdout_from_data(output_data)
            else:
                # Otherwise, we'll write to a file.
                write_file_from_data(config.output_file, output_data, working_dir=controller.base_path)
                controller.logger.success(f"Successfully wrote to output file: "
                                          f"{config.output_file} (kind: {config.output_format})")
        except PermissionError:
            controller.logger.error("There was a permission error when writing to the output file.")
            controller.logger.error("If this is unexpected, is the file in use?")
            raise AGError(f"Permission denied when writing to output file: {config.output_file}")

    except AGError as error:
        if controller is not None:
            controller.logger.error("A fatal error occurred, halting...")
            controller.logger.error(error)
        else:
            print(f"A fatal error occurred.\n\n{error}", file=sys.stderr)


if __name__ == '__main__':
    main()
