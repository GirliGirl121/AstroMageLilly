#!/usr/bin/env python3
# electional.py — Electional Astrology & Talismanic Timing

import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

import swisseph as swe
from config import COLORS, PLANETS
from astro_core import engine

console = Console()


class ElectionalPlanner:
    """Find auspicious astrological windows for talismanic work."""
    
    def __init__(self):
        self.favorable_conditions = {
            "Sun": {"signs": ["Leo", "Aries"], "day": "Sunday", "exalted": "Aries"},
            "Moon": {"signs": ["Cancer", "Taurus"], "day": "Monday", "exalted": "Taurus"},
            "Mars": {"signs": ["Aries", "Scorpio"], "day": "Tuesday", "exalted": "Capricorn"},
            "Mercury": {"signs": ["Gemini", "Virgo"], "day": "Wednesday", "exalted": "Virgo"},
            "Jupiter": {"signs": ["Sagittarius", "Pisces"], "day": "Thursday", "exalted": "Cancer"},
            "Venus": {"signs": ["Taurus", "Libra"], "day": "Friday", "exalted": "Pisces"},
            "Saturn": {"signs": ["Capricorn", "Aquarius"], "day": "Saturday", "exalted": "Libra"},
        }
    
    def score_election(self, jd: float, target_planet: str, 
                       purpose: str = "general") -> Dict:
        """Score an election for a specific planet/purpose."""
        positions = engine.get_all_planets(jd)
        moon = positions["Moon"]
        target = positions.get(target_planet, positions["Sun"])
        
        score = 50
        reasons = []
        
        if target["sign"] in self.favorable_conditions.get(target_planet, {}).get("signs", []):
            score += 20
            reasons.append(f"{target_planet} in domicile ({target['sign']})")
        
        if not target["retrograde"]:
            score += 10
            reasons.append(f"{target_planet} direct")
        else:
            score -= 15
            reasons.append(f"{target_planet} retrograde — caution")
        
        moon_lon = moon["longitude"]
        target_lon = target["longitude"]
        diff = abs(((moon_lon - target_lon + 180) % 360) - 180)
        
        if diff < 10:
            score += 15
            reasons.append("Moon conjunct target")
        elif 55 < diff < 65:
            score += 10
            reasons.append("Moon sextile target")
        elif 85 < diff < 95:
            score -= 5
            reasons.append("Moon square target — tension")
        elif 115 < diff < 125:
            score += 15
            reasons.append("Moon trine target — excellent")
        
        sun = positions["Sun"]
        elongation = ((moon_lon - sun["longitude"] + 360) % 360)
        if 120 < elongation < 240:
            score += 10
            reasons.append("Waxing Moon — building energy")
        elif elongation > 240:
            score -= 5
            reasons.append("Waning Moon — releasing phase")
        
        dt = self._jd_to_datetime(jd)
        weekday = dt.strftime("%A")
        favorable_day = self.favorable_conditions.get(target_planet, {}).get("day", "")
        if weekday == favorable_day:
            score += 10
            reasons.append(f"{weekday} — {target_planet}'s day")
        
        score = max(0, min(100, score))
        
        quality = "Excellent" if score >= 80 else "Good" if score >= 60 else \
                  "Fair" if score >= 40 else "Poor" if score >= 20 else "Avoid"
        
        return {
            "score": score,
            "quality": quality,
            "target_planet": target_planet,
            "datetime": dt.strftime("%Y-%m-%d %H:%M"),
            "weekday": weekday,
            "moon_sign": moon["sign"],
            "target_sign": target["sign"],
            "target_retro": target["retrograde"],
            "reasons": reasons,
        }
    
    def _jd_to_datetime(self, jd: float) -> datetime:
        y, m, d, h = swe.revjul(jd)
        hour = int(h)
        minute = int((h - hour) * 60)
        return datetime(int(y), int(m), int(d), hour, minute)
    
    def find_elections(self, start: datetime, end: datetime, 
                       target_planet: str, interval_hours: int = 1) -> List[Dict]:
        """Scan a date range for favorable elections."""
        elections = []
        current = start
        
        while current <= end:
            jd = engine.jd_from_datetime(current, 0)
            election = self.score_election(jd, target_planet)
            elections.append(election)
            current += timedelta(hours=interval_hours)
        
        elections.sort(key=lambda x: x["score"], reverse=True)
        return elections
    
    def print_election(self, election: Dict):
        """Display an election beautifully."""
        color = {
            "Excellent": "bold green", "Good": "green",
            "Fair": "yellow", "Poor": "red", "Avoid": "bold red"
        }.get(election["quality"], "white")
        
        panel = Panel(
            f"[bold {COLORS['sky']}]Date:[/] {election['datetime']} ({election['weekday']})\n"
            f"[bold {COLORS['rose']}]Target:[/] {election['target_planet']} in {election['target_sign']}\n"
            f"[bold {COLORS['moon']}]Moon:[/] in {election['moon_sign']}\n"
            f"[bold {COLORS['coral']}]Score:[/] [{color}]{election['score']}/100 — {election['quality']}[/{color}]\n\n"
            f"[dim]Reasons:[/dim]\n" + "\n".join(f"  • {r}" for r in election['reasons']),
            title=f"[bold {COLORS['gold']}]✨ Electional Window[/bold {COLORS['gold']}]",
            border_style=COLORS["lilac"],
        )
        console.print(panel)


planner = ElectionalPlanner()
