"""
Simple stub to provide type hints for the logger.
"""

from typing import TypeVar

# noinspection PyProtectedMember
from loguru._logger import Logger

LoggerType = TypeVar('LoggerType', bound=Logger)
"""
The application logger.

agtool's logger is loguru. The instance passed around the application (via the controller) has application-specific
metadata bound to it (e.g., the application name, formatting, etc.,).
"""
