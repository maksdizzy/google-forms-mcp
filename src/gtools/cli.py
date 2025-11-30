#!/usr/bin/env python3
"""Google Tools CLI - Main entry point for command-line interface.

Usage:
    gtools [COMMAND] [OPTIONS]

Command Groups:
    auth        Authentication management (setup, check)
    forms       Google Forms operations (create, manage, export)
    sheets      Google Sheets operations (read, export)

Examples:
    gtools auth setup
    gtools forms list
    gtools forms create "My Form"
    gtools sheets read SPREADSHEET_ID
"""

import typer
from rich.console import Console

from . import __version__, __app_name__

# Initialize Typer app
app = typer.Typer(
    name=__app_name__,
    help="Google Tools CLI - Manage Google Forms and Sheets from the command line",
    add_completion=False,
    rich_markup_mode="rich",
)

# Rich console for pretty output
console = Console()


def version_callback(value: bool):
    """Show version and exit."""
    if value:
        console.print(f"[bold blue]{__app_name__}[/bold blue] version [green]{__version__}[/green]")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True,
    ),
):
    """
    [bold blue]Google Tools CLI[/bold blue] - Manage Google Forms and Sheets from the command line.

    Use [bold]gtools --help[/bold] for available commands.
    """
    pass


# =============================================================================
# AUTH Commands
# =============================================================================

auth_app = typer.Typer(help="Authentication management")
app.add_typer(auth_app, name="auth")


@auth_app.command("setup")
def auth_setup():
    """
    Interactive OAuth setup wizard.

    Guides you through the process of obtaining Google OAuth credentials.
    """
    from .core.auth import setup_wizard
    setup_wizard()


@auth_app.command("check")
def auth_check():
    """
    Check if OAuth credentials are valid.

    Verifies that credentials in .env file work correctly.
    """
    from .core.auth import check_credentials
    check_credentials()


# =============================================================================
# Add Forms and Sheets command groups
# =============================================================================

from .forms.commands import forms_app
from .sheets.commands import sheets_app

app.add_typer(forms_app, name="forms")
app.add_typer(sheets_app, name="sheets")


# =============================================================================
# Entry Point
# =============================================================================

def run():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    run()
