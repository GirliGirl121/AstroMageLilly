#!/usr/bin/env python3
# dashboard.py — The Observatory Control Panel

import os
import sys
from datetime import datetime, timedelta
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.align import Align
from rich.prompt import Prompt
from rich.text import Text

from config import COLORS, DEFAULT_NATAL
from astro_core import engine
from planetary_hours import ph
from lunar_mansions import lmc
from wafq import wafq
from vedic import vedic
from electional import planner
from fixed_stars import scanner
from companion import companion

console = Console()


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
        menu = Panel(
            f"[bold {c['moon']}]🌙  L I L L Y  —  M A I N  M E N U[/bold {c['moon']}]\n\n"
            f"[{c['rose']}]1[/]  Live Sky & Transits\n"
            f"[{c['sky']}]2[/]  Planetary Hours\n"
            f"[{c['coral']}]3[/]  Lunar Mansion\n"
            f"[{c['azure']}]4[/]  Magic Squares (Wafq)\n"
            f"[{c['lilac']}]5[/]  Vedic Chart (Jyotish)\n"
            f"[{c['gold']}]6[/]  Electional Planner\n"
            f"[{c['rose']}]7[/]  Fixed Star Scan\n"
            f"[{c['sky']}]8[/]  Gigi's Natal Chart\n"
            f"[{c['coral']}]9[/]  Companion Chat\n"
            f"[{c['moon']}]0[/]  Exit Observatory\n\n"
            "[dim]Enter a number to select...[/dim]",
            border_style=COLORS["lilac"],
            width=50,
        )
        console.print(Align.center(menu))
    
    def live_sky(self):
        self.update_sky()
        positions = engine.get_all_planets(self.current_jd)
        moon_phase = engine.get_moon_phase(self.current_jd)
        
        table = Table(title=f"[bold {COLORS['sky']}]🪐 Live Sky[/bold {COLORS['sky']}]",
                      border_style=COLORS["lilac"])
        table.add_column("Planet", style=COLORS["gold"])
        table.add_column("Sign", style=COLORS["rose"])
        table.add_column("Deg", justify="right", style=COLORS["coral"])
        table.add_column("R", justify="center", style="dim")
        table.add_column("Element", style=COLORS["azure"])
        
        for name, p in positions.items():
            if name in ["North Node", "Chiron"]:
                continue
            retro = "℞" if p["retrograde"] else ""
            table.add_row(
                f"{p['symbol']} {name}",
                p["sign"],
                str(p["degree_in_sign"]),
                retro,
                p["element"]
            )
        
        console.print(table)
        console.print(f"\n[bold {COLORS['moon']}]🌙 Moon Phase:[/] {moon_phase['phase']} — "
                      f"{moon_phase['illumination']}% illuminated, age {moon_phase['age']} days")
        console.print()
    
    def planetary_hours_menu(self):
        self.update_sky()
        now = datetime.now()
        hour = ph.get_planetary_hour(now, DEFAULT_NATAL["lat"], DEFAULT_NATAL["lon"], 
                                      DEFAULT_NATAL["timezone_offset"])
        
        panel = Panel(
            f"[bold {COLORS['gold']}]{hour['symbol']} {hour['planet']}[/bold {COLORS['gold']}]\n"
            f"[{COLORS['sky']}]Hour {hour['hour_number']} of the {'Day' if hour['is_day'] else 'Night'}[/]\n"
            f"[{COLORS['rose']}]Metal:[/] {hour['metal']}\n"
            f"[{COLORS['coral']}]Angel:[/] {hour['angel']}\n"
            f"[dim]Hour ends at {hour['hour_end']}[/dim]",
            title=f"[bold {COLORS['moon']}]Current Planetary Hour[/bold {COLORS['moon']}]",
            border_style=COLORS["lilac"],
        )
        console.print(panel)
        console.print()
    
    def lunar_mansion_menu(self):
        self.update_sky()
        mansion = lmc.current_mansion(self.current_jd)
        
        panel = Panel(
            f"[bold {COLORS['gold']}]{mansion['number']}. {mansion['name']}[/bold {COLORS['gold']}]\n"
            f"[{COLORS['sky']}]Arabic:[/] {mansion['arabic']}\n"
            f"[{COLORS['rose']}]Meaning:[/] {mansion['meaning']}\n"
            f"[{COLORS['coral']}]Ruler:[/] {mansion['ruler']}\n"
            f"[{COLORS['azure']}]Moon in:[/] {mansion['moon_sign']}\n\n"
            f"[italic {COLORS['lilac']}]\"{mansion['interpretation']}\"[/italic {COLORS['lilac']}]",
            title=f"[bold {COLORS['moon']}]🌙 Lunar Mansion[/bold {COLORS['moon']}]",
            border_style=COLORS["lilac"],
        )
        console.print(panel)
        console.print()
    
    def wafq_menu(self):
        console.print(f"[bold {COLORS['moon']}]✨ Magic Squares (Wafq)[/bold {COLORS['moon']}]")
        console.print("[dim]Planets and their traditional squares:[/dim]\n")
        
        planets = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
        for p in planets:
            sq = wafq.get_planet_square(p)
            wafq.display_square(sq)
            console.print()
    
    def vedic_menu(self):
        self.update_sky()
        console.print(f"[bold {COLORS['sky']}]Calculating sidereal positions...[/bold {COLORS['sky']}]")
        vedic_data = vedic.full_vedic_chart(
            self.current_jd, DEFAULT_NATAL["lat"], DEFAULT_NATAL["lon"])
        vedic.print_vedic_table(vedic_data)
        console.print()
    
    def electional_menu(self):
        self.update_sky()
        now = datetime.now()
        end = now + timedelta(days=3)
        
        console.print(f"[bold {COLORS['gold']}]🔮 Scanning for favorable windows...[/bold {COLORS['gold']}]")
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
        console.print(f"[bold {COLORS['gold']}]⭐ Scanning royal stars...[/bold {COLORS['gold']}]")
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
        
        console.print(f"[bold {COLORS['rose']}]❤️ Gigi's Natal Chart[/bold {COLORS['rose']}]")
        console.print(f"[dim]{DEFAULT_NATAL['date']} {DEFAULT_NATAL['time']} — {DEFAULT_NATAL['location']}[/dim]\n")
        
        table = Table(border_style=COLORS["lilac"])
        table.add_column("Planet", style=COLORS["sky"])
        table.add_column("Sign", style=COLORS["rose"])
        table.add_column("House", style=COLORS["coral"])
        table.add_column("Deg", justify="right")
        
        for name, p in positions.items():
            if name in ["North Node", "Chiron"]:
                continue
            house_num = 1
            for h in houses:
                if p["longitude"] >= h["cusp"]:
                    house_num = h["house"]
            retro = " ℞" if p["retrograde"] else ""
            table.add_row(
                f"{p['symbol']} {name}{retro}",
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
        console.print(f"[bold {COLORS['moon']}]🌙 Lilly is listening... (type 'back' to return)[/bold {COLORS['moon']}]")
        while True:
            msg = Prompt.ask("[dim]You[/dim]")
            if msg.lower() in ["back", "quit", "exit", "0"]:
                break
            reply = companion.chat(msg, self.current_jd)
            console.print(Panel(reply, border_style=COLORS["lilac"], 
                               title=f"[bold {COLORS['rose']}]Lilly[/bold {COLORS['rose']}]"))
    
    def run(self):
        while self.running:
            self.show_menu()
            choice = Prompt.ask("Select", choices=["1","2","3","4","5","6","7","8","9","0","?"], default="1")
            
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
            elif choice == "0":
                self.running = False
            elif choice == "?":
                console.print("[dim]Each number opens a different chamber of the observatory.[/dim]")
            
            if self.running and choice != "9":
                Prompt.ask("[dim]Press Enter to continue...[/dim]", default="")
                console.clear()
