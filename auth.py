#!/usr/bin/env python3
"""OAuth authentication module for Google Forms MCP Server.

Handles OAuth 2.0 authentication using credentials from .env file.
Supports automatic token refresh for long-running sessions.
"""

import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Required OAuth scopes for Google Forms and Drive APIs
SCOPES = [
    'https://www.googleapis.com/auth/forms.body',
    'https://www.googleapis.com/auth/forms.responses.readonly',
    'https://www.googleapis.com/auth/drive.file'
]


def get_credentials() -> Credentials:
    """Get and refresh OAuth credentials from environment variables.

    Returns:
        Credentials: Refreshed Google OAuth credentials

    Raises:
        ValueError: If any required credentials are missing from .env
        google.auth.exceptions.RefreshError: If token refresh fails
    """
    # Load credentials from environment
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    refresh_token = os.getenv('GOOGLE_REFRESH_TOKEN')

    # Validate all required credentials are present
    if not all([client_id, client_secret, refresh_token]):
        missing = []
        if not client_id:
            missing.append('GOOGLE_CLIENT_ID')
        if not client_secret:
            missing.append('GOOGLE_CLIENT_SECRET')
        if not refresh_token:
            missing.append('GOOGLE_REFRESH_TOKEN')

        raise ValueError(
            f"Missing OAuth credentials in .env file: {', '.join(missing)}\n"
            f"Please add all required credentials to .env file.\n"
            f"See README.md for setup instructions."
        )

    # Create credentials object with refresh token
    creds = Credentials(
        token=None,  # Will be populated after refresh
        refresh_token=refresh_token,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=client_id,
        client_secret=client_secret,
        scopes=SCOPES
    )

    # Refresh the access token
    creds.refresh(Request())

    return creds
