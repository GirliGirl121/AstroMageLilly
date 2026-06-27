"""
AstroMage — Lilly-backed core engine.
This wraps the proven lilly engine and adds AstroMage helpers.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, Optional

LILLY_DIR = Path(__file__).resolve().parent.parent
if str(LILLY_DIR) not in sys.path:
    sys.path.insert(0, str(LILLY_DIR))

from astro_calculations import (
    get_live_astro_data,
    get_planet_position,
    calculate_ascendant,
    calculate_aspects,
    calculate_transit_calendar,
    get_lunar_mansion,
    get_planetary_hour,
)


EPHEMERIS_STATUS = "lilly-engine"


class Engine:
    """Single access point for all AstroMage chart operations."""

    def __init__(self, location: str = "Kariega", timezone: str = "Africa/Johannesburg"):
        self.location = location
        self.timezone = timezone

    def live(self) -> Dict[str, Any]:
        return {
            "ephemeris": EPHEMERIS_STATUS,
            "location": self.location,
            "timezone": self.timezone,
            **get_live_astro_data(),
        }

    def planet(self, name: str, date: Optional[str] = None, time: Optional[str] = None) -> Dict[str, Any]:
        return get_planet_position(
            name,
            birth_date=date,
            birth_time=time,
            location=self.location,
            timezone=self.timezone,
        )

    def ascendant(self, birth_date: str, birth_time: str) -> Dict[str, Any]:
        return calculate_ascendant(birth_date, birth_time, self.location, self.timezone)

    def aspects(self) -> Dict[str, Any]:
        data = get_live_astro_data()
        return {
            "ephemeris": EPHEMERIS_STATUS,
            "aspects": calculate_aspects(data.get("planets", {})),
            "planets": data.get("planets", {}),
        }

    def transits(self, natal_chart: Dict[str, Any], days: int = 30) -> Dict[str, Any]:
        transits = calculate_transit_calendar(natal_chart, days=days)
        return {
            "ephemeris": EPHEMERIS_STATUS,
            "days": days,
            "transits": transits,
        }

    def mansion(self) -> Dict[str, Any]:
        return get_lunar_mansion()

    def planetary_hour(self) -> Dict[str, Any]:
        return get_planetary_hour()


_default_engine = Engine()


def live() -> Dict[str, Any]:
    return _default_engine.live()
