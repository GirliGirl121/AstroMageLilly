#!/usr/bin/env python3
# vedic.py — Jyotish Calculations

import math
from typing import Dict, List, Tuple
from rich.console import Console
from rich.table import Table

from config import NAKSHATRAS, LAHIRI_AYANAMSHA_2026, COLORS
from astro_core import engine, SIGNS

console = Console()


class VedicEngine:
    """Vedic astrology calculations using Lahiri Ayanamsha."""
    
    def __init__(self, ayanamsha: float = LAHIRI_AYANAMSHA_2026):
        self.ayanamsha = ayanamsha
    
    def tropical_to_sidereal(self, tropical_lon: float) -> float:
        """Convert tropical longitude to sidereal (Lahiri)."""
        sidereal = (tropical_lon - self.ayanamsha) % 360
        return sidereal
    
    def get_nakshatra(self, sidereal_lon: float) -> Dict:
        """Find Nakshatra for a given sidereal longitude."""
        lon = sidereal_lon % 360
        
        for i, nak in enumerate(NAKSHATRAS):
            start = nak["deg"]
            end = NAKSHATRAS[(i + 1) % 27]["deg"]
            if end < start:
                end += 360
            
            if start <= lon < end or (start <= lon + 360 < end):
                pada = int(((lon - start) % 360) / 3.333) + 1
                return {
                    "number": i + 1,
                    "name": nak["name"],
                    "lord": nak["lord"],
                    "pada": min(pada, 4),
                    "degree_start": round(start, 2),
                    "degree_in_nakshatra": round((lon - start) % 360, 2),
                }
        
        return NAKSHATRAS[0]
    
    def get_rashi(self, sidereal_lon: float) -> Dict:
        """Get sidereal sign (Rashi)."""
        lon = sidereal_lon % 360
        sign_idx = int(lon / 30) % 12
        sign_names = [
            "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
            "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena"
        ]
        return {
            "name": sign_names[sign_idx],
            "number": sign_idx + 1,
            "lord": self._rashi_lord(sign_idx),
            "degree_in_sign": round(lon % 30, 2),
        }
    
    def _rashi_lord(self, sign_idx: int) -> str:
        """Get lord of a sidereal sign."""
        lords = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
                 "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]
        return lords[sign_idx]
    
    def calculate_navamsa(self, sidereal_lon: float) -> Dict:
        """Calculate Navamsa (D9) position."""
        lon = sidereal_lon % 360
        sign_idx = int(lon / 30)
        deg_in_sign = lon % 30
        
        navamsa_sign_idx = (sign_idx * 9 + int(deg_in_sign / 3.333)) % 12
        navamsa_deg = (deg_in_sign % 3.333) * 9
        
        sign_names = [
            "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
            "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena"
        ]
        
        return {
            "navamsa_sign": sign_names[navamsa_sign_idx],
            "navamsa_degree": round(navamsa_deg, 2),
            "navamsa_number": navamsa_sign_idx + 1,
        }
    
    def full_vedic_chart(self, jd: float, lat: float, lon: float) -> Dict:
        """Generate complete Vedic chart data."""
        tropical = engine.get_all_planets(jd)
        vedic_data = {}
        
        for planet_name, pos in tropical.items():
            sidereal_lon = self.tropical_to_sidereal(pos["longitude"])
            nakshatra = self.get_nakshatra(sidereal_lon)
            rashi = self.get_rashi(sidereal_lon)
            navamsa = self.calculate_navamsa(sidereal_lon)
            
            vedic_data[planet_name] = {
                "tropical": pos,
                "sidereal_longitude": round(sidereal_lon, 4),
                "nakshatra": nakshatra,
                "rashi": rashi,
                "navamsa": navamsa,
            }
        
        return vedic_data
    
    def print_vedic_table(self, vedic_data: Dict):
        """Display Vedic positions in a formatted table."""
        table = Table(
            title=f"[bold {COLORS['moon']}]🕉️  Vedic Chart (Lahiri Ayanamsha)[/bold {COLORS['moon']}]",
            border_style=COLORS["lilac"],
        )
        table.add_column("Planet", style=COLORS["sky"])
        table.add_column("Nakshatra", style=COLORS["rose"])
        table.add_column("Pada", justify="center", style=COLORS["coral"])
        table.add_column("Rashi", style=COLORS["azure"])
        table.add_column("Navamsa", style=COLORS["gold"])
        table.add_column("Retro", justify="center", style="dim")
        
        for planet, data in vedic_data.items():
            if planet in ["North Node", "South Node", "Lilith"]:
                continue
            nak = data["nakshatra"]
            nav = data["navamsa"]
            retro = "℞" if data["tropical"]["retrograde"] else ""
            
            table.add_row(
                f"{data['tropical']['symbol']} {planet}",
                f"{nak['name']} ({nak['lord']})",
                str(nak["pada"]),
                data["rashi"]["name"],
                nav["navamsa_sign"],
                retro,
            )
        
        console.print(table)


vedic = VedicEngine()
