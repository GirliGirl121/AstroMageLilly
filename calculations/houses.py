"""AstroMage — House cusp and ascendant calculations via Swiss Ephemeris.

Single source of truth for house systems used in AstroMage.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone, timedelta

import swisseph as swe

swe.set_ephe_path(os.path.expanduser('~/.swisseph'))

SAST = timezone(timedelta(hours=2))

# Default location: Kariega, South Africa
KARIEGA_LAT = -33.7367
KARIEGA_LON = 25.3983


def get_house_cusps(
    birth_date: str,
    birth_time: str,
    lat: float = KARIEGA_LAT,
    lon: float = KARIEGA_LON,
    house_system: str = 'E',  # Equal House
    timezone_name: str = 'Africa/Johannesburg',
) -> dict:
    """Calculate house cusps and ascendant for a given birth time/location.

    Args:
        birth_date: 'YYYY-MM-DD'
        birth_time: 'HH:MM' (24-hour, local)
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees
        house_system: Swiss Ephemeris house system code
                      'E' = Equal House, 'P' = Placidus, 'K' = Koch, etc.
        timezone_name: pytz timezone string

    Returns:
        dict with ascendant, MC, houses, etc.
    """
    import pytz
    tz = pytz.timezone(timezone_name)

    dt_str = f"{birth_date} {birth_time}"
    local_dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M')
    local_dt = tz.localize(local_dt)
    utc_dt = local_dt.astimezone(pytz.UTC)

    jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day,
                    utc_dt.hour + utc_dt.minute/60 + utc_dt.second/3600)

    # Calculate houses
    cusps, ascmc = swe.houses(jd, lat, lon, house_system.encode())

    # ascmc[0] = ASC, ascmc[1] = MC, ascmc[2] = ARMC, ascmc[3] = Vertex
    asc_lon = ascmc[0]
    mc_lon = ascmc[1]
    vertex_lon = ascmc[3] if len(ascmc) > 3 else 0

    # Sign names
    SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo',
             'Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
    GLYPHS = ['♈','♉','♊','♋','♌','♍','♎','♏','♐','♑','♒','♓']

    def _sign_info(lon):
        idx = int(lon / 30) % 12
        return {'sign': SIGNS[idx], 'symbol': GLYPHS[idx],
                'longitude': round(lon, 4), 'degree': round(lon % 30, 4)}

    houses = []
    for i, cusp in enumerate(cusps):
        houses.append({
            'house': i + 1,
            **_sign_info(cusp),
        })

    return {
        'ascendant': _sign_info(asc_lon),
        'midheaven': _sign_info(mc_lon),
        'vertex': _sign_info(vertex_lon),
        'houses': houses,
        'system': house_system,
        'julian_day': jd,
        'location': {'lat': lat, 'lon': lon},
    }


def get_ascendant(
    birth_date: str,
    birth_time: str,
    lat: float = KARIEGA_LAT,
    lon: float = KARIEGA_LON,
    timezone_name: str = 'Africa/Johannesburg',
) -> dict:
    """Quick ascendant-only lookup."""
    result = get_house_cusps(birth_date, birth_time, lat, lon, 'E', timezone_name)
    return result['ascendant']
