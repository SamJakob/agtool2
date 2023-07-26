# DO NOT IMPORT THIS FILE DIRECTLY. IMPORT FROM agtool.abstract INSTEAD.

from abc import ABC, abstractmethod

from agtool.abstract import AbstractPluginRegistry
from agtool.config import AppConfig
from agtool.helpers.logger import LoggerType


class AbstractController(ABC):
    """
    Abstract base type to represent a controller for the application.
    Useful for core modules that would otherwise have to import the
    controller module directly which could cause circular imports.
    """

    logger: LoggerType
    """The application-wide logger."""

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the application"""

    @property
    @abstractmethod
    def version(self) -> str:
        """The version of the application"""

    @property
    @abstractmethod
    def description(self) -> list[str]:
        """The description of the application"""

    @property
    @abstractmethod
    def timestamp(self) -> str:
        """
        The localized timestamp of the application's execution (this may be updated to be current time
        automatically). This is useful for logging or otherwise printing a timestamp that is consistent
        across the application.
        """

    @property
    @abstractmethod
    def config(self) -> AppConfig:
        """The application's current configuration"""

    @property
    def settings(self) -> dict[str, str]:
        """A convenience property to access the application's settings"""
        return self.config.settings

    @property
    @abstractmethod
    def standalone(self) -> bool:
        """Whether the application should run in standalone mode (e.g.,
        initializing its own logger, etc.,)"""

    @property
    @abstractmethod
    def plugins(self) -> AbstractPluginRegistry:
        """The application's plugin registry"""

    @property
    @abstractmethod
    def debug(self) -> bool:
        """
        Whether the application is running in debug mode.
        """

    @property
    @abstractmethod
    def has_booted(self) -> bool:
        """
        Whether the application has booted.

        This will also return true if the application is booting. It is intended to
        denote whether `boot` needs to be called. If `boot` is called when the
        application has already booted (per this property), it will be a no-op.
        """

    @abstractmethod
    def boot(self):
        """
        Boot the application (loads plugins, etc.,).

        This is done in a separate method so that the controller can be initialized
        first to initialize a logger, get configuration, etc., before booting the
        remaining application components.

        If boot is not called early enough, the controller may decide to invoke this
        method automatically.
        """

    @abstractmethod
    def shutdown(self, ordinary: bool = False, exit_code: int = 0):
        """
        Terminates the application. This should be called when the application is
        finished running, or when the application is to be terminated early.

        This MAY be used by the application core to shut down the application
        cleanly on a normal exit from the main loop, but ths is not necessarily the
        case.

        Plugins, etc., SHOULD use this method to terminate the application
        cleanly. They may signal a non-zero `exit_code` to indicate a failure or
        error. Plugins SHOULD ALWAYS leave `ordinary` as `False`.

        Usage of this method is preferred over `sys.exit()` as it allows the
        application to perform cleanup and logging before exiting (e.g., if a web
        server is running, it can be shut down gracefully).

        If the application hasn't yet booted, this will be a no-op.

        :param ordinary: Whether the application is shutting down ordinarily.
        This should be false outside of the application's main loop regardless of
        whether an error has occurred and may be ignored by the controller.
        :param exit_code: The exit code to exit with.
        """
