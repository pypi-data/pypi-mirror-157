"""
Exception types for Deirokay processes.
"""

from .enums import SeverityLevel


class ValidationError(Exception):
    """Validation failure exception."""

    def __init__(self, level: SeverityLevel, message='Validation failed'):
        self.level = level
        super().__init__(message)
