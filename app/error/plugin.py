# Purpose: Plugin-related errors.
from typing import Optional

from app.error import AGError


class AGPluginError(AGError):
    """Wrapper exception for all problems encountered by a plugin."""

    def __init__(self,
                 plugin_id: Optional[str],
                 message: str = None,
                 description: str = None):
        self.plugin_id = plugin_id
        """The ID of the plugin that threw the error."""

        default_message: str = (f"""Plugin {plugin_id} encountered an error."""
                                if plugin_id is not None else
                                f"""A plugin error has occurred.""")

        super().__init__(message=default_message if message is None else message,
                         description=description)


class AGPluginConflictError(AGPluginError):
    """
    Thrown when there is a conflict between two plugins. (e.g., because of
    duplicate IDs).
    """

    def __init__(self,
                 plugin_id: str,
                 description: str = None):

        super().__init__(plugin_id=plugin_id,
                         message=f"There is a conflict between {plugin_id} and another plugin.",
                         description=description)


class AGMissingPluginError(AGPluginError):
    """
    Thrown when a plugin that is required for certain functionality cannot be
    found.
    """

    def __init__(self, description: str = None):
        # The full description is the default description plus the optional
        # extended description (if there is one).
        full_description = ("The requested functionality requires a plugin, "
                            "but a suitable plugin could not be found." +
                            (f"\n\n{description}"
                                if description is not None
                                else ""))

        super().__init__(plugin_id=None,
                         message="A required plugin could not be found.",
                         description=full_description)
