"""
STALKER - CLI Menu System
Interactive menu for the STALKER framework.
"""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.table import Table
from rich import box

console = Console()

MENU_ITEMS = [
    ("01", "Create Training Campaign"),
    ("02", "Generate Awareness Link"),
    ("03", "Start Training Server"),
    ("04", "Manage Campaigns"),
    ("05", "View Participant Events"),
    ("06", "View Location Permission Reports"),
    ("07", "View Browser Information"),
    ("08", "Generate Security Report"),
    ("09", "Configuration"),
    ("00", "Exit"),
]


def display_menu():
    """Render the main menu and return the user's choice."""
    table = Table(
        box=box.SIMPLE_HEAVY,
        border_style="bright_magenta",
        show_header=False,
        padding=(0, 3),
        expand=True,
    )
    table.add_column("Code", style="bold bright_cyan", width=6, justify="center")
    table.add_column("Action", style="bright_white")

    for code, label in MENU_ITEMS:
        table.add_row(f"[{code}]", label)

    console.print(
        Panel(
            table,
            title="[bold bright_white]MAIN MENU[/]",
            border_style="bright_magenta",
            padding=(1, 2),
        )
    )

    choice = Prompt.ask(
        "\n  [bold bright_cyan]stalker[/][bold bright_magenta]>[/]",
        default="00",
    )
    return choice.strip().zfill(2)
