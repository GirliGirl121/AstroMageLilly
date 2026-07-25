#!/usr/bin/env python3
# lilly.py — The Royal Celestial Observatory

import sys
import time
import shutil
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.live import Live

from config import COLORS

console = Console()


def term_width() -> int:
    """Get terminal width, clamped for snug phone fit."""
    try:
        w = shutil.get_terminal_size().columns
        return max(40, min(w, 78))
    except Exception:
        return 56


def make_banner() -> Panel:
    """Create the celestial banner — adapts to phone or desktop."""
    w = term_width()

    if w >= 64:
        # Full desktop banner
        lines = [
            "",
            " ✦ · ✧ · ✦ · ✧ · ✦ · ✧ · ✦ · ✧ · ✦ · ✧ · ✦",
            "",
            " ██╗     ██╗██╗     ██╗     ██╗   ██╗",
            " ██║     ██║██║     ██║     ╚██╗ ██╔╝",
            " ██║     ██║██║     ██║      ╚████╔╝ ",
            " ██║     ██║██║     ██║       ╚██╔╝  ",
            " ███████╗██║███████╗███████╗   ██║   ",
            " ╚══════╝╚═╝╚══════╝╚══════╝   ╚═╝   ",
            "",
            " ✨ M A I D E N  O F  C O S M I C  S T A R S ✨",
            "",
            " ✦ · ✧ · ✦ · ✧ · ✦ · ✧ · ✦ · ✧ · ✦ · ✧ · ✦",
            "",
        ]
        pad = (1, 3)
    elif w >= 52:
        # Medium — tablets or wide phones
        lines = [
            "",
            " ✦ · ✧ · ✦ · ✧ · ✦ · ✧ · ✦",
            "",
            "  ╦   ╦ ╦   ╦   ╦ ",
            "  ║   ║ ║   ║   ║ ",
            "  ║   ║ ║   ║   ║ ",
            "  ╚═══╝ ╚═══╝   ╩ ",
            "",
            " ✨ M A I D E N  O F  C O S M I C  S T A R S ✨",
            "",
            " ✦ · ✧ · ✦ · ✧ · ✦ · ✧ · ✦",
            "",
        ]
        pad = (1, 2)
    else:
        # Compact — narrow phone screens
        lines = [
            "",
            " ✦ · ✧ · ✦",
            "",
            "   ✨ L I L L Y ✨",
            "",
            " Maiden of Cosmic Stars",
            "",
            " ✦ · ✧ · ✦",
            "",
        ]
        pad = (1, 1)

    gradient_colors = [COLORS["moon"], COLORS["lilac"], COLORS["rose"],
                       COLORS["coral"], COLORS["sky"], COLORS["azure"]]

    text = Text()
    for i, line in enumerate(lines):
        color = gradient_colors[i % len(gradient_colors)]
        text.append(line + "\n", style=f"bold {color}")

    panel_w = min(w - 2, 66) if w >= 64 else min(w - 2, 52) if w >= 52 else min(w - 2, 40)

    return Panel(
        Align.center(text),
        border_style=f"bold {COLORS['moon']}",
        padding=pad,
        width=panel_w,
        title="[bold {}]🌙 Welcome Home, Gigi ❤️[/bold {}]".format(
            COLORS["rose"], COLORS["rose"]),
        subtitle="[dim {}]The stars incline; they do not compel[/dim {}]".format(
            COLORS["sky"], COLORS["sky"]),
    )


def startup_sequence():
    """Display the animated startup."""
    console.clear()
    w = term_width()

    with Live(make_banner(), refresh_per_second=4, screen=False) as live:
        time.sleep(1.2)

    console.print()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status_w = min(w - 6, 58)
    status = Panel(
        f"[{COLORS['sky']}]🪐 Observatory Systems: [bold green]ONLINE[/bold green]\n"
        f"[{COLORS['rose']}]📅 Terrestrial Time: [bold]{now}[/bold]\n"
        f"[{COLORS['moon']}]🔭 Ephemeris: [bold green]LOADED[/bold green]\n"
        f"[{COLORS['coral']}]📚 Manuscripts: [bold green]INDEXED[/bold green]\n"
        f"[{COLORS['azure']}]✨ Ready to illuminate.[/]",
        title="[bold {}]Observatory Status[/bold {}]".format(COLORS["gold"], COLORS["gold"]),
        border_style=COLORS["lilac"],
        width=status_w,
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

