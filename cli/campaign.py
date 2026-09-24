"""
STALKER - Campaign CLI Module
Campaign management commands for the CLI interface.
"""

import asyncio
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import box

console = Console()

# ---------------------------------------------------------------------------
# Helpers – thin HTTP client that talks to the running backend
# ---------------------------------------------------------------------------

BACKEND_URL = os.getenv("STALKER_BACKEND_URL", "http://127.0.0.1:8443")


def _sync_request(method: str, path: str, **kwargs):
    """Synchronous wrapper around httpx for CLI usage."""
    import httpx

    url = f"{BACKEND_URL}{path}"
    try:
        with httpx.Client(timeout=10) as client:
            resp = getattr(client, method)(url, **kwargs)
            resp.raise_for_status()
            return resp.json()
    except httpx.ConnectError:
        console.print(
            "[bold red]✗[/] Cannot reach the STALKER backend. "
            "Start the server first with option [bold cyan][03][/]."
        )
        return None
    except httpx.HTTPStatusError as exc:
        console.print(f"[bold red]✗[/] Server error: {exc.response.status_code}")
        return None


# ---------------------------------------------------------------------------
# Campaign creation
# ---------------------------------------------------------------------------

def create_campaign():
    """Interactive campaign creation wizard."""
    console.print(
        Panel(
            "[bold bright_white]CREATE TRAINING CAMPAIGN[/]",
            border_style="bright_magenta",
            padding=(1, 4),
        )
    )

    name = Prompt.ask("  [bright_cyan]Campaign Name[/]")
    description = Prompt.ask("  [bright_cyan]Description[/]")
    hours = int(
        Prompt.ask("  [bright_cyan]Duration (hours)[/]", default="24")
    )

    console.print()
    console.print("  [dim]Creating campaign …[/]")

    data = _sync_request(
        "post",
        "/api/campaigns",
        json={
            "name": name,
            "description": description,
            "duration_hours": hours,
        },
    )

    if data is None:
        return

    console.print()
    table = Table(box=box.HEAVY_EDGE, border_style="bright_magenta", show_header=False)
    table.add_column("Field", style="bold bright_cyan")
    table.add_column("Value", style="bright_white")
    table.add_row("Campaign ID", data.get("id", "—"))
    table.add_row("Name", data.get("name", "—"))
    table.add_row("Status", data.get("status", "—"))
    table.add_row("Training URL", data.get("training_url", "—"))
    table.add_row("Created", data.get("created_at", "—"))
    table.add_row("Expires", data.get("expires_at", "—"))
    console.print(table)
    console.print()


# ---------------------------------------------------------------------------
# Generate awareness link
# ---------------------------------------------------------------------------

def generate_awareness_link():
    """Generate a shareable awareness training link."""
    console.print(
        Panel(
            "[bold bright_white]GENERATE AWARENESS LINK[/]",
            border_style="bright_magenta",
            padding=(1, 4),
        )
    )

    campaigns = _sync_request("get", "/api/campaigns")
    if not campaigns:
        console.print("  [yellow]No campaigns found. Create one first.[/]")
        return

    table = Table(box=box.SIMPLE_HEAVY, border_style="bright_magenta")
    table.add_column("#", style="bold bright_cyan", width=4)
    table.add_column("ID", style="dim")
    table.add_column("Name", style="bright_white")
    table.add_column("Status", style="green")
    for idx, c in enumerate(campaigns, 1):
        table.add_row(str(idx), c["id"][:8], c["name"], c["status"])
    console.print(table)

    choice = int(Prompt.ask("  [bright_cyan]Select campaign #[/]", default="1")) - 1
    if 0 <= choice < len(campaigns):
        campaign = campaigns[choice]
        local_url = f"{BACKEND_URL}/train/{campaign['id']}"
        public_url = os.getenv("STALKER_PUBLIC_URL", "").rstrip("/")

        if public_url:
            tunnel_url = f"{public_url}/train/{campaign['id']}"
            console.print(
                Panel(
                    f"[bold bright_white]Training URLs:[/]\n\n"
                    f"  [bold green]PUBLIC (HTTPS):[/]\n"
                    f"  [bold underline bright_cyan]{tunnel_url}[/]\n\n"
                    f"  [dim]LOCAL:[/]\n"
                    f"  [dim]{local_url}[/]\n\n"
                    f"  [bold green]✓[/] [dim]Camera & Location will work over HTTPS[/]",
                    border_style="green",
                    padding=(1, 4),
                )
            )
        else:
            console.print(
                Panel(
                    f"[bold bright_white]Training URL:[/]\n\n"
                    f"[bold underline bright_cyan]{local_url}[/]\n\n"
                    f"[yellow]⚠ No tunnel active. Start server with tunnel "
                    f"for camera/location on remote devices.[/]",
                    border_style="green",
                    padding=(1, 4),
                )
            )


# ---------------------------------------------------------------------------
# Manage campaigns
# ---------------------------------------------------------------------------

def manage_campaigns():
    """List and manage existing campaigns."""
    console.print(
        Panel(
            "[bold bright_white]MANAGE CAMPAIGNS[/]",
            border_style="bright_magenta",
            padding=(1, 4),
        )
    )

    campaigns = _sync_request("get", "/api/campaigns")
    if not campaigns:
        console.print("  [yellow]No campaigns found.[/]")
        return

    table = Table(box=box.HEAVY_EDGE, border_style="bright_magenta")
    table.add_column("ID", style="dim", width=10)
    table.add_column("Name", style="bright_white")
    table.add_column("Participants", style="bright_cyan", justify="center")
    table.add_column("Status", style="green")
    table.add_column("Created", style="dim")

    for c in campaigns:
        table.add_row(
            c["id"][:8],
            c["name"],
            str(c.get("participant_count", 0)),
            c["status"],
            c.get("created_at", "—")[:19],
        )
    console.print(table)


# ---------------------------------------------------------------------------
# View participant events
# ---------------------------------------------------------------------------

def view_participant_events():
    """Display participant training events."""
    console.print(
        Panel(
            "[bold bright_white]PARTICIPANT EVENTS[/]",
            border_style="bright_magenta",
            padding=(1, 4),
        )
    )

    events = _sync_request("get", "/api/events")
    if not events:
        console.print("  [yellow]No events recorded yet.[/]")
        return

    table = Table(box=box.HEAVY_EDGE, border_style="bright_magenta")
    table.add_column("Participant", style="bold bright_cyan", width=12)
    table.add_column("Campaign", style="bright_white")
    table.add_column("Event", style="yellow")
    table.add_column("Timestamp", style="dim")

    for e in events:
        table.add_row(
            e.get("participant_id", "—")[:10],
            e.get("campaign_id", "—")[:8],
            e.get("event_type", "—"),
            e.get("timestamp", "—")[:19],
        )
    console.print(table)


# ---------------------------------------------------------------------------
# View location reports
# ---------------------------------------------------------------------------

def view_location_reports():
    """Display location permission events."""
    console.print(
        Panel(
            "[bold bright_white]LOCATION PERMISSION REPORTS[/]",
            border_style="bright_magenta",
            padding=(1, 4),
        )
    )

    locations = _sync_request("get", "/api/locations")
    if not locations:
        console.print("  [yellow]No location events recorded.[/]")
        return

    table = Table(box=box.HEAVY_EDGE, border_style="bright_magenta")
    table.add_column("Participant", style="bold bright_cyan", width=12)
    table.add_column("Permission", style="green")
    table.add_column("Latitude", style="bright_white", justify="right")
    table.add_column("Longitude", style="bright_white", justify="right")
    table.add_column("Map Link", style="underline bright_cyan")

    for loc in locations:
        status = loc.get("permission_status", "UNKNOWN")
        lat = loc.get("latitude")
        lon = loc.get("longitude")
        map_link = ""
        if lat and lon:
            map_link = f"https://maps.google.com/?q={lat},{lon}"
        table.add_row(
            loc.get("participant_id", "—")[:10],
            status,
            str(lat) if lat else "—",
            str(lon) if lon else "—",
            map_link or "—",
        )
    console.print(table)


# ---------------------------------------------------------------------------
# View browser info
# ---------------------------------------------------------------------------

def view_browser_info():
    """Display collected browser information."""
    console.print(
        Panel(
            "[bold bright_white]BROWSER INFORMATION[/]",
            border_style="bright_magenta",
            padding=(1, 4),
        )
    )

    info = _sync_request("get", "/api/browser-info")
    if not info:
        console.print("  [yellow]No browser data collected.[/]")
        return

    table = Table(box=box.HEAVY_EDGE, border_style="bright_magenta")
    table.add_column("Participant", style="bold bright_cyan", width=12)
    table.add_column("Browser", style="bright_white")
    table.add_column("OS", style="bright_white")
    table.add_column("Resolution", style="dim")
    table.add_column("Language", style="dim")
    table.add_column("Timezone", style="dim")

    for b in info:
        table.add_row(
            b.get("participant_id", "—")[:10],
            b.get("browser", "—"),
            b.get("os", "—"),
            b.get("screen_resolution", "—"),
            b.get("language", "—"),
            b.get("timezone", "—"),
        )
    console.print(table)


# ---------------------------------------------------------------------------
# Generate security report
# ---------------------------------------------------------------------------

def generate_report():
    """Generate an HTML/JSON security awareness report."""
    console.print(
        Panel(
            "[bold bright_white]GENERATE SECURITY REPORT[/]",
            border_style="bright_magenta",
            padding=(1, 4),
        )
    )

    campaigns = _sync_request("get", "/api/campaigns")
    if not campaigns:
        console.print("  [yellow]No campaigns to report on.[/]")
        return

    # Pick campaign
    for idx, c in enumerate(campaigns, 1):
        console.print(f"  [bright_cyan][{idx}][/] {c['name']}")
    choice = int(Prompt.ask("\n  [bright_cyan]Select campaign #[/]", default="1")) - 1
    if choice < 0 or choice >= len(campaigns):
        return

    campaign_id = campaigns[choice]["id"]
    fmt = Prompt.ask(
        "  [bright_cyan]Format[/]", choices=["html", "json"], default="html"
    )

    data = _sync_request("get", f"/api/reports/{campaign_id}?format={fmt}")
    if not data:
        return

    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    filename = reports_dir / f"stalker_report_{campaign_id[:8]}.{fmt}"

    if fmt == "json":
        filename.write_text(json.dumps(data, indent=2))
    else:
        filename.write_text(data.get("html", ""))

    console.print(
        f"\n  [bold green]✓[/] Report saved to [underline]{filename}[/]"
    )


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

def show_configuration():
    """Display current configuration."""
    console.print(
        Panel(
            "[bold bright_white]CONFIGURATION[/]",
            border_style="bright_magenta",
            padding=(1, 4),
        )
    )

    table = Table(box=box.HEAVY_EDGE, border_style="bright_magenta", show_header=False)
    table.add_column("Key", style="bold bright_cyan")
    table.add_column("Value", style="bright_white")
    table.add_row("Backend URL", BACKEND_URL)
    table.add_row("Database", os.getenv("STALKER_DATABASE_URL", "sqlite (default)"))
    table.add_row("Bind Host", os.getenv("STALKER_BIND_HOST", "0.0.0.0"))
    table.add_row("Display Host", os.getenv("STALKER_HOST", "127.0.0.1"))
    table.add_row("Port", os.getenv("STALKER_PORT", "8443"))
    table.add_row("Debug", os.getenv("STALKER_DEBUG", "true"))

    public_url = os.getenv("STALKER_PUBLIC_URL", "")
    if public_url:
        table.add_row("Tunnel (HTTPS)", f"[bold green]{public_url}[/]")
    else:
        table.add_row("Tunnel (HTTPS)", "[dim]Not active[/]")

    console.print(table)
