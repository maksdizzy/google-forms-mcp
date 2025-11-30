"""Google Sheets CLI commands."""

import typer
from typing import Optional
from rich.console import Console
from rich.table import Table

console = Console()

# Sheets command group
sheets_app = typer.Typer(
    name="sheets",
    help="Google Sheets operations - read and export spreadsheet data",
    rich_markup_mode="rich",
)


@sheets_app.command("info")
def sheets_info(
    spreadsheet_id: str = typer.Argument(..., help="Spreadsheet ID or URL"),
):
    """
    Get spreadsheet metadata.

    Shows spreadsheet title, locale, timezone, and list of sheets.
    """
    from .api import SheetsAPI

    try:
        api = SheetsAPI()
        info = api.get_spreadsheet(spreadsheet_id)

        console.print(f"\n[bold blue]Spreadsheet Info[/bold blue]")
        console.print(f"[dim]ID:[/dim] {info['spreadsheetId']}")
        console.print(f"[dim]Title:[/dim] [green]{info['title']}[/green]")
        if info.get('locale'):
            console.print(f"[dim]Locale:[/dim] {info['locale']}")
        if info.get('timeZone'):
            console.print(f"[dim]Timezone:[/dim] {info['timeZone']}")

        console.print(f"\n[bold]Sheets ({len(info['sheets'])}):[/bold]")
        table = Table()
        table.add_column("Index", style="dim", justify="right")
        table.add_column("Title", style="cyan")
        table.add_column("Rows", justify="right", style="green")
        table.add_column("Columns", justify="right", style="magenta")

        for sheet in info['sheets']:
            table.add_row(
                str(sheet['index']),
                sheet['title'],
                str(sheet['rowCount']),
                str(sheet['columnCount'])
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@sheets_app.command("list")
def sheets_list_sheets(
    spreadsheet_id: str = typer.Argument(..., help="Spreadsheet ID or URL"),
):
    """
    List all sheets in a spreadsheet.

    Shows sheet names with row and column counts.
    """
    from .api import SheetsAPI

    try:
        api = SheetsAPI()
        sheets = api.list_sheets(spreadsheet_id)

        if not sheets:
            console.print("[yellow]No sheets found.[/yellow]")
            return

        table = Table(title="Sheets")
        table.add_column("Index", style="dim", justify="right")
        table.add_column("Sheet ID", style="dim")
        table.add_column("Title", style="cyan")
        table.add_column("Size", style="green")

        for sheet in sheets:
            table.add_row(
                str(sheet['index']),
                str(sheet['sheetId']),
                sheet['title'],
                f"{sheet['rowCount']} x {sheet['columnCount']}"
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@sheets_app.command("read")
def sheets_read(
    spreadsheet_id: str = typer.Argument(..., help="Spreadsheet ID or URL"),
    range_notation: Optional[str] = typer.Argument(None, help="A1 notation range (e.g., A1:D10)"),
    sheet: Optional[str] = typer.Option(None, "--sheet", "-s", help="Sheet name"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, csv, json"),
    limit: int = typer.Option(100, "--limit", "-l", help="Max rows to display in table format"),
    header: bool = typer.Option(True, "--header/--no-header", help="Treat first row as header"),
):
    """
    Read data from a spreadsheet.

    Supports table, CSV, and JSON output formats.

    Examples:
        gtools sheets read SPREADSHEET_ID
        gtools sheets read SPREADSHEET_ID A1:D10
        gtools sheets read SPREADSHEET_ID --sheet "Sheet1" --format csv -o data.csv
        gtools sheets read "https://docs.google.com/spreadsheets/d/ID/edit" --format json
    """
    from .api import SheetsAPI
    import json

    try:
        api = SheetsAPI()
        data = api.read_values(spreadsheet_id, range_notation, sheet)

        values = data["values"]
        if not values:
            console.print("[yellow]No data found in the specified range.[/yellow]")
            return

        # Format output
        if format == "csv":
            csv_content = api.export_to_csv(spreadsheet_id, range_notation, sheet)
            if output:
                with open(output, "w", encoding="utf-8") as f:
                    f.write(csv_content)
                console.print(f"[green]✓ Exported {data['rowCount']} rows to {output}[/green]")
            else:
                console.print(csv_content)

        elif format == "json":
            if header and len(values) > 1:
                headers = values[0]
                json_data = [
                    dict(zip(headers, row))
                    for row in values[1:]
                ]
            else:
                json_data = values

            json_output = json.dumps(json_data, indent=2, ensure_ascii=False)
            if output:
                with open(output, "w", encoding="utf-8") as f:
                    f.write(json_output)
                console.print(f"[green]✓ Exported {len(json_data)} records to {output}[/green]")
            else:
                console.print(json_output)

        else:  # table format
            table = Table(title=f"Data from {data['range']}")

            # Use first row as headers if enabled
            if header and len(values) > 0:
                for col in values[0]:
                    table.add_column(str(col), style="cyan")
                data_rows = values[1:limit+1] if len(values) > 1 else []
            else:
                # Generate column headers
                for i in range(data['columnCount']):
                    table.add_column(f"Col {i+1}", style="cyan")
                data_rows = values[:limit]

            for row in data_rows:
                table.add_row(*[str(cell) for cell in row])

            console.print(table)
            console.print(f"\n[dim]Showing {len(data_rows)} of {data['rowCount']} rows, {data['columnCount']} columns[/dim]")
            console.print(f"[dim]Range: {data['range']}[/dim]")

            if output:
                csv_content = api.export_to_csv(spreadsheet_id, range_notation, sheet)
                with open(output, "w", encoding="utf-8") as f:
                    f.write(csv_content)
                console.print(f"[green]✓ Also exported to {output}[/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
