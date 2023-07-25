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
