"""AstroMage — Swiss Ephemeris planetary positions and utilities.

This module is the SINGLE source of truth for all planetary
position calculations. Every route module that needs current
planet positions must import from here.
"""
from __future__ import annotations

import math
import os
from datetime import datetime, timezone, timedelta

import swisseph as swe

swe.set_ephe_path(os.path.expanduser('~/.swisseph'))

# ─── Constants ──────────────────────────────────────────────────────────

SAST = timezone(timedelta(hours=2))

PLANET_IDS = [
    (swe.SUN, 'Sun'), (swe.MOON, 'Moon'), (swe.MERCURY, 'Mercury'),
    (swe.VENUS, 'Venus'), (swe.MARS, 'Mars'), (swe.JUPITER, 'Jupiter'),
    (swe.SATURN, 'Saturn'), (swe.URANUS, 'Uranus'), (swe.NEPTUNE, 'Neptune'),
    (swe.PLUTO, 'Pluto'), (swe.CHIRON, 'Chiron'),
]

SIGNS_LIST = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo',
              'Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
GLYPHS = ['♈','♉','♊','♋','♌','♍','♎','♏','♐','♑','♒','♓']
ELEMENTS = ['Fire','Earth','Air','Water'] * 3
QUALITIES = ['Cardinal','Fixed','Mutable'] * 4

PLANET_SYMBOLS = {
    'Sun':'☉','Moon':'☽','Mercury':'☿','Venus':'♀','Mars':'♂',
    'Jupiter':'♃','Saturn':'♄','Uranus':'♅','Neptune':'♆','Pluto':'♇',
    'Chiron':'⚷','Rahu':'☊','Ketu':'☋',
}

PLANET_ENERGY = {
    'Sun':     ('🔥 Fire',   'Vitality, radiance, and sovereign will'),
    'Moon':    ('💧 Water',  'Emotion, intuition, and deep feeling'),
    'Mercury': ('🌬 Air',    'Thought, movement, and exchange'),
    'Venus':   ('💧 Water',  'Beauty, love, and harmony'),
    'Mars':    ('🔥 Fire',   'Drive, courage, and assertion'),
    'Jupiter': ('🌬 Air',    'Expansion, wisdom, and fortune'),
    'Saturn':  ('🌍 Earth',  'Discipline, structure, and karma'),
    'Uranus':  ('🌬 Air',    'Awakening, rebellion, and sudden change'),
    'Neptune': ('💧 Water',  'Dreams, illusion, and transcendence'),
    'Pluto':   ('🔥 Fire',   'Transformation, power, and deep rebirth'),
}

NAKSHATRAS_27 = [
    'Ashwini','Bharani','Krittika','Rohini','Mrigashira','Ardra',
    'Punarvasu','Pushya','Ashlesha','Magha','Purva Phalguni','Uttara Phalguni',
    'Hasta','Chitra','Swati','Vishakha','Anuradha','Jyeshtha',
    'Mula','Purva Ashada','Uttara Ashada','Shravana','Dhanishta','Shatabhisha',
    'Purva Bhadrapada','Uttara Bhadrapada','Revati',
]

NAKSHATRA_LORDS = ['Ketu','Venus','Sun','Moon','Mars','Rahu',
                   'Jupiter','Saturn','Mercury'] * 3

DASHA_YEARS = {'Ketu':7,'Venus':20,'Sun':6,'Moon':10,'Mars':7,
               'Rahu':18,'Jupiter':16,'Saturn':19,'Mercury':17}
DASHA_SEQUENCE = ['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury']
SIDEREAL_YEAR = 365.25636


# ─── Core helpers ───────────────────────────────────────────────────────

def get_jd_now() -> float:
    """Current Julian Day Number (UT)."""
    utc = datetime.now(timezone.utc)
    return swe.julday(utc.year, utc.month, utc.day,
                      utc.hour + utc.minute/60 + utc.second/3600)


def get_sign_info(longitude: float) -> dict:
    """Get sign metadata for a given ecliptic longitude."""
    deg = longitude % 360
    sign_idx = int(deg / 30)
    deg_in_sign = deg % 30
    return {
        'sign': SIGNS_LIST[sign_idx],
        'symbol': GLYPHS[sign_idx],
        'element': ELEMENTS[sign_idx],
        'quality': QUALITIES[sign_idx],
        'degree': f"{int(deg_in_sign)}°{int((deg_in_sign%1)*60):02d}'",
        'longitude': round(deg, 2),
    }


def get_planet_positions(jd: float | None = None) -> list[dict]:
    """Get positions for all major planets via Swiss Ephemeris."""
    if jd is None:
        jd = get_jd_now()
    positions = []
    for sid, name in PLANET_IDS:
        try:
            flags = swe.FLG_SWIEPH
            xx, ret = swe.calc_ut(jd, sid, flags)
            lon = xx[0]
            lat = xx[1]
            dist = xx[2]
            speed = xx[3]
        except swe.Error:
            continue
        sign_idx = int(lon / 30) % 12
        retrograde = speed < 0
        positions.append({
            'id': sid,
            'name': name,
            'symbol': PLANET_SYMBOLS.get(name, ''),
            'longitude': round(lon, 4),
            'latitude': round(lat, 4),
            'distance_au': round(dist, 6),
            'speed': round(speed, 4),
            'sign': SIGNS_LIST[sign_idx],
            'sign_symbol': GLYPHS[sign_idx],
            'degree': round(lon % 30, 4),
            'retrograde': retrograde,
        })
    return positions


def get_planet_position_by_name(name: str, jd: float | None = None) -> dict | None:
    """Get a single planet's position by name."""
    planet_map = {n.lower(): sid for sid, n in PLANET_IDS}
    sid = planet_map.get(name.lower())
    if sid is None:
        return None
    if jd is None:
        jd = get_jd_now()
    try:
        xx, ret = swe.calc_ut(jd, sid)
        lon = xx[0]
    except swe.Error:
        return None
    sign_idx = int(lon / 30) % 12
    return {
        'name': name.title(),
        'symbol': PLANET_SYMBOLS.get(name.title(), ''),
        'longitude': round(lon, 4),
        'sign': SIGNS_LIST[sign_idx],
        'sign_symbol': GLYPHS[sign_idx],
        'degree': round(lon % 30, 4),
        'retrograde': xx[3] < 0,
    }


def get_moon_phase() -> dict:
    """Get current moon phase data."""
    jd = get_jd_now()
    sun_lon = swe.calc_ut(jd, swe.SUN)[0][0]
    moon_lon = swe.calc_ut(jd, swe.MOON)[0][0]
    angle = (moon_lon - sun_lon) % 360
    pv = angle / 360.0

    if pv < 0.025 or pv > 0.975:
        phase, emoji = 'New Moon', '🌑'
    elif pv < 0.25:
        phase, emoji = 'Waxing Crescent', '🌒'
    elif pv < 0.275:
        phase, emoji = 'First Quarter', '🌓'
    elif pv < 0.475:
        phase, emoji = 'Waxing Gibbous', '🌔'
    elif pv < 0.525:
        phase, emoji = 'Full Moon', '🌕'
    elif pv < 0.725:
        phase, emoji = 'Waning Gibbous', '🌖'
    elif pv < 0.775:
        phase, emoji = 'Last Quarter', '🌗'
    else:
        phase, emoji = 'Waning Crescent', '🌘'

    return {
        'phase': phase, 'phase_value': round(pv, 4),
        'emoji': emoji, 'angle': round(angle, 2),
        'sun_longitude': round(sun_lon, 4),
        'moon_longitude': round(moon_lon, 4),
    }


def get_current_nakshatra(jd: float | None = None) -> dict:
    """Get the nakshatra the Moon is currently in."""
    if jd is None:
        jd = get_jd_now()
    moon_lon = swe.calc_ut(jd, swe.MOON)[0][0]
    n_idx = int(moon_lon / (360 / 27)) % 27
    pada = int((moon_lon % (360 / 27)) / (360 / 27 / 4)) + 1
    return {
        'nakshatra': NAKSHATRAS_27[n_idx],
        'index': n_idx,
        'pada': pada,
        'lord': NAKSHATRA_LORDS[n_idx],
        'moon_longitude': round(moon_lon, 4),
    }
