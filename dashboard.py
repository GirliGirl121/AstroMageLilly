#!/usr/bin/env python3
# dashboard.py — The Observatory Control Panel

import os
import sys
import shutil
from datetime import datetime, timedelta
from typing import Optional, Dict

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.align import Align
from rich.prompt import Prompt
from rich.text import Text

from config import COLORS, DEFAULT_NATAL
from unified_engine import engine
from planetary_hours import ph
from lunar_mansions import lmc
from wafq import wafq
from vedic import vedic
from electional import planner
from fixed_stars import scanner
from companion import companion
from profiles import vault

console = Console()


def term_width() -> int:
    try:
        w = shutil.get_terminal_size().columns
        return max(40, min(w, 78))
    except Exception:
        return 56


class Dashboard:
    def __init__(self):
        self.running = True
        self.current_jd = None
        self.update_sky()

    def update_sky(self):
        now = datetime.now()
        self.current_jd = engine.jd_from_datetime(now, DEFAULT_NATAL["timezone_offset"])

    def show_menu(self):
        c = COLORS
        w = term_width()
        mw = min(w - 4, 58)

        menu = Panel(
            "[bold " + c['moon'] + "]🌙 L I L L Y — M A I N  M E N U[/bold " + c['moon'] + "]\n\n"
            "[" + c['rose'] + "]1[/] Live Sky & Transits\n"
            "[" + c['sky'] + "]2[/] Planetary Hours\n"
            "[" + c['coral'] + "]3[/] Lunar Mansion\n"
            "[" + c['azure'] + "]4[/] Magic Squares (Wafq)\n"
            "[" + c['lilac'] + "]5[/] Vedic Chart (Jyotish)\n"
            "[" + c['gold'] + "]6[/] Electional Planner\n"
            "[" + c['rose'] + "]7[/] Fixed Star Scan\n"
            "[" + c['sky'] + "]8[/] Gigi's Natal Chart\n"
            "[" + c['coral'] + "]9[/] Companion Chat\n"
            "[" + c['azure'] + "]10[/] High-Precision Sky (Skyfield)\n"
            "[" + c['lilac'] + "]11[/] Synastry & Transits\n"
            "[" + c['gold'] + "]12[/] Profile Vault\n"
            "[" + c['rose'] + "]13[/] Composite Chart\n"
            "[" + c['sky'] + "]14[/] Daily Brief 🆕\n"
            "[" + c['moon'] + "]0[/] Exit Observatory\n\n"
            "[dim]Enter a number to select...[/dim]",
            border_style=COLORS["lilac"],
            width=mw,
        )
        console.print(Align.center(menu))

    def live_sky(self):
        self.update_sky()
        positions = engine.get_all_planets(self.current_jd)
        moon_phase = engine.get_moon_phase(self.current_jd)

        table = Table(title="[bold " + COLORS['sky'] + "]🪐 Live Sky[/bold " + COLORS['sky'] + "]",
                      border_style=COLORS["lilac"])
        table.add_column("Planet", style=COLORS["gold"])
        table.add_column("Sign", style=COLORS["rose"])
        table.add_column("Deg", justify="right", style=COLORS["coral"])
        table.add_column("R", justify="center", style="dim")
        table.add_column("Element", style=COLORS["azure"])

        for name, p in positions.items():
            retro = "℞" if p.get("retrograde") else ""
            table.add_row(
                f"{p.get('symbol', '')} {name}",
                p["sign"],
                str(p["degree_in_sign"]),
                retro,
                p["element"]
            )

        console.print(table)
        console.print("\n[bold " + COLORS['moon'] + "]🌙 Moon Phase:[/] " + moon_phase['phase'] + " — "
                      + str(moon_phase['illumination']) + "% illuminated, age " + str(moon_phase['age']) + " days")
        console.print()

    def planetary_hours_menu(self):
        self.update_sky()
        now = datetime.now()
        hour = ph.get_planetary_hour(now, DEFAULT_NATAL["lat"], DEFAULT_NATAL["lon"],
                                     DEFAULT_NATAL["timezone_offset"])

        panel = Panel(
            "[bold " + COLORS['gold'] + "]" + hour['symbol'] + " " + hour['planet'] + "[/bold " + COLORS['gold'] + "]\n"
            "[" + COLORS['sky'] + "]Hour " + str(hour['hour_number']) + " of the " + ('Day' if hour['is_day'] else 'Night') + "[/]\n"
            "[" + COLORS['rose'] + "]Metal:[/] " + hour['metal'] + "\n"
            "[" + COLORS['coral'] + "]Angel:[/] " + hour['angel'] + "\n"
            "[dim]Hour ends at " + hour['hour_end'] + "[/dim]",
            title="[bold " + COLORS['moon'] + "]Current Planetary Hour[/bold " + COLORS['moon'] + "]",
            border_style=COLORS["lilac"],
        )
        console.print(panel)
        console.print()

    def lunar_mansion_menu(self):
        self.update_sky()
        mansion = lmc.current_mansion(self.current_jd)

        panel = Panel(
            "[bold " + COLORS['gold'] + "]" + str(mansion['number']) + ". " + mansion['name'] + "[/bold " + COLORS['gold'] + "]\n"
            "[" + COLORS['sky'] + "]Arabic:[/] " + mansion['arabic'] + "\n"
            "[" + COLORS['rose'] + "]Meaning:[/] " + mansion['meaning'] + "\n"
            "[" + COLORS['coral'] + "]Ruler:[/] " + mansion['ruler'] + "\n"
            "[" + COLORS['azure'] + "]Moon in:[/] " + mansion['moon_sign'] + "\n\n"
            "[italic " + COLORS['lilac'] + "]" + chr(8220) + mansion['interpretation'] + chr(8221) + "[/italic " + COLORS['lilac'] + "]",
            title="[bold " + COLORS['moon'] + "]🌙 Lunar Mansion[/bold " + COLORS['moon'] + "]",
            border_style=COLORS["lilac"],
        )
        console.print(panel)
        console.print()

    def wafq_menu(self):
        console.print("[bold " + COLORS['moon'] + "]✨ Magic Squares (Wafq)[/bold " + COLORS['moon'] + "]")
        console.print("[dim]Planets and their traditional squares:[/dim]\n")

        planets = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
        for p in planets:
            sq = wafq.get_planet_square(p)
            wafq.display_square(sq)
        console.print()

    def vedic_menu(self):
        self.update_sky()
        console.print("[bold " + COLORS['sky'] + "]Calculating sidereal positions...[/bold " + COLORS['sky'] + "]")
        vedic_data = vedic.full_vedic_chart(
            self.current_jd, DEFAULT_NATAL["lat"], DEFAULT_NATAL["lon"])
        vedic.print_vedic_table(vedic_data)
        console.print()

    def electional_menu(self):
        self.update_sky()
        now = datetime.now()
        end = now + timedelta(days=3)

        console.print("[bold " + COLORS['gold'] + "]🔮 Scanning for favorable windows...[/bold " + COLORS['gold'] + "]")
        target = Prompt.ask("Which planet", choices=["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"],
                            default="Moon")

        elections = planner.find_elections(now, end, target, interval_hours=4)
        top = [e for e in elections if e["score"] >= 50][:5]

        if top:
            for e in top:
                planner.print_election(e)
        else:
            console.print("[dim]No strong windows found in the next 3 days. Patience, Gigi.[/dim]")
        console.print()

    def fixed_stars_menu(self):
        self.update_sky()
        console.print("[bold " + COLORS['gold'] + "]⭐ Scanning royal stars...[/bold " + COLORS['gold'] + "]")
        alignments = scanner.scan_natal_chart(self.current_jd)
        scanner.print_alignments(alignments)
        console.print()

    def natal_chart(self):
        dt = datetime.strptime(f"{DEFAULT_NATAL['date']} {DEFAULT_NATAL['time']}",
                               "%Y-%m-%d %H:%M:%S")
        jd = engine.jd_from_datetime(dt, DEFAULT_NATAL["timezone_offset"])
        positions = engine.get_all_planets(jd)
        houses = engine.calculate_houses(jd, DEFAULT_NATAL["lat"], DEFAULT_NATAL["lon"])
        aspects = engine.calculate_aspects(positions)
        lots = engine.calculate_arabic_parts(jd, DEFAULT_NATAL["lat"], DEFAULT_NATAL["lon"])

        console.print("[bold " + COLORS['rose'] + "]❤️ Gigi's Natal Chart[/bold " + COLORS['rose'] + "]")
        console.print("[dim]" + DEFAULT_NATAL['date'] + " " + DEFAULT_NATAL['time'] + " — " + DEFAULT_NATAL['location'] + "[/dim]\n")

        table = Table(border_style=COLORS["lilac"])
        table.add_column("Planet", style=COLORS["sky"])
        table.add_column("Sign", style=COLORS["rose"])
        table.add_column("House", style=COLORS["coral"])
        table.add_column("Deg", justify="right")

        for name, p in positions.items():
            house_num = engine.get_house_for_longitude(p["longitude"], houses)
            retro = " ℞" if p.get("retrograde") else ""
            table.add_row(
                f"{p.get('symbol', '')} {name}{retro}",
                p["sign"],
                str(house_num),
                str(p["degree_in_sign"])
            )

        for name, p in lots.items():
            house_num = engine.get_house_for_longitude(p["longitude"], houses)
            table.add_row(
                f"{p.get('symbol', '')} {p['name']}",
                p["sign"],
                str(house_num),
                str(p["degree_in_sign"])
            )

        console.print(table)

        if aspects:
            asp_table = Table(title="Major Aspects", border_style=COLORS["lilac"])
            asp_table.add_column("Aspect", style=COLORS["gold"])
            asp_table.add_column("Planets", style=COLORS["sky"])
            asp_table.add_column("Orb", justify="right")
            for a in aspects[:10]:
                app = " applying" if a["applying"] else " separating"
                asp_table.add_row(a["aspect"], f"{a['planet1']} — {a['planet2']}",
                                  f"{a['orb']}°{app}")
            console.print(asp_table)
        console.print()

    def companion_chat(self):
        console.print("[bold " + COLORS['moon'] + "]🌙 Lilly is listening... (type 'back' to return)[/bold " + COLORS['moon'] + "]")
        while True:
            msg = Prompt.ask("[dim]You[/dim]")
            if msg.lower() in ["back", "quit", "exit", "0"]:
                break
            reply = companion.chat(msg, self.current_jd)
            console.print(Panel(reply, border_style=COLORS["lilac"],
                                title="[bold " + COLORS['rose'] + "]Lilly[/bold " + COLORS['rose'] + "]"))

    def skyfield_menu(self):
        console.print("[bold " + COLORS['sky'] + "]🔭 Skyfield High-Precision Astronomy[/bold " + COLORS['sky'] + "]")
        ephe = engine.ephe_name
        console.print("[dim]Ephemeris: " + ephe + " — JPL planetary positions with full atmospheric refraction.[/dim]\n")

        sub = Panel(
            "[" + COLORS['rose'] + "]1[/] Planet Positions (RA/Dec/Alt/Az)\n"
            "[" + COLORS['sky'] + "]2[/] Rise / Set / Transit Times\n"
            "[" + COLORS['coral'] + "]3[/] Find Conjunction\n"
            "[" + COLORS['azure'] + "]4[/] Angular Separation\n"
            "[" + COLORS['gold'] + "]5[/] Precise Moon Phase\n"
            "[" + COLORS['moon'] + "]0[/] Back to Main Menu",
            title="[bold " + COLORS['azure'] + "]Skyfield Submenu[/bold " + COLORS['azure'] + "]",
            border_style=COLORS["lilac"],
        )
        console.print(Align.center(sub))

        sub_choice = Prompt.ask("Skyfield", choices=["1","2","3","4","5","0"], default="1")

        if sub_choice == "1":
            bodies = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
            positions = []
            for b in bodies:
                try:
                    positions.append(engine.high_precision_pos(b, DEFAULT_NATAL["lat"], DEFAULT_NATAL["lon"]))
                except Exception as e:
                    console.print(f"[dim red]Could not compute {b}: {e}[/dim red]")
            if positions:
                engine.print_positions_table(positions)
        elif sub_choice == "2":
            body = Prompt.ask("Which body", default="Sun")
            today = datetime.now()
            try:
                events = engine.riset_transit(body, today, DEFAULT_NATAL["lat"], DEFAULT_NATAL["lon"])
                table = Table(title="[bold " + COLORS['gold'] + "]🌅 " + body + " Today — Cape Town[/bold " + COLORS['gold'] + "]", border_style=COLORS["lilac"])
                table.add_column("Event", style=COLORS["sky"])
                table.add_column("Time", style=COLORS["rose"])
                for e in events:
                    icon = "🌅" if e['event'] == 'Rise' else "🌇" if e['event'] == 'Set' else "🔭"
                    table.add_row(f"{icon} {e['event']}", e['time'])
                console.print(table)
            except Exception as e:
                console.print(f"[dim red]Could not compute: {e}[/dim red]")
        elif sub_choice == "3":
            b1 = Prompt.ask("First body", default="Venus")
            b2 = Prompt.ask("Second body", default="Jupiter")
            start = datetime.now()
            end = start + timedelta(days=30)
            try:
                result = engine.find_conjunction(b1, b2, start, end)
                if result:
                    console.print(Panel(
                        "[bold " + COLORS['gold'] + "]" + result['body1'] + " & " + result['body2'] + "[/bold " + COLORS['gold'] + "]\n"
                        "[" + COLORS['sky'] + "]Closest approach:[/] " + result['time'] + "\n"
                        "[" + COLORS['rose'] + "]Separation:[/] " + str(result['separation_deg']) + "°",
                        title="[bold " + COLORS['moon'] + "]✨ Conjunction Found[/bold " + COLORS['moon'] + "]",
                        border_style=COLORS["lilac"],
                    ))
                else:
                    console.print("[dim]No close conjunction found in the next 30 days.[/dim]")
            except Exception as e:
                console.print(f"[dim red]Could not search: {e}[/dim red]")
        elif sub_choice == "4":
            b1 = Prompt.ask("First body", default="Moon")
            b2 = Prompt.ask("Second body", default="Venus")
            try:
                sep = engine.angular_separation(b1, b2)
                console.print(Panel(
                    "[bold " + COLORS['gold'] + "]" + sep['body1'] + " — " + sep['body2'] + "[/bold " + COLORS['gold'] + "]\n"
                    "[" + COLORS['sky'] + "]Separation:[/] " + str(sep['separation_deg']) + "° (" + str(sep['separation_arcmin']) + "')",
                    border_style=COLORS["lilac"],
                ))
            except Exception as e:
                console.print(f"[dim red]Could not compute: {e}[/dim red]")
        elif sub_choice == "5":
            try:
                phase = engine.precise_moon_phase()
                console.print(Panel(
                    "[bold " + COLORS['moon'] + "]🌙 " + phase['phase_name'] + "[/bold " + COLORS['moon'] + "]\n"
                    "[" + COLORS['sky'] + "]Illumination:[/] " + str(phase['illumination_percent']) + "%\n"
                    "[" + COLORS['rose'] + "]Elongation:[/] " + str(phase['elongation_deg']) + "°\n"
                    "[" + COLORS['coral'] + "]Distance:[/] " + str(phase['distance_km']) + " km\n"
                    "[" + COLORS['azure'] + "]Age:[/] " + str(phase['age_days']) + " days",
                    border_style=COLORS["lilac"],
                ))
            except Exception as e:
                console.print(f"[dim red]Could not compute: {e}[/dim red]")

    def synastry_menu(self):
        self.update_sky()
        dt = datetime.strptime(f"{DEFAULT_NATAL['date']} {DEFAULT_NATAL['time']}",
                               "%Y-%m-%d %H:%M:%S")
        gigi = engine.get_full_chart(
            dt, DEFAULT_NATAL["lat"], DEFAULT_NATAL["lon"],
            DEFAULT_NATAL["timezone_offset"], name="Gigi"
        )

        trans = engine.transits(gigi, self.current_jd, orb=5.0)

        console.print("[bold " + COLORS['rose'] + "]❤️ Gigi's Current Transits[/bold " + COLORS['rose'] + "]")
        console.print("[dim]Natal: " + DEFAULT_NATAL['date'] + " " + DEFAULT_NATAL['time'] + " — " + DEFAULT_NATAL['location'] + "[/dim]\n")

        if trans["inter_aspects"]:
            table = Table(title="Major Transit Aspects", border_style=COLORS["lilac"])
            table.add_column("Transit", style=COLORS["gold"])
            table.add_column("Natal", style=COLORS["sky"])
            table.add_column("Aspect", style=COLORS["rose"])
            table.add_column("Orb", justify="right", style=COLORS["coral"])
            for a in trans["inter_aspects"][:12]:
                table.add_row(
                    str(a['planet2']),
                    str(a['planet1']),
                    a["aspect"],
                    str(a['orb']) + "°"
                )
            console.print(table)
        else:
            console.print("[dim]No major transits within 5° orb right now.[/dim]")

        console.print("\n[bold " + COLORS['azure'] + "]🏠 Transit Planets in Gigi's Houses[/bold " + COLORS['azure'] + "]")
        overlay_table = Table(border_style=COLORS["lilac"])
        overlay_table.add_column("Planet", style=COLORS["gold"])
        overlay_table.add_column("House", style=COLORS["sky"])
        overlay_table.add_column("House Sign", style=COLORS["rose"])

        current_positions = engine.get_all_planets(self.current_jd)
        houses = gigi["houses"]
        for name, pos in current_positions.items():
            if name in ["North Node", "South Node", "Chiron"]:
                continue
            h = engine.get_house_for_longitude(pos["longitude"], houses)
            house_sign = houses[h-1]["sign"] if houses and 1 <= h <= 12 else "?"
            overlay_table.add_row(
                f"{pos.get('symbol', '')} {name}",
                str(h),
                house_sign
            )
        console.print(overlay_table)
        console.print()

    def profile_vault_menu(self):
        while True:
            sub = Panel(
                "[" + COLORS['rose'] + "]1[/] List Profiles\n"
                "[" + COLORS['sky'] + "]2[/] Add Profile\n"
                "[" + COLORS['coral'] + "]3[/] Delete Profile\n"
                "[" + COLORS['azure'] + "]4[/] View Profile Chart\n"
                "[" + COLORS['moon'] + "]0[/] Back to Main Menu",
                title="[bold " + COLORS['gold'] + "]📚 Profile Vault[/bold " + COLORS['gold'] + "]",
                border_style=COLORS["lilac"],
            )
            console.print(Align.center(sub))

            choice = Prompt.ask("Vault", choices=["1","2","3","4","0"], default="1")

            if choice == "1":
                console.print("[bold " + COLORS['gold'] + "]Saved Profiles[/bold " + COLORS['gold'] + "]")
                vault.display_all()
                console.print()

            elif choice == "2":
                console.print("[bold " + COLORS['sky'] + "]Add New Profile[/bold " + COLORS['sky'] + "]")
                name = Prompt.ask("Name")
                date = Prompt.ask("Date (YYYY-MM-DD)")
                time = Prompt.ask("Time (HH:MM:SS)")
                lat = float(Prompt.ask("Latitude"))
                lon = float(Prompt.ask("Longitude"))
                tz = float(Prompt.ask("Timezone offset (e.g. 2.0)", default="2.0"))
                loc = Prompt.ask("Location", default="")
                vault.add(name, date, time, lat, lon, tz, loc)
                console.print(f"[green]✓ {name} saved to the vault.[/green]\n")

            elif choice == "3":
                console.print("[bold " + COLORS['coral'] + "]Delete Profile[/bold " + COLORS['coral'] + "]")
                names = vault.list()
                if not names:
                    console.print("[dim]No profiles to delete.[/dim]\n")
                    continue
                for n in names:
                    console.print(f" • {n}")
                target = Prompt.ask("Name to delete")
                if vault.delete(target):
                    console.print(f"[green]✓ {target} removed.[/green]\n")
                else:
                    console.print(f"[red]✗ {target} not found.[/red]\n")

            elif choice == "4":
                names = vault.list()
                if not names:
                    console.print("[dim]No profiles saved yet.[/dim]\n")
                    continue
                for n in names:
                    console.print(f" • {n}")
                target = Prompt.ask("Whose chart")
                pdata = vault.get(target)
                if not pdata:
                    console.print("[red]✗ Profile not found.[/red]\n")
                    continue
                dt = datetime.strptime(f"{pdata['date']} {pdata['time']}", "%Y-%m-%d %H:%M:%S")
                chart = engine.get_full_chart(
                    dt, pdata["lat"], pdata["lon"],
                    pdata["timezone_offset"], name=target
                )
                self._print_chart_table(chart)

            elif choice == "0":
                break

            if choice != "0":
                Prompt.ask("[dim]Press Enter...[/dim]", default="")
                console.clear()

    def composite_menu(self):
        names = vault.list()
        if len(names) < 2:
            console.print("[dim]You need at least two saved profiles to build a composite.[/dim]")
            console.print("[dim]Go to Profile Vault (12) and add more souls.[/dim]\n")
            return

        console.print("[bold " + COLORS['gold'] + "]✨ Composite Chart Builder[/bold " + COLORS['gold'] + "]")
        console.print("[dim]Select two profiles to merge into a midpoint composite.[/dim]\n")
        for n in names:
            console.print(f" • {n}")

        p1_name = Prompt.ask("First profile")
        p2_name = Prompt.ask("Second profile")

        pdata1 = vault.get(p1_name)
        pdata2 = vault.get(p2_name)

        if not pdata1 or not pdata2:
            console.print("[red]✗ One or both profiles not found.[/red]\n")
            return

        dt1 = datetime.strptime(f"{pdata1['date']} {pdata1['time']}", "%Y-%m-%d %H:%M:%S")
        dt2 = datetime.strptime(f"{pdata2['date']} {pdata2['time']}", "%Y-%m-%d %H:%M:%S")

        chart1 = engine.get_full_chart(
            dt1, pdata1["lat"], pdata1["lon"],
            pdata1["timezone_offset"], name=p1_name
        )
        chart2 = engine.get_full_chart(
            dt2, pdata2["lat"], pdata2["lon"],
            pdata2["timezone_offset"], name=p2_name
        )

        comp = engine.composite_chart(chart1, chart2, name=f"{p1_name} + {p2_name}")

        console.print("\n[bold " + COLORS['moon'] + "]✨ " + comp['name'] + " — Midpoint Composite[/bold " + COLORS['moon'] + "]")
        console.print("[dim]The child of two skies, born from the space between.[/dim]\n")

        self._print_chart_table(comp)

        if comp["aspects"]:
            asp_table = Table(title="Composite Aspects", border_style=COLORS["lilac"])
            asp_table.add_column("Aspect", style=COLORS["gold"])
            asp_table.add_column("Planets", style=COLORS["sky"])
            asp_table.add_column("Orb", justify="right")
            for a in comp["aspects"][:10]:
                asp_table.add_row(a["aspect"], f"{a['planet1']} — {a['planet2']}", f"{a['orb']}°")
            console.print(asp_table)
        console.print()

    def daily_brief(self):
        """🆕 One-screen summary of today's sky for Gigi — phone optimized."""
        self.update_sky()
        w = term_width()
        pw = min(w - 4, 58)

        now = datetime.now()
        positions = engine.get_all_planets(self.current_jd)
        moon_phase = engine.get_moon_phase(self.current_jd)

        # Planetary hour
        hour = ph.get_planetary_hour(now, DEFAULT_NATAL["lat"], DEFAULT_NATAL["lon"],
                                     DEFAULT_NATAL["timezone_offset"])

        # Natal transits
        dt = datetime.strptime(f"{DEFAULT_NATAL['date']} {DEFAULT_NATAL['time']}",
                               "%Y-%m-%d %H:%M:%S")
        gigi = engine.get_full_chart(
            dt, DEFAULT_NATAL["lat"], DEFAULT_NATAL["lon"],
            DEFAULT_NATAL["timezone_offset"], name="Gigi"
        )
        trans = engine.transits(gigi, self.current_jd, orb=5.0)
        top_transits = trans["inter_aspects"][:4] if trans["inter_aspects"] else []

        # Lunar mansion
        mansion = lmc.current_mansion(self.current_jd)

        # Build brief text
        lines = [
            f"[{COLORS['gold']}]🪐 Planetary Hour:[/] {hour['symbol']} {hour['planet']} ({hour['metal']})",
            f"[{COLORS['sky']}]🌙 Moon:[/] {moon_phase['phase']} — {moon_phase['illumination']}% illuminated",
            f"[{COLORS['rose']}]🏠 Mansion:[/] {mansion['name']} ({mansion['ruler']})",
            "",
            f"[bold {COLORS['moon']}]Today's Transits for Gigi:[/bold {COLORS['moon']}]",
        ]

        if top_transits:
            for t in top_transits:
                lines.append(f"  [{COLORS['coral']}]✦[/] {t['planet2']} {t['aspect']} natal {t['planet1']} @ {t['orb']}°")
        else:
            lines.append(f"  [dim]Quiet skies — no major transits within 5°.[/dim]")

        lines.extend([
            "",
            f"[{COLORS['azure']}]Current Positions:[/]",
        ])

        for name, p in list(positions.items())[:7]:
            retro = " ℞" if p.get("retrograde") else ""
            lines.append(f"  {p.get('symbol', '')} {name}{retro} → {p['sign']} {p['degree_in_sign']}°")

        brief = Panel(
            "\n".join(lines),
            title="[bold {}]📜 Daily Brief — {}[/bold {}]".format(
                COLORS["gold"], now.strftime("%a %d %b"), COLORS["gold"]),
            subtitle="[dim {}]The stars incline; they do not compel[/dim {}]".format(
                COLORS["sky"], COLORS["sky"]),
            border_style=COLORS["lilac"],
            width=pw,
        )
        console.print(Align.center(brief))
        console.print()

    def _print_chart_table(self, chart: Dict):
        """Helper to print any chart as a table."""
        table = Table(border_style=COLORS["lilac"])
        table.add_column("Planet", style=COLORS["sky"])
        table.add_column("Sign", style=COLORS["rose"])
        table.add_column("House", style=COLORS["coral"])
        table.add_column("Deg", justify="right")

        houses = chart.get("houses", [])
        for name, p in chart.get("planets", {}).items():
            house_num = engine.get_house_for_longitude(p["longitude"], houses) if houses else "-"
            retro = " ℞" if p.get("retrograde") else ""
            table.add_row(
                f"{p.get('symbol', '')} {name}{retro}",
                p["sign"],
                str(house_num),
                str(p["degree_in_sign"])
            )
        console.print(table)
        console.print()

    def run(self):
        while self.running:
            self.show_menu()
            choice = Prompt.ask("Select", choices=["1","2","3","4","5","6","7","8","9","10","11","12","13","14","0","?"], default="1")

            if choice == "1":
                self.live_sky()
            elif choice == "2":
                self.planetary_hours_menu()
            elif choice == "3":
                self.lunar_mansion_menu()
            elif choice == "4":
                self.wafq_menu()
            elif choice == "5":
                self.vedic_menu()
            elif choice == "6":
                self.electional_menu()
            elif choice == "7":
                self.fixed_stars_menu()
            elif choice == "8":
                self.natal_chart()
            elif choice == "9":
                self.companion_chat()
            elif choice == "10":
                self.skyfield_menu()
            elif choice == "11":
                self.synastry_menu()
            elif choice == "12":
                self.profile_vault_menu()
            elif choice == "13":
                self.composite_menu()
            elif choice == "14":
                self.daily_brief()
            elif choice == "0":
                self.running = False
            elif choice == "?":
                console.print("[dim]Each number opens a different chamber of the observatory.[/dim]")

            if self.running and choice not in ("9", "10", "11", "12", "13"):
                Prompt.ask("[dim]Press Enter to continue...[/dim]", default="")
                console.clear()

