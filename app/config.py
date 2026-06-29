"""AstroMage — shared configuration, constants, and helper functions."""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

import swisseph as swe

# ─── Paths ──────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
TZ = timezone(timedelta(hours=2))  # SAST

# ─── Load JSON Data Files ──────────────────────────────────────────────────
def load_json(name: str) -> dict:
    p = ROOT / 'data' / name
    if not p.exists():
        return {}
    with open(p, encoding='utf-8') as f:
        return json.load(f)

MANIONS_DATA = load_json('picatrix_mansions.json')
NAKSHATRA_DATA = load_json('nakshatra_data.json')
TAROT_RAW = load_json('tarot_data.json')
# Build flat cards list from major_arcana + minor_arcana suits
_TAROT_CARDS = list(TAROT_RAW.get('major_arcana', []))
_minor = TAROT_RAW.get('minor_arcana', {})
for suit in ('wands', 'cups', 'swords', 'pentacles'):
    for card in _minor.get(suit, []):
        card['suit'] = suit
        _TAROT_CARDS.append(card)
TAROT_DATA = {**TAROT_RAW, 'cards': _TAROT_CARDS}
QH_DATA = load_json('quran_hadith_data.json')

# ─── Nakshatra & Dasha Constants ──────────────────────────────────────────
NAKSHATRAS_27 = [
    'Ashwini','Bharani','Krittika','Rohini','Mrigashira','Ardra',
    'Punarvasu','Pushya','Ashlesha','Magha','Purva Phalguni','Uttara Phalguni',
    'Hasta','Chitra','Swati','Vishakha','Anuradha','Jyeshtha',
    'Mula','Purva Ashada','Uttara Ashada','Shravana','Dhanishta','Shatabhisha',
    'Purva Bhadrapada','Uttara Bhadrapada','Revati',
]
NAKSHATRA_LORDS = ['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury'] * 3
DASHA_YEARS_MAP = {'Ketu':7,'Venus':20,'Sun':6,'Moon':10,'Mars':7,'Rahu':18,'Jupiter':16,'Saturn':19,'Mercury':17}
DASHA_SEQUENCE = ['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury']
SIDEREAL_YEAR = 365.25636

# ─── Planet Metaphysical Constants ────────────────────────────────────────
PLANET_ENERGY = {
    'Sun':      ('🔥 Fire',   'Vitality, radiance, and sovereign will — time to lead'),
    'Moon':     ('💧 Water',  'Emotion, intuition, and deep feeling — go inward'),
    'Mercury':  ('🌬 Air',    'Thought, movement, and exchange — speak and connect'),
    'Venus':    ('💧 Water',  'Beauty, love, and harmony — soften and receive'),
    'Mars':     ('🔥 Fire',   'Drive, courage, and assertion — act with purpose'),
    'Jupiter':  ('🌬 Air',    'Expansion, wisdom, and fortune — grow and trust'),
    'Saturn':   ('🌍 Earth',  'Discipline, structure, and karma — build what endures'),
    'Uranus':   ('🌬 Air',    'Awakening, rebellion, and sudden change — break the mold'),
    'Neptune':  ('💧 Water',  'Dreams, illusion, and transcendence — let the veil thin'),
    'Pluto':    ('🔥 Fire',   'Transformation, power, and deep rebirth — shed what no longer serves'),
}
PLANET_SYMBOLS = {'Sun':'☉','Moon':'☽','Mercury':'☿','Venus':'♀','Mars':'♂','Jupiter':'♃','Saturn':'♄','Uranus':'♅','Neptune':'♆','Pluto':'♇',
    'Chiron':'⚷','Lilith':'⚸','Rahu':'☊','Ketu':'☋','Part of Fortune':'⊕','Part of Spirit':'Ⲯ'}
PLANET_COLORS = {'Sun':'#ffd166','Moon':'#c0c0ff','Mercury':'#b0b0b0','Venus':'#ff9ec4','Mars':'#ff3b5c','Jupiter':'#ffa500','Saturn':'#d4b86a','Uranus':'#00cfff','Neptune':'#4444ff','Pluto':'#a020f0',
    'Chiron':'#77dd77','Lilith':'#cc44bb','Rahu':'#ff8844','Ketu':'#8844ff','Part of Fortune':'#88ddff','Part of Spirit':'#ffdd88'}

SIGNS = [
    ('Aries','♈','🔥 Fire','Cardinal'), ('Taurus','♉','🌍 Earth','Fixed'),
    ('Gemini','♊','🌬 Air','Mutable'), ('Cancer','♋','💧 Water','Cardinal'),
    ('Leo','♌','🔥 Fire','Fixed'), ('Virgo','♍','🌍 Earth','Mutable'),
    ('Libra','♎','🌬 Air','Cardinal'), ('Scorpio','♏','💧 Water','Fixed'),
    ('Sagittarius','♐','🔥 Fire','Mutable'), ('Capricorn','♑','🌍 Earth','Cardinal'),
    ('Aquarius','♒','🌬 Air','Fixed'), ('Pisces','♓','💧 Water','Mutable'),
]

# ─── Helper Functions ─────────────────────────────────────────────────────

def get_sign_info(longitude: float) -> dict:
    deg = longitude % 360
    sign_idx = int(deg / 30)
    deg_in_sign = deg % 30
    sign_name, sym, elem, qual = SIGNS[sign_idx]
    return {
        'sign': sign_name, 'symbol': sym, 'element': elem,
        'quality': qual, 'degree': f"{int(deg_in_sign)}°{int((deg_in_sign%1)*60):02d}'",
        'longitude': round(deg, 2),
    }

def get_moon_phase_obj() -> dict:
    """Calculate moon phase from current Swiss Ephemeris data."""
    utc = datetime.now(TZ).astimezone(timezone.utc)
    jd = swe.julday(utc.year, utc.month, utc.day, utc.hour + utc.minute/60 + utc.second/3600)
    sun_pos = swe.calc_ut(jd, swe.SUN)[0][0]
    moon_pos = swe.calc_ut(jd, swe.MOON)[0][0]
    angle = (moon_pos - sun_pos) % 360
    pv = angle / 360.0
    if pv < 0.025 or pv > 0.975: phase, emoji = 'New Moon', '🌑'
    elif pv < 0.25: phase, emoji = 'Waxing Crescent', '🌒'
    elif pv < 0.275: phase, emoji = 'First Quarter', '🌓'
    elif pv < 0.475: phase, emoji = 'Waxing Gibbous', '🌔'
    elif pv < 0.525: phase, emoji = 'Full Moon', '🌕'
    elif pv < 0.725: phase, emoji = 'Waning Gibbous', '🌖'
    elif pv < 0.775: phase, emoji = 'Last Quarter', '🌗'
    else: phase, emoji = 'Waning Crescent', '🌘'
    return {'phase': phase, 'phase_value': round(pv, 4), 'emoji': emoji, 'angle': round(angle, 2)}

def get_current_hour(data: dict) -> Optional[dict]:
    """Find the currently active planetary hour."""
    from calendar_engine import get_day_data
    hours = data.get('planetary_hours', [])
    now = datetime.now(TZ)
    utc = now.astimezone(timezone.utc)
    jd = swe.julday(utc.year, utc.month, utc.day, utc.hour + utc.minute/60 + utc.second/3600)
    if hours:
        for h in hours:
            if h['start_jd'] <= jd < h['end_jd']:
                return h
    # Check surrounding days for boundary edge-cases
    for offset in [-1, 1]:
        other = (now + timedelta(days=offset)).strftime('%Y-%m-%d')
        o_data = get_day_data(other)
        for h in o_data.get('planetary_hours', []):
            if h.get('period') == 'night' and h['start_jd'] <= jd < h['end_jd']:
                return h
    return None

def calc_planet_pos(jd: float, swe_id: int, name: str) -> dict | None:
    """Calculate a planet's position using Swiss Ephemeris."""
    try:
        pos = swe.calc_ut(jd, swe_id)
        lon = pos[0][0]
        lat = pos[0][1]
        dist = pos[0][2]
        speed = pos[0][3]
        sign_info = get_sign_info(lon)
        return {
            'name': name, 'longitude': round(lon, 6), 'latitude': round(lat, 6),
            'distance': round(dist, 6), 'speed': round(speed, 6),
            'sign': sign_info['sign'], 'symbol': sign_info['symbol'],
            'element': sign_info['element'], 'quality': sign_info['quality'],
            'degree': sign_info['degree'], 'retrograde': speed < 0,
        }
    except swe.Error:
        return None
