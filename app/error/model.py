# Purpose: Model or processing-related errors.

# TODO: refactor model.py errors to AGError (i.e., runtime and library errors)
#   instead of AGToolError (i.e., runtime errors only).
#   For now, they are AGToolError because it includes app-specific behaviors
#   like logging the error automatically and including the controller that
#   threw the error.

from app.error import AGToolError


class InvalidModelData(AGToolError):
    """Wrapper exception for all problems encountered when parsing a model representation."""

    def __init__(self, description: str = None, input_source: str = None, **kwargs):
        self.input_source = input_source
        """The label for the source of the model."""

        super().__init__(message=f"""Invalid model found{': ' + self.input_source if input_source is not None else ''}.
There was a problem with parsing the requested model.""",
                         description=description,
                         **kwargs)
