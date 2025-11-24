#!/usr/bin/env python3
"""OAuth authentication module for Google Forms CLI.

Handles OAuth 2.0 authentication with interactive setup wizard
and credential validation for non-technical users.
"""

import os
import sys
from pathlib import Path
from typing import Optional

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

# Load environment variables from .env file
load_dotenv()

console = Console()

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
        RefreshError: If token refresh fails
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
            f"Run 'uv run gforms auth setup' to configure credentials."
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


def check_credentials():
    """Check if OAuth credentials are valid and working."""
    console.print("\n[bold]Checking OAuth credentials...[/bold]\n")

    # Check .env file exists
    env_path = Path(".env")
    if not env_path.exists():
        console.print("[red]✗ .env file not found[/red]")
        console.print("  Run 'uv run gforms auth setup' to configure credentials.")
        return

    # Check required variables
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    refresh_token = os.getenv('GOOGLE_REFRESH_TOKEN')

    checks = [
        ("GOOGLE_CLIENT_ID", client_id),
        ("GOOGLE_CLIENT_SECRET", client_secret),
        ("GOOGLE_REFRESH_TOKEN", refresh_token),
    ]

    all_present = True
    for name, value in checks:
        if value:
            console.print(f"[green]✓[/green] {name} is set")
        else:
            console.print(f"[red]✗[/red] {name} is missing")
            all_present = False

    if not all_present:
        console.print("\n[yellow]Some credentials are missing.[/yellow]")
        console.print("Run 'uv run gforms auth setup' to configure.")
        return

    # Try to authenticate
    console.print("\n[bold]Testing authentication...[/bold]")
    try:
        creds = get_credentials()
        console.print("[green]✓ Authentication successful![/green]")
        console.print(f"  Token expires: {creds.expiry}")
    except RefreshError as e:
        console.print(f"[red]✗ Authentication failed: {e}[/red]")
        console.print("  Your refresh token may be invalid or expired.")
        console.print("  Run 'uv run gforms auth setup' to get new credentials.")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


def setup_wizard():
    """Interactive OAuth setup wizard for non-technical users."""
    console.print(Panel.fit(
        "[bold blue]Google Forms CLI - OAuth Setup Wizard[/bold blue]\n\n"
        "This wizard will help you configure Google OAuth credentials.\n"
        "You'll need to create credentials in Google Cloud Console first.",
        title="🔐 Authentication Setup"
    ))

    console.print("\n[bold]Before you begin:[/bold]")
    console.print("1. Go to [link=https://console.cloud.google.com]Google Cloud Console[/link]")
    console.print("2. Create a new project (or select existing)")
    console.print("3. Enable [bold]Google Forms API[/bold] and [bold]Google Drive API[/bold]")
    console.print("4. Go to [bold]APIs & Services → Credentials[/bold]")
    console.print("5. Create [bold]OAuth 2.0 Client ID[/bold] (Desktop application)")
    console.print()

    if not Confirm.ask("Do you have OAuth credentials ready?"):
        console.print("\n[yellow]Please create OAuth credentials first and run this wizard again.[/yellow]")
        console.print("\n[bold]Detailed instructions:[/bold]")
        console.print("https://developers.google.com/forms/api/quickstart/python#set_up_your_environment")
        return

    # Collect credentials
    console.print("\n[bold]Enter your OAuth credentials:[/bold]\n")

    client_id = Prompt.ask(
        "[cyan]Client ID[/cyan]",
        default=os.getenv('GOOGLE_CLIENT_ID', '')
    )

    client_secret = Prompt.ask(
        "[cyan]Client Secret[/cyan]",
        default=os.getenv('GOOGLE_CLIENT_SECRET', '')
    )

    # Check if we need to get refresh token
    refresh_token = os.getenv('GOOGLE_REFRESH_TOKEN', '')

    if refresh_token:
        use_existing = Confirm.ask(
            "Existing refresh token found. Use it?",
            default=True
        )
        if not use_existing:
            refresh_token = ''

    if not refresh_token:
        console.print("\n[bold]Getting Refresh Token:[/bold]")
        console.print("\nYou have two options:\n")
        console.print("[bold]Option 1: OAuth Playground (Recommended)[/bold]")
        console.print("1. Go to [link=https://developers.google.com/oauthplayground/]OAuth Playground[/link]")
        console.print("2. Click ⚙️ Settings → Check 'Use your own OAuth credentials'")
        console.print("3. Enter your Client ID and Client Secret")
        console.print("4. In 'Select & authorize APIs', add these scopes:")
        console.print("   - https://www.googleapis.com/auth/forms.body")
        console.print("   - https://www.googleapis.com/auth/forms.responses.readonly")
        console.print("   - https://www.googleapis.com/auth/drive.file")
        console.print("5. Click 'Authorize APIs' and sign in")
        console.print("6. Click 'Exchange authorization code for tokens'")
        console.print("7. Copy the [bold]refresh_token[/bold] value")

        console.print("\n[bold]Option 2: Run local OAuth flow[/bold]")

        method = Prompt.ask(
            "\nChoose method",
            choices=["playground", "local"],
            default="playground"
        )

        if method == "playground":
            refresh_token = Prompt.ask("\n[cyan]Refresh Token[/cyan]")
        else:
            refresh_token = _run_local_oauth_flow(client_id, client_secret)

    if not all([client_id, client_secret, refresh_token]):
        console.print("\n[red]Missing required credentials. Setup cancelled.[/red]")
        return

    # Save to .env file
    console.print("\n[bold]Saving credentials to .env file...[/bold]")

    env_content = f"""# Google Forms CLI OAuth Credentials
# Generated by: uv run gforms auth setup

GOOGLE_CLIENT_ID={client_id}
GOOGLE_CLIENT_SECRET={client_secret}
GOOGLE_REFRESH_TOKEN={refresh_token}
"""

    env_path = Path(".env")

    if env_path.exists():
        if not Confirm.ask(".env file exists. Overwrite?", default=False):
            console.print("[yellow]Cancelled. Credentials not saved.[/yellow]")
            return

    env_path.write_text(env_content)
    console.print("[green]✓ Credentials saved to .env[/green]")

    # Make sure .env is in .gitignore
    gitignore_path = Path(".gitignore")
    if gitignore_path.exists():
        gitignore_content = gitignore_path.read_text()
        if ".env" not in gitignore_content:
            with open(gitignore_path, "a") as f:
                f.write("\n# OAuth credentials\n.env\n")
            console.print("[green]✓ Added .env to .gitignore[/green]")
    else:
        gitignore_path.write_text("# OAuth credentials\n.env\n")
        console.print("[green]✓ Created .gitignore with .env[/green]")

    # Test credentials
    console.print("\n[bold]Testing credentials...[/bold]")

    # Reload environment
    load_dotenv(override=True)

    try:
        creds = get_credentials()
        console.print("[green]✓ Authentication successful![/green]")

        console.print(Panel.fit(
            "[bold green]Setup Complete![/bold green]\n\n"
            "You can now use the Google Forms CLI:\n\n"
            "  [cyan]uv run gforms list[/cyan]          - List your forms\n"
            "  [cyan]uv run gforms create \"Title\"[/cyan] - Create a new form\n"
            "  [cyan]uv run gforms --help[/cyan]        - See all commands",
            title="✅ Success"
        ))

    except Exception as e:
        console.print(f"[red]✗ Authentication failed: {e}[/red]")
        console.print("\nPlease check your credentials and try again.")


def _run_local_oauth_flow(client_id: str, client_secret: str) -> Optional[str]:
    """Run local OAuth flow to get refresh token."""
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        console.print("[red]google-auth-oauthlib not installed.[/red]")
        console.print("Install it with: uv add google-auth-oauthlib")
        return None

    console.print("\n[bold]Starting local OAuth flow...[/bold]")
    console.print("A browser window will open for authorization.")

    # Create client config
    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uris": ["http://localhost:8080"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    }

    try:
        flow = InstalledAppFlow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri='http://localhost:8080'
        )

        creds = flow.run_local_server(port=8080, open_browser=True)
        console.print("[green]✓ Authorization successful![/green]")

        return creds.refresh_token

    except Exception as e:
        console.print(f"[red]OAuth flow failed: {e}[/red]")
        return None
