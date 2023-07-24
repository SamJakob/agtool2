"""
The error module contains all domain-specific exceptions that can be thrown by
agtool.

All runtime exceptions inherit from AGToolError, which is a subclass of
Exception. This allows for all exceptions thrown by agtool to be caught in a
single except block and handled together, if desired.

For now, it is expected that all exceptions thrown by agtool will be
superclasses of AGToolError, but this may change in the future if AGTool is
adapted to be used as a library, in which case errors pertaining to both the
library and tool would be superclasses of AGError instead.
"""

from app.abstract import AbstractController


class AGError(Exception):
    """Superclass for all exceptions thrown by agtool."""

    def __init__(self,
                 message: str,
                 description: str = None):
        self.message = message
        """A human-readable description of why the error occurred."""

        self.description = description
        """An optional extended explanation of what caused the error."""

    def __str__(self):
        final_message = (self.message if self.message is not None else "An unexpected error occurred.")
        final_description = f'\n\n{self.description}' if self.description is not None else ""
        return f'({self.__class__.__name__}) {final_message}{final_description}'


class AGToolError(AGError):
    """Superclass for all exceptions thrown within agtool at runtime."""

    def __init__(self,
                 message: str,
                 controller: AbstractController,
                 description: str = None,
                 skip_auto_log: bool = False):
        self.message = message
        """A human-readable description of why the error occurred."""

        self.description = description
        """An optional extended explanation of what caused the error."""

        self.controller = controller
        """The controller that was running when the error was thrown."""

        self.skip_auto_log = skip_auto_log
        """Whether the error should be automatically logged."""

        super().__init__(message=message,
                         description=description)


from .plugin import *
from .model import *
