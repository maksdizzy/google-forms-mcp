#!/usr/bin/env python3
"""One-time OAuth token generator for Google Forms MCP Server.

Run this script once to generate a refresh token for your .env file.
Requires client_secrets.json with OAuth client credentials.
"""

import os
import sys
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://www.googleapis.com/auth/forms.body',
    'https://www.googleapis.com/auth/forms.responses.readonly',
    'https://www.googleapis.com/auth/drive.file'
]


def get_refresh_token():
    """Run OAuth flow and display credentials for .env file."""

    # Check for client_secrets.json
    if not os.path.exists('client_secrets.json'):
        print("\n❌ ERROR: client_secrets.json not found")
        print("\nPlease create client_secrets.json with your OAuth credentials:")
        print("""
{
  "installed": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uris": ["http://localhost:8080"],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token"
  }
}
        """)
        sys.exit(1)

    print("\n" + "="*60)
    print("Google Forms MCP - OAuth Token Generator")
    print("="*60)
    print("\n📋 This will:")
    print("1. Open your browser for Google account authorization")
    print("2. Generate OAuth credentials for the MCP server")
    print("3. Display credentials to add to your .env file")
    print("\n⚠️  Keep these credentials secure - they provide full access to your forms")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    input()

    try:
        # Run OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secrets.json',
            scopes=SCOPES,
            redirect_uri='http://localhost:8080'
        )

        print("\n🌐 Opening browser for authorization...")
        creds = flow.run_local_server(port=8080, open_browser=True)

        # Display credentials
        print("\n" + "="*60)
        print("✅ SUCCESS - Copy these credentials to your .env file:")
        print("="*60)
        print(f"\nGOOGLE_CLIENT_ID={creds.client_id}")
        print(f"GOOGLE_CLIENT_SECRET={creds.client_secret}")
        print(f"GOOGLE_REFRESH_TOKEN={creds.refresh_token}")
        print("\n" + "="*60)
        print("\n📝 Next steps:")
        print("1. Create .env file in the project root")
        print("2. Copy the three lines above into .env")
        print("3. Run: python main.py")
        print("\n✅ You're ready to use the MCP server!")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nTroubleshooting:")
        print("- Verify client_secrets.json has correct OAuth credentials")
        print("- Check that Google Forms API is enabled in Cloud Console")
        print("- Ensure redirect URI is http://localhost:8080")
        sys.exit(1)


if __name__ == "__main__":
    get_refresh_token()
