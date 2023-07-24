# DO NOT IMPORT THIS FILE DIRECTLY. IMPORT FROM app.abstract INSTEAD.

from abc import ABC, abstractmethod

from loguru import logger

from app.abstract import AbstractPluginRegistry


class AbstractController(ABC):
    """
    Abstract base type to represent a controller for the application.
    Useful for core modules that would otherwise have to import the
    controller module directly which could cause circular imports.
    """

    logger: logger
    """The application-wide logger."""

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the application"""
        pass

    @property
    @abstractmethod
    def config(self):
        """The application's current configuration"""
        pass

    @property
    @abstractmethod
    def standalone(self) -> bool:
        """Whether the application should run in standalone mode (e.g.,
        initializing its own logger, etc.,)"""
        pass

    @property
    @abstractmethod
    def plugins(self) -> AbstractPluginRegistry:
        """The application's plugin registry"""
        pass

    @property
    @abstractmethod
    def debug(self) -> bool:
        """
        Whether the application is running in debug mode.
        """
        pass
