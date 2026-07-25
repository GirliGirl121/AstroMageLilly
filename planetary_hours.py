#!/usr/bin/env python3
# planetary_hours.py — The Hours of the Planets

import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

import swisseph as swe
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from config import PLANETS, PLANET_SYMBOLS, PLANET_METALS, PLANET_ANGELS, COLORS
from astro_core import engine

console = Console()


class PlanetaryHours:
    """Calculate planetary hours with traditional correspondences."""
    
    PLANET_SEQ = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
    
    def get_sun_times(self, date: datetime, lat: float, lon: float) -> Tuple[datetime, datetime]:
        """Calculate sunrise and sunset for a given date/location."""
        try:
            jd = engine.jd_from_datetime(datetime(date.year, date.month, date.day, 12, 0), 0)
            
            result = swe.rise_trans(
                jd, swe.SUN, lon, lat, 0, 1013.25, 15,
                swe.CALC_RISE | swe.BIT_DISC_CENTER
            )
            sunrise_jd = result[1][0]
            
            result_set = swe.rise_trans(
                jd, swe.SUN, lon, lat, 0, 1013.25, 15,
                swe.CALC_SET | swe.BIT_DISC_CENTER
            )
            sunset_jd = result_set[1][0]
            
            sunrise = self._jd_to_datetime(sunrise_jd)
            sunset = self._jd_to_datetime(sunset_jd)
            return sunrise, sunset
        except Exception:
            noon = datetime(date.year, date.month, date.day, 12, 0)
            return noon.replace(hour=6, minute=0), noon.replace(hour=18, minute=0)
    
    def _jd_to_datetime(self, jd: float) -> datetime:
        """Convert Julian Day to datetime."""
        y, m, d, h = swe.revjul(jd)
        hour = int(h)
        minute = int((h - hour) * 60)
        second = int(((h - hour) * 60 - minute) * 60)
        return datetime(int(y), int(m), int(d), hour, minute, second)
    
    def get_planetary_hour(self, dt: datetime, lat: float, lon: float, 
                          tz_offset: float = 0.0) -> Dict:
        """Determine the current planetary hour."""
        weekday = dt.weekday()
        day_of_week = (weekday + 1) % 7
        
        sunrise, sunset = self.get_sun_times(dt, lat, lon)
        sunrise_local = sunrise + timedelta(hours=tz_offset)
        sunset_local = sunset + timedelta(hours=tz_offset)
        
        day_length = sunset_local - sunrise_local
        day_hour_length = day_length / 12
        
        next_day = dt + timedelta(days=1)
        next_sunrise, _ = self.get_sun_times(next_day, lat, lon)
        next_sunrise_local = next_sunrise + timedelta(hours=tz_offset)
        night_length = next_sunrise_local - sunset_local
        night_hour_length = night_length / 12
        
        if sunrise_local <= dt < sunset_local:
            is_day = True
            elapsed = dt - sunrise_local
            hour_num = int(elapsed / day_hour_length)
            hour_length = day_hour_length
        elif dt >= sunset_local:
            is_day = False
            elapsed = dt - sunset_local
            hour_num = int(elapsed / night_hour_length)
            hour_length = night_hour_length
        else:
            is_day = False
            prev_day = dt - timedelta(days=1)
            prev_sunrise, prev_sunset = self.get_sun_times(prev_day, lat, lon)
            prev_sunset_local = prev_sunset + timedelta(hours=tz_offset)
            elapsed = dt - prev_sunset_local
            hour_num = int(elapsed / night_hour_length)
            hour_length = night_hour_length
        
        day_planet_idx = day_of_week
        if is_day:
            hour_planet_idx = (day_planet_idx + hour_num) % 7
        else:
            night_start_idx = (day_planet_idx + 3) % 7
            hour_planet_idx = (night_start_idx + hour_num) % 7
        
        planet = self.PLANET_SEQ[hour_planet_idx]
        hour_end = (sunrise_local if is_day else sunset_local) + (hour_num + 1) * hour_length
        
        return {
            "planet": planet,
            "symbol": PLANET_SYMBOLS.get(planet, ""),
            "metal": PLANET_METALS.get(planet, ""),
            "angel": PLANET_ANGELS.get(planet, ""),
            "hour_number": hour_num + 1,
            "is_day": is_day,
            "hour_length_minutes": round(hour_length.total_seconds() / 60, 1),
            "current": True,
            "hour_end": hour_end.strftime("%H:%M:%S"),
        }
    
    def get_full_day_hours(self, date: datetime, lat: float, lon: float,
                           tz_offset: float = 0.0) -> List[Dict]:
        """Get all 24 planetary hours for a day."""
        sunrise, sunset = self.get_sun_times(date, lat, lon)
        sunrise_local = sunrise + timedelta(hours=tz_offset)
        sunset_local = sunset + timedelta(hours=tz_offset)
        
        next_day = date + timedelta(days=1)
        next_sunrise, _ = self.get_sun_times(next_day, lat, lon)
        next_sunrise_local = next_sunrise + timedelta(hours=tz_offset)
        
        day_length = sunset_local - sunrise_local
        night_length = next_sunrise_local - sunset_local
        
        day_hour_len = day_length / 12
        night_hour_len = night_length / 12
        
        weekday = date.weekday()
        day_of_week = (weekday + 1) % 7
        day_planet_idx = day_of_week
        
        hours = []
        
        for i in range(12):
            planet_idx = (day_planet_idx + i) % 7
            planet = self.PLANET_SEQ[planet_idx]
            start = sunrise_local + i * day_hour_len
            end = start + day_hour_len
            
            hours.append({
                "hour": i + 1,
                "type": "Day",
                "planet": planet,
                "symbol": PLANET_SYMBOLS.get(planet, ""),
                "metal": PLANET_METALS.get(planet, ""),
                "angel": PLANET_ANGELS.get(planet, ""),
                "start": start.strftime("%H:%M"),
                "end": end.strftime("%H:%M"),
            })
        
        night_start_idx = (day_planet_idx + 3) % 7
        for i in range(12):
            planet_idx = (night_start_idx + i) % 7
            planet = self.PLANET_SEQ[planet_idx]
            start = sunset_local + i * night_hour_len
            end = start + night_hour_len
            
            hours.append({
                "hour": i + 13,
                "type": "Night",
                "planet": planet,
                "symbol": PLANET_SYMBOLS.get(planet, ""),
                "metal": PLANET_METALS.get(planet, ""),
                "angel": PLANET_ANGELS.get(planet, ""),
                "start": start.strftime("%H:%M"),
                "end": end.strftime("%H:%M"),
            })
        
        return hours


ph = PlanetaryHours()
