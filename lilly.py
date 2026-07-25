#!/usr/bin/env python3
# lilly.py — The Royal Celestial Observatory

import sys
import time
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.live import Live

from config import COLORS

console = Console()


def make_banner() -> Panel:
    """Create the celestial banner with purple-pink-blue gradient."""
    lines = [
        "",
        "    ✦  ·  ✧  ·  ✦  ·  ✧  ·  ✦  ·  ✧  ·  ✦  ·  ✧  ·  ✦  ·  ✧  ·  ✦",
        "",
        "         ██╗     ██╗██╗     ██╗     ██╗   ██╗",
        "         ██║     ██║██║     ██║     ╚██╗ ██╔╝",
        "         ██║     ██║██║     ██║      ╚████╔╝ ",
        "         ██║     ██║██║     ██║       ╚██╔╝  ",
        "         ███████╗██║███████╗███████╗   ██║   ",
        "         ╚══════╝╚═╝╚══════╝╚══════╝   ╚═╝   ",
        "",
        "      ✨  M A I D E N   O F   C O S M I C   S T A R S  ✨",
        "",
        "    ✦  ·  ✧  ·  ✦  ·  ✧  ·  ✦  ·  ✧  ·  ✦  ·  ✧  ·  ✦  ·  ✧  ·  ✦",
        "",
    ]

    gradient_colors = [COLORS["moon"], COLORS["lilac"], COLORS["rose"],
                       COLORS["coral"], COLORS["sky"], COLORS["azure"]]

    text = Text()
    for i, line in enumerate(lines):
        color = gradient_colors[i % len(gradient_colors)]
        text.append(line + "\n", style=f"bold {color}")

    return Panel(
        Align.center(text),
        border_style=f"bold {COLORS['moon']}",
        padding=(1, 4),
        title="[bold {}]🌙  Welcome Home, Gigi  ❤️[/bold {}]".format(
            COLORS["rose"], COLORS["rose"]),
        subtitle="[dim {}]The stars incline; they do not compel[/dim {}]".format(
            COLORS["sky"], COLORS["sky"]),
    )


def startup_sequence():
    """Display the animated startup."""
    console.clear()

    with Live(make_banner(), refresh_per_second=4, screen=False) as live:
        time.sleep(1.2)

    console.print()

    now = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
    status = Panel(
        f"[{COLORS['sky']}]🪐  Observatory Systems: [bold green]ONLINE[/bold green]\n"
        f"[{COLORS['rose']}]📅  Terrestrial Time: [bold]{now}[/bold]\n"
        f"[{COLORS['moon']}]🔭  Ephemeris: [bold green]LOADED[/bold green]\n"
        f"[{COLORS['coral']}]📚  Manuscripts: [bold green]INDEXED[/bold green]\n"
        f"[{COLORS['azure']}]✨  Ready to illuminate.[/]",
        title="[bold {}]Observatory Status[/bold {}]".format(COLORS["gold"], COLORS["gold"]),
        border_style=COLORS["lilac"],
        width=60,
    )
    console.print(Align.center(status))
    console.print()


def main():
    startup_sequence()

    try:
        from dashboard import Dashboard
        dashboard = Dashboard()
        dashboard.run()
    except KeyboardInterrupt:
        console.print(f"\n\n[{COLORS['moon']}]🌙 The observatory grows quiet. Goodnight, Gigi. ❤️[/]\n")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]An error occurred: {e}[/bold red]")
        raise


if __name__ == "__main__":
    main()

