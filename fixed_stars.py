#!/usr/bin/env python3
# fixed_stars.py — The Royal Behenian Stars

import math
from typing import Dict, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from config import BEHENIAN_STARS, COLORS
from astro_core import engine

console = Console()


class FixedStarScanner:
    """Scan for alignments with Behenian fixed stars."""
    
    def __init__(self, orb: float = 2.0):
        self.orb = orb
    
    def check_alignment(self, planet_lon: float, planet_lat: float = 0,
                        planet_name: str = "Planet") -> List[Dict]:
        """Check which fixed stars align with a planet's position."""
        alignments = []
        
        for star in BEHENIAN_STARS:
            lon_diff = abs(((planet_lon - star["lon"] + 180) % 360) - 180)
            
            if lon_diff <= self.orb:
                alignments.append({
                    "star": star["name"],
                    "planet": planet_name,
                    "separation": round(lon_diff, 2),
                    "orb": self.orb,
                    "nature": star["nature"],
                    "magnitude": star["magnitude"],
                    "royal": star["royal"],
                    "star_longitude": star["lon"],
                    "planet_longitude": round(planet_lon, 2),
                })
        
        return alignments
    
    def scan_natal_chart(self, jd: float) -> List[Dict]:
        """Scan all planets against fixed stars for a chart."""
        positions = engine.get_all_planets(jd)
        all_alignments = []
        
        for planet_name, pos in positions.items():
            if planet_name in ["North Node", "South Node", "Lilith"]:
                continue
            
            alignments = self.check_alignment(
                pos["longitude"], 
                planet_name=planet_name
            )
            all_alignments.extend(alignments)
        
        all_alignments.sort(key=lambda x: x["separation"])
        return all_alignments
    
    def interpret_alignment(self, alignment: Dict) -> str:
        """Provide traditional interpretation."""
        interpretations = {
            "Aldebaran": "Honor, intelligence, eloquence, steadfastness. The Watcher of the East.",
            "Regulus": "Royalty, success, power. The Heart of the Lion — but beware revenge.",
            "Antares": "Obsession, intensity, danger. The Watcher of the West tests the soul.",
            "Formalhaut": "Magic, idealism, fall from grace. The Watcher of the South.",
            "Spica": "Giftedness, harvest, artistic talent. The Ear of Wheat brings blessings.",
            "Capella": "Curiosity, learning, honor through knowledge.",
            "Sirius": "Wealth, fame, ambition. The Scorcher brings burning brilliance.",
            "Altair": "Courage, risk-taking, sudden fortunes. The Flying Eagle.",
            "Vega": "Artistic talent, charisma, generosity. The Falling Vulture.",
            "Deneb Algedi": "Justice, protection, transformation. The Judge's wisdom.",
        }
        return interpretations.get(alignment["star"], "A significant stellar influence.")
    
    def print_alignments(self, alignments: List[Dict]):
        """Display alignments in a table."""
        if not alignments:
            console.print(f"[dim {COLORS['lilac']}]No close fixed star alignments found.[/]")
            return
        
        table = Table(
            title=f"[bold {COLORS['moon']}]⭐ Behenian Fixed Star Alignments[/bold {COLORS['moon']}]",
            border_style=COLORS["gold"],
        )
        table.add_column("Star", style=COLORS["gold"])
        table.add_column("Planet", style=COLORS["sky"])
        table.add_column("Sep", justify="right", style=COLORS["rose"])
        table.add_column("Nature", style=COLORS["coral"])
        table.add_column("Royal", justify="center", style=COLORS["azure"])
        table.add_column("Interpretation", style="dim")
        
        for a in alignments[:15]:
            royal = "👑" if a["royal"] else ""
            interp = self.interpret_alignment(a)
            table.add_row(
                a["star"],
                f"{engine.get_planet_pos(a['planet'], 0).get('symbol', '')} {a['planet']}",
                f"{a['separation']}°",
                a["nature"],
                royal,
                interp[:50] + "..." if len(interp) > 50 else interp,
            )
        
        console.print(table)


scanner = FixedStarScanner()
