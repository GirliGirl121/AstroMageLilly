#!/usr/bin/env python3
# astro_core.py — The Heart of the Heavens

import math
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

import swisseph as swe
from rich.console import Console

from config import (
    EPHE_DIR, CHARTS_FILE, DEFAULT_NATAL,
    PLANETS, PLANET_SYMBOLS
)

console = Console()

swe.set_ephe_path(str(EPHE_DIR))

SWE_PLANETS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY,
    "Venus": swe.VENUS, "Mars": swe.MARS, "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN, "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO, "North Node": swe.MEAN_NODE,
    "South Node": swe.TRUE_NODE,
}

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

SIGN_ELEMENTS = {
    "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
    "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
    "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
    "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water",
}

SIGN_MODALITIES = {
    "Aries": "Cardinal", "Cancer": "Cardinal", "Libra": "Cardinal", "Capricorn": "Cardinal",
    "Taurus": "Fixed", "Leo": "Fixed", "Scorpio": "Fixed", "Aquarius": "Fixed",
    "Gemini": "Mutable", "Virgo": "Mutable", "Sagittarius": "Mutable", "Pisces": "Mutable",
}


class CelestialEngine:
    """Core astronomical and astrological calculations."""
    
    def __init__(self):
        self.swe = swe
    
    def jd_from_datetime(self, dt: datetime, tz_offset: float = 0.0) -> float:
        """Convert datetime to Julian Day."""
        utc_dt = dt - timedelta(hours=tz_offset)
        return swe.julday(utc_dt.year, utc_dt.month, utc_dt.day,
                         utc_dt.hour + utc_dt.minute/60 + utc_dt.second/3600)
    
    def get_planet_pos(self, planet_name: str, jd: float) -> Optional[Dict]:
        """Calculate planet position at given Julian Day."""
        if planet_name not in SWE_PLANETS:
            return None
        
        body = SWE_PLANETS[planet_name]
        try:
            result = swe.calc_ut(jd, body, swe.FLG_EQUATORIAL)
            vals = result[0]
            lon, lat, dist = vals[0], vals[1], vals[2]
            
            sign_idx = int(lon / 30) % 12
            sign = SIGNS[sign_idx]
            degree_in_sign = lon % 30
            
            result_speed = swe.calc_ut(jd, body, swe.FLG_SPEED)
            speed_vals = result_speed[0]
            speed = speed_vals[3] if len(speed_vals) > 3 else 0
            retrograde = speed < 0
            
            return {
                "name": planet_name,
                "symbol": PLANET_SYMBOLS.get(planet_name, ""),
                "longitude": round(lon, 4),
                "latitude": round(lat, 4),
                "distance": round(dist, 6),
                "sign": sign,
                "element": SIGN_ELEMENTS[sign],
                "modality": SIGN_MODALITIES[sign],
                "degree_in_sign": round(degree_in_sign, 2),
                "retrograde": retrograde,
                "speed": round(speed, 6),
            }
        except Exception as e:
            return {
                "name": planet_name,
                "symbol": PLANET_SYMBOLS.get(planet_name, ""),
                "longitude": 0.0,
                "latitude": 0.0,
                "distance": 0.0,
                "sign": "Aries",
                "element": "Fire",
                "modality": "Cardinal",
                "degree_in_sign": 0.0,
                "retrograde": False,
                "speed": 0.0,
                "error": str(e),
            }
    
    def get_all_planets(self, jd: float) -> Dict[str, Dict]:
        """Get positions for all classical + modern planets."""
        planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", 
                   "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto",
                   "North Node"]
        result = {}
        for p in planets:
            pos = self.get_planet_pos(p, jd)
            if pos and "error" not in pos:
                result[p] = pos
        return result
    
    def calculate_houses(self, jd: float, lat: float, lon: float, 
                         hsys: bytes = b'P') -> List[Dict]:
        """Calculate house cusps using Placidus (default) or other systems."""
        try:
            houses = swe.houses_ex(jd, lat, lon, hsys)
            cusps = houses[0]
        except Exception:
            # Fallback to equal houses if Placidus fails at extreme latitudes
            houses = swe.houses_ex(jd, lat, lon, b'E')
            cusps = houses[0]
        
        house_data = []
        for i, cusp in enumerate(cusps[:12], 1):
            sign_idx = int(cusp / 30) % 12
            house_data.append({
                "house": i,
                "cusp": round(cusp, 4),
                "sign": SIGNS[sign_idx],
                "element": SIGN_ELEMENTS[SIGNS[sign_idx]],
                "degree_in_sign": round(cusp % 30, 2),
            })
        return house_data
    
    def calculate_aspects(self, positions: Dict[str, Dict], 
                         orb: float = 8.0) -> List[Dict]:
        """Calculate major aspects between planets."""
        ASPECTS = {
            "Conjunction": 0, "Sextile": 60, "Square": 90,
            "Trine": 120, "Opposition": 180,
        }
        planets = list(positions.keys())
        aspects = []
        
        for i, p1 in enumerate(planets):
            for p2 in planets[i+1:]:
                lon1 = positions[p1]["longitude"]
                lon2 = positions[p2]["longitude"]
                diff = abs(((lon1 - lon2 + 180) % 360) - 180)
                
                for name, angle in ASPECTS.items():
                    orb_val = abs(diff - angle)
                    if orb_val <= orb:
                        aspects.append({
                            "planet1": p1,
                            "planet2": p2,
                            "aspect": name,
                            "angle": round(diff, 2),
                            "orb": round(orb_val, 2),
                            "applying": self._is_applying(positions[p1], positions[p2], angle),
                        })
        return aspects
    
    def _is_applying(self, p1: Dict, p2: Dict, aspect_angle: float) -> bool:
        """Determine if an aspect is applying or separating."""
        speed1 = p1.get("speed", 0)
        speed2 = p2.get("speed", 0)
        lon1 = p1["longitude"]
        lon2 = p2["longitude"]
        
        if speed1 > speed2:
            return ((lon2 - lon1) % 360) < aspect_angle
        return ((lon1 - lon2) % 360) < aspect_angle
    
    def get_moon_phase(self, jd: float) -> Dict:
        """Calculate moon phase and illumination."""
        sun = self.get_planet_pos("Sun", jd)
        moon = self.get_planet_pos("Moon", jd)
        
        if not sun or not moon:
            return {"phase": "Unknown", "illumination": 0, "age": 0, "elongation": 0}
        
        elongation = ((moon["longitude"] - sun["longitude"] + 360) % 360)
        illumination = (1 - math.cos(math.radians(elongation))) / 2
        
        if elongation < 45:
            phase = "New Moon"
        elif elongation < 90:
            phase = "Waxing Crescent"
        elif elongation < 135:
            phase = "First Quarter"
        elif elongation < 180:
            phase = "Waxing Gibbous"
        elif elongation < 225:
            phase = "Full Moon"
        elif elongation < 270:
            phase = "Waning Gibbous"
        elif elongation < 315:
            phase = "Last Quarter"
        else:
            phase = "Waning Crescent"
        
        return {
            "elongation": round(elongation, 2),
            "illumination": round(illumination * 100, 2),
            "phase": phase,
            "age": round(elongation / 360 * 29.53, 2),
        }
    
    def save_chart(self, chart_data: Dict):
        """Save chart to JSON storage."""
        charts = []
        if CHARTS_FILE.exists():
            with open(CHARTS_FILE, 'r') as f:
                charts = json.load(f)
        
        charts.append({
            "saved_at": datetime.now().isoformat(),
            **chart_data
        })
        
        with open(CHARTS_FILE, 'w') as f:
            json.dump(charts, f, indent=2)
    
    def load_charts(self) -> List[Dict]:
        """Load all saved charts."""
        if not CHARTS_FILE.exists():
            return []
        with open(CHARTS_FILE, 'r') as f:
            return json.load(f)


engine = CelestialEngine()
