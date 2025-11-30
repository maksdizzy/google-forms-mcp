"""Core module - shared authentication and base classes."""

from .auth import get_credentials, check_credentials, setup_wizard
from .base import BaseAPI
from .scopes import SCOPES, SCOPES_FORMS, SCOPES_SHEETS, SCOPES_DRIVE

__all__ = [
    "get_credentials",
    "check_credentials",
    "setup_wizard",
    "BaseAPI",
    "SCOPES",
    "SCOPES_FORMS",
    "SCOPES_SHEETS",
    "SCOPES_DRIVE",
]
