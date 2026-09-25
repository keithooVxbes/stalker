"""
STALKER - CLI Banner Module
Security Tracking Awareness & Learning Knowledge Education Research
Creator: 0xPurpleMiaw16
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box

console = Console()

BANNER = r"""
[bold bright_magenta]███████╗████████╗ █████╗ ██╗     ██╗  ██╗███████╗██████╗ [/]
[bold bright_magenta]██╔════╝╚══██╔══╝██╔══██╗██║     ██║ ██╔╝██╔════╝██╔══██╗[/]
[bold magenta]███████╗   ██║   ███████║██║     █████╔╝ █████╗  ██████╔╝[/]
[bold purple4]╚════██║   ██║   ██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗[/]
[bold dark_magenta]███████║   ██║   ██║  ██║███████╗██║  ██╗███████╗██║  ██║[/]
[bold dark_magenta]╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝[/]
"""

VERSION = "1.0.0"
CREATOR = "0xPurpleMiaw16"
CODENAME = "STALKER"
FULL_NAME = "Security Tracking Awareness & Learning Knowledge Education Research"

MODULES = [
    ("Campaign Generator", True),
    ("Training Landing Page", True),
    ("Permission Awareness", True),
    ("Browser Analysis", True),
    ("Reporting Engine", True),
    ("Camera Awareness", True),
]


def display_banner():
    """Display the STALKER framework banner with system info."""
    console.print(BANNER)
    console.print(
        f"  [dim italic]Creator:[/] [bold bright_cyan]{CREATOR}[/]\n"
    )



def display_separator():
    """Print a separator line."""
    console.print(
        "[bright_magenta]" + "─" * 60 + "[/]"
    )
