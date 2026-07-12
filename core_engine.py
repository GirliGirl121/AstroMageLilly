"""
AstroMage — Lilly-backed core engine.
Wraps the calculations/ package (Swiss Ephemeris) as the
single source of truth for all astro computations.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

# Import from the new calculations package (Swiss Ephemeris)
from calculations.ephemeris import (
    get_planet_positions,
    get_planet_position_by_name,
    get_moon_phase,
    get_current_nakshatra,
    get_jd_now,
)
from calculations.houses import get_house_cusps, get_ascendant

EPHEMERIS_STATUS = "swisseph"


class Engine:
    """Single access point for all AstroMage chart operations."""

    def __init__(self, location: str = "Kariega", timezone: str = "Africa/Johannesburg"):
        self.location = location
        self.timezone = timezone
        self.lat = -33.7367
        self.lon = 25.3983

    def live(self) -> Dict[str, Any]:
        planets = get_planet_positions()
        moon = get_moon_phase()
        lunar_mansion = get_current_nakshatra()
        # calendar_engine.py lives in the MagiJournal/ subpackage. Make it
        # importable whether core_engine is run from the project root (CLI)
        # or from within the Flask app (where app/__init__.py already adds it).
        import os as _os
        import sys as _sys
        from pathlib import Path as _Path
        _magijournal = str(_Path(__file__).resolve().parent / "MagiJournal")
        if _magijournal not in _sys.path:
            _sys.path.insert(0, _magijournal)
        from calendar_engine import compute_planetary_hours, compute_moon_position
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone(timedelta(hours=2)))
        hours_data, sr_jd, ss_jd, nsr_jd = compute_planetary_hours(now)
        # Find the current hour from the list
        current_hour = {}
        if hours_data:
            for h in hours_data:
                if h['start_jd'] <= get_jd_now() <= h['end_jd']:
                    current_hour = h
                    break
            if not current_hour and hours_data:
                current_hour = hours_data[0]
        hour = {
            'planet': current_hour.get('planet', ''),
            'planet_ar': current_hour.get('planet_ar', ''),
            'spirit': current_hour.get('spirit_name', ''),
            'spirit_angel': current_hour.get('spirit_angel', ''),
            'hour': now.hour,
            'minute': now.minute,
            'time': now.strftime('%H:%M'),
            'system': "Chaldean planetary hours (sunrise-based unequal hours); spirit names from Picatrix Book II",
        }

        return {
            "ephemeris": EPHEMERIS_STATUS,
            "location": self.location,
            "timezone": self.timezone,
            "timestamp": __import__('datetime').datetime.now().strftime('%Y-%m-%d %I:%M:%S %p'),
            "lunar_mansion": {"name": lunar_mansion.get('nakshatra', '')},
            "planetary_hour": hour,
            "planets": {p['name']: p for p in planets},
        }

    def planet(self, name: str, date: Optional[str] = None, time: Optional[str] = None) -> Dict[str, Any]:
        jd = get_jd_now()
        result = get_planet_position_by_name(name, jd)
        return result or {}

    def ascendant(self, birth_date: str, birth_time: str) -> Dict[str, Any]:
        return get_ascendant(birth_date, birth_time, self.lat, self.lon, self.timezone)

    def aspects(self) -> Dict[str, Any]:
        planets = get_planet_positions()
        from calculations.aspects import calculate_aspects
        return {
            "ephemeris": EPHEMERIS_STATUS,
            "aspects": calculate_aspects({p['name']: p for p in planets}),
        }

    def transit_calendar(self, days: int = 30, natal_planets: Optional[dict] = None) -> list:
        from calculations.transits import get_transit_calendar
        return get_transit_calendar(days=days, natal_planets=natal_planets)

    def houses(self, birth_date: str, birth_time: str) -> Dict[str, Any]:
        return get_house_cusps(birth_date, birth_time, self.lat, self.lon, 'E', self.timezone)

    def nakshatra(self) -> Dict[str, Any]:
        return get_current_nakshatra()

    def moon_phase(self) -> Dict[str, Any]:
        return get_moon_phase()
