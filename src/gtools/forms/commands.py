"""Google Forms CLI commands."""

import typer
from typing import Optional
from rich.console import Console
from rich.table import Table

console = Console()


def _process_text(text: str) -> str:
    """Convert escaped newlines to actual newlines for CLI input.

    Allows users to pass 'Line1\\nLine2' and have it converted to actual newlines.
    """
    if text:
        return text.replace('\\n', '\n')
    return text

# Forms command group
forms_app = typer.Typer(
    name="forms",
    help="Google Forms operations - create, manage, and export forms",
    rich_markup_mode="rich",
)


@forms_app.command("list")
def forms_list(
    page_size: int = typer.Option(50, "--page-size", "-n", help="Number of forms to list"),
):
    """
    List all your Google Forms.

    Shows form ID, title, response count, and links.
    """
    from .api import FormsAPI

    try:
        api = FormsAPI()
        result = api.list_forms(page_size=page_size)

        if not result.get("forms"):
            console.print("[yellow]No forms found.[/yellow]")
            return

        table = Table(title="Your Google Forms")
        table.add_column("Form ID", style="cyan", no_wrap=True)
        table.add_column("Title", style="green")
        table.add_column("Responses", justify="right", style="magenta")

        for form in result["forms"]:
            table.add_row(
                form["formId"][:20] + "...",
                form["title"][:40],
                str(form.get("responseCount", 0))
            )

        console.print(table)

        if result.get("nextPageToken"):
            console.print(f"\n[dim]More forms available. Use --page-size to see more.[/dim]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@forms_app.command("create")
def forms_create(
    title: str = typer.Argument(..., help="Form title"),
    description: str = typer.Option("", "--description", "-d", help="Form description"),
):
    """
    Create a new Google Form.

    Returns the form ID and sharing link.
    """
    from .api import FormsAPI

    try:
        api = FormsAPI()
        result = api.create_form(title=title, description=description)

        console.print("\n[green]✓ Form created successfully![/green]\n")
        console.print(f"[bold]Form ID:[/bold] {result['formId']}")
        console.print(f"[bold]Share link:[/bold] {result['responderUri']}")
        console.print(f"[bold]Edit link:[/bold] {result['editUri']}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@forms_app.command("get")
def forms_get(
    form_id: str = typer.Argument(..., help="Form ID"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """
    Get details of a specific form.

    Shows form structure, questions, and settings.
    """
    from .api import FormsAPI
    import json

    try:
        api = FormsAPI()
        result = api.get_form(form_id)

        if json_output:
            console.print_json(json.dumps(result, indent=2))
        else:
            info = result.get("info", {})
            console.print(f"\n[bold]Title:[/bold] {info.get('title', 'N/A')}")
            console.print(f"[bold]Description:[/bold] {info.get('description', 'N/A')}")
            console.print(f"[bold]Form ID:[/bold] {result.get('formId', 'N/A')}")
            console.print(f"[bold]Share link:[/bold] {result.get('responderUri', 'N/A')}")

            items = result.get("items", [])
            if items:
                console.print(f"\n[bold]Questions ({len(items)}):[/bold]")
                for i, item in enumerate(items, 1):
                    title = item.get("title", "Untitled")
                    item_type = "Question"
                    if "pageBreakItem" in item:
                        item_type = "Section"
                    elif "textItem" in item:
                        item_type = "Text"
                    console.print(f"  {i}. [{item_type}] {title}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@forms_app.command("update")
def forms_update(
    form_id: str = typer.Argument(..., help="Form ID"),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="New title"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="New description (supports \\n for newlines)"),
):
    """
    Update form title and/or description.

    Use \\n in --description for line breaks.
    """
    from .api import FormsAPI

    if not title and not description:
        console.print("[yellow]Please provide --title or --description to update[/yellow]")
        raise typer.Exit(1)

    try:
        api = FormsAPI()
        # Process description for newlines
        processed_desc = _process_text(description) if description else description
        api.update_form(form_id, title=title, description=processed_desc)

        console.print("[green]✓ Form updated successfully![/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@forms_app.command("delete")
def forms_delete(
    form_id: str = typer.Argument(..., help="Form ID"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """
    Delete a form.

    This action cannot be undone.
    """
    from .api import FormsAPI

    if not confirm:
        confirm = typer.confirm(f"Are you sure you want to delete form {form_id}?")
        if not confirm:
            console.print("[yellow]Cancelled.[/yellow]")
            raise typer.Exit(0)

    try:
        api = FormsAPI()
        api.delete_form(form_id)

        console.print("[green]✓ Form deleted successfully![/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@forms_app.command("duplicate")
def forms_duplicate(
    form_id: str = typer.Argument(..., help="Form ID to duplicate"),
    new_title: str = typer.Option(..., "--title", "-t", help="Title for the new form"),
    personalize: Optional[str] = typer.Option(None, "--personalize", "-p", help="Replace NAME placeholder with this value"),
):
    """
    Duplicate an existing form.

    Creates a copy with all questions and settings.
    Use --personalize to replace NAME placeholders with a specific name.

    Example:
        gtools forms duplicate FORM_ID -t "360 Feedback - John" -p "John"
    """
    from .api import FormsAPI

    try:
        api = FormsAPI()
        result = api.duplicate_form(form_id, new_title)

        console.print("\n[green]✓ Form duplicated successfully![/green]\n")
        console.print(f"[bold]New Form ID:[/bold] {result['newFormId']}")
        console.print(f"[bold]Share link:[/bold] {result['responderUri']}")
        console.print(f"[bold]Items copied:[/bold] {result['copiedItems']}")
        console.print(f"[bold]Execution time:[/bold] {result['executionTime']}")

        # Personalize if requested
        if personalize:
            console.print(f"\n[cyan]Personalizing form with '{personalize}'...[/cyan]")
            # Replace NAME and Employee Name placeholders
            replacements = {
                "NAME": personalize,
                "Employee Name": personalize,
            }
            pers_result = api.personalize_form(result['newFormId'], replacements)
            console.print(f"[green]✓ Personalized {pers_result['itemsUpdated']} items[/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@forms_app.command("link")
def forms_link(
    form_id: str = typer.Argument(..., help="Form ID"),
):
    """
    Get shareable links for a form.
    """
    from .api import FormsAPI

    try:
        api = FormsAPI()
        form = api.get_form(form_id)

        console.print(f"\n[bold]Form:[/bold] {form.get('info', {}).get('title', 'N/A')}")
        console.print(f"[bold]Share link:[/bold] {form.get('responderUri', 'N/A')}")
        console.print(f"[bold]Edit link:[/bold] https://docs.google.com/forms/d/{form_id}/edit")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


# Question commands
@forms_app.command("add-question")
def add_question(
    form_id: str = typer.Argument(..., help="Form ID"),
    question_type: str = typer.Option(..., "--type", "-t", help="Question type (SHORT_ANSWER, PARAGRAPH, MULTIPLE_CHOICE, CHECKBOXES, DROPDOWN, LINEAR_SCALE, DATE, TIME, RATING)"),
    title: str = typer.Option(..., "--title", help="Question text"),
    description: str = typer.Option("", "--description", "-d", help="Question description/helper text (supports \\n for newlines)"),
    options: Optional[str] = typer.Option(None, "--options", "-o", help="Comma-separated options for choice questions"),
    required: bool = typer.Option(False, "--required", "-r", help="Make question required"),
    position: int = typer.Option(0, "--position", "-p", help="Position index"),
    low: int = typer.Option(1, "--low", help="Low value for scale questions"),
    high: int = typer.Option(5, "--high", help="High value for scale questions"),
    low_label: str = typer.Option("", "--low-label", help="Label for low value"),
    high_label: str = typer.Option("", "--high-label", help="Label for high value"),
):
    """
    Add a question to a form.

    Supported types: SHORT_ANSWER, PARAGRAPH, MULTIPLE_CHOICE, CHECKBOXES,
    DROPDOWN, LINEAR_SCALE, DATE, TIME, RATING

    Use \\n in --description for line breaks.
    """
    from .api import FormsAPI

    try:
        api = FormsAPI()

        kwargs = {
            "required": required,
            "position": position,
        }

        if options:
            kwargs["options"] = [o.strip() for o in options.split(",")]

        if question_type in ["LINEAR_SCALE", "RATING"]:
            kwargs["low"] = low
            kwargs["high"] = high
            kwargs["lowLabel"] = low_label
            kwargs["highLabel"] = high_label

        # Process description for newlines
        processed_desc = _process_text(description)

        api.add_question(form_id, question_type, title, description=processed_desc, **kwargs)

        console.print("[green]✓ Question added successfully![/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@forms_app.command("delete-question")
def delete_question(
    form_id: str = typer.Argument(..., help="Form ID"),
    item_id: str = typer.Argument(..., help="Item ID to delete"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """
    Delete a question from a form.
    """
    from .api import FormsAPI

    if not confirm:
        confirm = typer.confirm(f"Delete question {item_id}?")
        if not confirm:
            console.print("[yellow]Cancelled.[/yellow]")
            raise typer.Exit(0)

    try:
        api = FormsAPI()
        api.delete_question(form_id, item_id)

        console.print("[green]✓ Question deleted successfully![/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@forms_app.command("move-question")
def move_question(
    form_id: str = typer.Argument(..., help="Form ID"),
    item_id: str = typer.Argument(..., help="Item ID to move"),
    position: int = typer.Option(..., "--position", "-p", help="New position index"),
):
    """
    Move a question to a new position.
    """
    from .api import FormsAPI

    try:
        api = FormsAPI()
        api.move_question(form_id, item_id, position)

        console.print("[green]✓ Question moved successfully![/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@forms_app.command("add-section")
def add_section(
    form_id: str = typer.Argument(..., help="Form ID"),
    title: str = typer.Option(..., "--title", "-t", help="Section title"),
    description: str = typer.Option("", "--description", "-d", help="Section description (supports \\n for newlines)"),
    position: Optional[int] = typer.Option(None, "--position", "-p", help="Position index"),
):
    """
    Add a section break to a form.

    Use \\n in --description for line breaks.
    """
    from .api import FormsAPI

    try:
        api = FormsAPI()
        # Process description for newlines
        processed_desc = _process_text(description)
        api.add_section(form_id, title, processed_desc, position)

        console.print("[green]✓ Section added successfully![/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


# Response commands
@forms_app.command("responses")
def list_responses(
    form_id: str = typer.Argument(..., help="Form ID"),
    page_size: int = typer.Option(100, "--page-size", "-n", help="Number of responses"),
):
    """
    List responses for a form.
    """
    from .api import FormsAPI

    try:
        api = FormsAPI()
        result = api.list_responses(form_id, page_size=page_size)

        responses = result.get("responses", [])
        if not responses:
            console.print("[yellow]No responses yet.[/yellow]")
            return

        table = Table(title=f"Responses ({len(responses)})")
        table.add_column("Response ID", style="cyan", no_wrap=True)
        table.add_column("Submitted", style="green")
        table.add_column("Email", style="magenta")

        for resp in responses:
            table.add_row(
                resp.get("responseId", "N/A")[:20] + "...",
                resp.get("createTime", "N/A")[:19],
                resp.get("respondentEmail", "Anonymous")
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@forms_app.command("export")
def export_responses(
    form_id: str = typer.Argument(..., help="Form ID"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    format: str = typer.Option("csv", "--format", "-f", help="Output format (csv)"),
):
    """
    Export responses to CSV file.
    """
    from .api import FormsAPI

    try:
        api = FormsAPI()
        result = api.export_responses_csv(form_id)

        csv_content = result.get("csv", "")
        row_count = result.get("rowCount", 0)

        if not csv_content:
            console.print("[yellow]No responses to export.[/yellow]")
            return

        if output:
            with open(output, "w", encoding="utf-8") as f:
                f.write(csv_content)
            console.print(f"[green]✓ Exported {row_count} responses to {output}[/green]")
        else:
            console.print(csv_content)
            console.print(f"\n[dim]Total: {row_count} responses[/dim]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


# Template commands
@forms_app.command("apply")
def apply_template(
    template_path: str = typer.Argument(..., help="Path to YAML template file"),
):
    """
    Create a form from a YAML template.

    See templates/examples/ for template format.
    """
    from ..templates import create_from_template

    try:
        result = create_from_template(template_path)

        console.print("\n[green]✓ Form created from template![/green]\n")
        console.print(f"[bold]Form ID:[/bold] {result['formId']}")
        console.print(f"[bold]Share link:[/bold] {result['responderUri']}")
        console.print(f"[bold]Questions added:[/bold] {result['questionsAdded']}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@forms_app.command("export-template")
def export_template(
    form_id: str = typer.Argument(..., help="Form ID to export"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
):
    """
    Export a form to YAML template format.
    """
    from ..templates import export_to_template

    try:
        yaml_content = export_to_template(form_id)

        if output:
            with open(output, "w", encoding="utf-8") as f:
                f.write(yaml_content)
            console.print(f"[green]✓ Template exported to {output}[/green]")
        else:
            console.print(yaml_content)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
