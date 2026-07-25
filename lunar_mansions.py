#!/usr/bin/env python3
# lunar_mansions.py — Manazil al-Qamar

from typing import Dict, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from config import LUNAR_MANSIONS, COLORS
from astro_core import engine

console = Console()


class LunarMansionCalculator:
    """Calculate and interpret the 28 Lunar Mansions."""
    
    def get_mansion(self, moon_longitude: float) -> Dict:
        """Find which Lunar Mansion the Moon occupies."""
        lon = moon_longitude % 360
        
        for i, mansion in enumerate(LUNAR_MANSIONS):
            start = mansion["deg"]
            end = LUNAR_MANSIONS[(i + 1) % 28]["deg"]
            if end < start:
                end += 360
            
            if start <= lon < end or (start <= lon + 360 < end):
                degree_in_mansion = (lon - start) % 360
                return {
                    "number": i + 1,
                    "name": mansion["name"],
                    "arabic": mansion["arabic"],
                    "meaning": mansion["meaning"],
                    "ruler": mansion["ruler"],
                    "degree_start": round(start, 2),
                    "degree_end": round(end % 360, 2),
                    "degree_in_mansion": round(degree_in_mansion, 2),
                    "moon_longitude": round(lon, 2),
                }
        
        return LUNAR_MANSIONS[0]
    
    def get_mansion_by_number(self, num: int) -> Dict:
        """Get mansion by number (1-28)."""
        if 1 <= num <= 28:
            return LUNAR_MANSIONS[num - 1]
        return LUNAR_MANSIONS[0]
    
    def interpret_mansion(self, mansion: Dict) -> str:
        """Provide traditional interpretation for a mansion."""
        interpretations = {
            "Al-Sharatain": "Beginnings, initiative, planting seeds. Good for starting journeys.",
            "Al-Butain": "Patience, building foundations. Favorable for agriculture and construction.",
            "Al-Thurayya": "Beauty, gathering, community. Excellent for social endeavors and arts.",
            "Al-Dabaran": "Steadfastness, endurance. The Follower brings persistence.",
            "Al-Haqa": "Truth, verification, justice. Good for legal matters and oaths.",
            "Al-Han'a": "Flexibility, adaptation. The Bend teaches us to flow with change.",
            "Al-Dhira": "Action, labor, craftsmanship. The Arm favors manual work and effort.",
            "Al-Nathrah": "Revelation, emergence. The Gap allows hidden things to surface.",
            "Al-Tarf": "Observation, caution. The Glance advises careful watching before acting.",
            "Al-Jabhah": "Recovery, healing. The Forehead brings restoration of health.",
            "Al-Zubrah": "Pride, honor, leadership. The Mane favors authority and dignity.",
            "Al-Sarfah": "Transformation, change. The Changer alters conditions swiftly.",
            "Al-Awwa": "Protection, guardianship. The Barker warns and defends.",
            "Al-Simak": "Harvest, gathering. The Unarmed brings peaceful reaping.",
            "Al-Ghafr": "Concealment, privacy. The Covering shields from harm.",
            "Al-Zubana": "Balance, partnership. The Claws grasp and hold relationships.",
            "Al-Iklil": "Crowning achievement, recognition. The Crown bestows honor.",
            "Al-Qalb": "Courage, inner strength. The Heart is the seat of valor.",
            "Al-Shaulah": "Intensity, penetration. The Sting reaches deep into matters.",
            "Al-Na'aim": "Comfort, ease, prosperity. The Ostriches bring abundance.",
            "Al-Baldah": "Settlement, home. The Town favors establishing roots.",
            "Sa'd al-Dhabih": "Sacrifice, dedication. Luck comes through giving.",
            "Sa'd Bula": "Swallowing pride, acceptance. Luck through humility.",
            "Sa'd al-Su'ud": "Supreme good fortune. The luckiest of all mansions.",
            "Sa'd al-Akhbiyah": "Concealment, hidden treasures. Luck in secret matters.",
            "Al-Fargh al-Muqdim": "Flow, release. The Fore Spout pours forth blessings.",
            "Al-Fargh al-Mu'akhkhar": "Retention, preservation. The Rear Spout holds what is precious.",
            "Al-Risha": "Binding, commitment. The Rope ties agreements and destinies.",
        }
        return interpretations.get(mansion["name"], "A time of celestial significance.")
    
    def current_mansion(self, jd: float) -> Dict:
        """Get current lunar mansion."""
        moon_pos = engine.get_planet_pos("Moon", jd)
        mansion = self.get_mansion(moon_pos["longitude"])
        mansion["interpretation"] = self.interpret_mansion(mansion)
        mansion["moon_sign"] = moon_pos["sign"]
        return mansion


lmc = LunarMansionCalculator()
