"""Base API class for all Google service clients.

Provides common functionality for authentication and service initialization.
"""

from abc import ABC
from typing import Optional
import logging

from googleapiclient.discovery import build, Resource

from .auth import get_credentials

logger = logging.getLogger("gtools")


class BaseAPI(ABC):
    """Abstract base class for Google API clients.

    Provides lazy-loading of API services and shared credentials.

    Subclasses should define:
        API_NAME: str - The Google API name (e.g., 'forms', 'sheets')
        API_VERSION: str - The API version (e.g., 'v1', 'v4')

    Example:
        class FormsAPI(BaseAPI):
            API_NAME = "forms"
            API_VERSION = "v1"
    """

    API_NAME: str = ""
    API_VERSION: str = ""

    def __init__(self):
        """Initialize API client with OAuth credentials."""
        self.creds = get_credentials()
        self._service: Optional[Resource] = None
        self._drive_service: Optional[Resource] = None

    @property
    def service(self) -> Resource:
        """Lazy-load the primary API service.

        Returns:
            Google API Resource for the specific service.
        """
        if self._service is None:
            if not self.API_NAME or not self.API_VERSION:
                raise NotImplementedError(
                    "Subclass must define API_NAME and API_VERSION"
                )
            self._service = build(
                self.API_NAME,
                self.API_VERSION,
                credentials=self.creds
            )
        return self._service

    @property
    def drive_service(self) -> Resource:
        """Lazy-load Google Drive service.

        Many Google APIs need Drive access for file operations.

        Returns:
            Google Drive API Resource (v3).
        """
        if self._drive_service is None:
            self._drive_service = build('drive', 'v3', credentials=self.creds)
        return self._drive_service
