#!/usr/bin/env python3
"""
AstroMage Dashboard v5.0 — Islamic Astrology & Tarot Hub
For Gigi ❤️ — You are stardust, you are magic, you are limitless.
"""
from __future__ import annotations

import json
import math
import os
import random
import sys
from datetime import datetime, date, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

from flask import Flask, jsonify, make_response, render_template, request
import swisseph as swe
swe.set_ephe_path(os.path.expanduser('~/.swisseph'))
from web_diary_db import get_diary_db

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'MagiJournal'))

from calendar_engine import get_day_data, PICATRIX_SPIRITS
from astro_calculations import (
    get_live_astro_data,
    get_lunar_mansion,
    get_planetary_hour,
)

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config['TEMPLATES_AUTO_RELOAD'] = True
TZ = timezone(timedelta(hours=2))  # SAST

# ─── Load Data Files ─────────────────────────────────────────────────────
def _load_json(name: str) -> dict:
    p = ROOT / name
    if not p.exists():
        return {}
    with open(p, encoding='utf-8') as f:
        return json.load(f)

MANIONS_DATA = _load_json('picatrix_mansions.json')
NAKSHATRA_DATA = _load_json('nakshatra_data.json')
TAROT_DATA = _load_json('tarot_data.json')
QH_DATA = _load_json('quran_hadith_data.json')

# ─── Constants ────────────────────────────────────────────────────────────
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

# ─── Helpers ─────────────────────────────────────────────────────────────

def _get_sign_info(longitude: float) -> dict:
    deg = longitude % 360
    sign_idx = int(deg / 30)
    deg_in_sign = deg % 30
    sign_name, sym, elem, qual = SIGNS[sign_idx]
    return {
        'sign': sign_name, 'symbol': sym, 'element': elem,
        'quality': qual, 'degree': f"{int(deg_in_sign)}°{int((deg_in_sign%1)*60):02d}'",
        'longitude': round(deg, 2),
    }

def _get_current_hour(data: dict) -> Optional[dict]:
    hours = data.get('planetary_hours', [])
    now = datetime.now(TZ)
    utc = now.astimezone(timezone.utc)
    jd = swe.julday(utc.year, utc.month, utc.day, utc.hour + utc.minute/60 + utc.second/3600)
    if hours:
        for h in hours:
            if h['start_jd'] <= jd < h['end_jd']:
                return h
    # Night hours from yesterday may extend past midnight into early morning
    yesterday = (now - timedelta(days=1)).strftime('%Y-%m-%d')
    ydata = get_day_data(yesterday)
    yhours = ydata.get('planetary_hours', [])
    for h in yhours:
        if h.get('period') == 'night' and h['start_jd'] <= jd < h['end_jd']:
            return h
    # Also check tomorrow's early hours in case of boundary edge-case
    tomorrow = (now + timedelta(days=1)).strftime('%Y-%m-%d')
    tdata = get_day_data(tomorrow)
    for h in tdata.get('planetary_hours', []):
        if h.get('period') == 'night' and h['start_jd'] <= jd < h['end_jd']:
            return h
    return None

def _get_moon_phase() -> dict:
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

# ─── Vimshottari Dasha Calculator ─────────────────────────────────────

def _calc_dasha(birth_year=1981, birth_month=10, birth_day=30,
                birth_hour=3, birth_min=6, tz_offset=2):
    """Calculate current Vimshottari Dasha based on birth Moon nakshatra."""
    # Birth in UTC
    jd_birth = swe.julday(birth_year, birth_month, birth_day,
                          birth_hour - tz_offset + birth_min/60)
    moon = swe.calc_ut(jd_birth, swe.MOON)[0][0]
    nak_idx = int(moon // 13.333333333333334)
    start_lord = NAKSHATRA_LORDS[nak_idx]
    start_lord_idx = DASHA_SEQUENCE.index(start_lord)

    # Remaining portion of first dasha
    elapsed_pct = (moon % 13.333333333333334) / 13.333333333333334
    rem_pct = 1 - elapsed_pct

    # Build timeline
    from datetime import datetime as dt, timedelta, timezone
    birth_dt = dt(birth_year, birth_month, birth_day, birth_hour, birth_min, tzinfo=TZ)

    dashas = []
    cur = birth_dt

    first_yrs = DASHA_YEARS_MAP[start_lord] * rem_pct
    first_end = cur + timedelta(days=first_yrs * SIDEREAL_YEAR)
    dashas.append({'lord': start_lord, 'years': round(DASHA_YEARS_MAP[start_lord], 1),
                   'remaining_at_birth': round(rem_pct * DASHA_YEARS_MAP[start_lord], 4),
                   'start': birth_dt.isoformat(), 'end': first_end.isoformat(),
                   'type': 'first (balance)'})
    cur = first_end

    for i in range(1, 9):
        idx = (start_lord_idx + i) % 9
        lord = DASHA_SEQUENCE[idx]
        yrs = DASHA_YEARS_MAP[lord]
        end = cur + timedelta(days=yrs * SIDEREAL_YEAR)
        dashas.append({'lord': lord, 'years': yrs,
                       'start': cur.isoformat(), 'end': end.isoformat(),
                       'type': 'full'})
        cur = end

    # Find current dasha
    now = datetime.now(TZ)
    current_dasha = None
    current_bhukti = None
    for i, d in enumerate(dashas):
        d_start = dt.fromisoformat(d['start'])
        d_end = dt.fromisoformat(d['end'])
        if d_start <= now < d_end:
            current_dasha = d
            current_dasha['index'] = i
            # Calculate bhukti (sub-period)
            maha_yrs = d['years']
            d_total_days = (d_end - d_start).days
            d_elapsed = (now - d_start).total_seconds() / 86400
            d_elapsed_pct = d_elapsed / d_total_days if d_total_days > 0 else 0

            # Bhuktis within this Mahadasha
            start_idx = DASHA_SEQUENCE.index(d['lord'])
            bhuktis = []
            bhukti_cur = d_start
            for bi in range(9):
                bl_idx = (start_idx + bi) % 9
                bl = DASHA_SEQUENCE[bl_idx]
                byrs = (maha_yrs * DASHA_YEARS_MAP[bl]) / 120.0  # proportion of 120yr cycle
                bhukti_end = bhukti_cur + timedelta(days=byrs * SIDEREAL_YEAR)
                active = bhukti_cur <= now < bhukti_end
                bhuktis.append({
                    'lord': bl, 'years': round(byrs, 3),
                    'start': bhukti_cur.isoformat(), 'end': bhukti_end.isoformat(),
                    'active': active
                })
                if active:
                    current_bhukti = bhuktis[-1]
                bhukti_cur = bhukti_end
            current_dasha['bhuktis'] = bhuktis
            break

    return {
        'birth_nakshatra': NAKSHATRAS_27[nak_idx],
        'birth_nakshatra_lord': start_lord,
        'current_dasha': current_dasha,
        'current_bhukti': current_bhukti,
        'moon_longitude': round(moon, 4),
        'dashas': dashas,
    }

# ─── Get current nakshatra from transit Moon ──────────────────────────

def _current_nakshatra() -> dict:
    utc = datetime.now(TZ).astimezone(timezone.utc)
    jd = swe.julday(utc.year, utc.month, utc.day, utc.hour + utc.minute/60 + utc.second/3600)
    moon = swe.calc_ut(jd, swe.MOON)[0][0]
    nak_idx = int(moon // 13.333333333333334)
    nak_pada = int((moon % 13.333333333333334) // 3.3333333333333335)
    lord = NAKSHATRA_LORDS[nak_idx]

    result = {
        'nakshatra': NAKSHATRAS_27[nak_idx],
        'nakshatra_index': nak_idx,
        'pada': nak_pada + 1,
        'lord': lord,
        'moon_longitude': round(moon, 4),
    }

    # Enrich from nakshatra data file if available
    nd = NAKSHATRA_DATA.get('nakshatras', [])
    for n in nd:
        if n.get('name', '').lower() == NAKSHATRAS_27[nak_idx].lower():
            result['sanskrit'] = n.get('sanskrit', '')
            result['meaning'] = n.get('meaning', '')
            result['gana'] = n.get('gana', '')
            result['guna'] = n.get('guna', '')
            result['deity'] = n.get('deity', '')
            result['symbol'] = n.get('symbol', '')
            result['description'] = n.get('description', '')
            break
    return result

# ─── Islamic Astrology Section ────────────────────────────────────────

def _islamic_astro() -> dict:
    """Combined Islamic astrology data: lunar mansion + nakshatra + dasha."""
    utc = datetime.now(TZ).astimezone(timezone.utc)
    jd = swe.julday(utc.year, utc.month, utc.day, utc.hour + utc.minute/60 + utc.second/3600)
    moon = swe.calc_ut(jd, swe.MOON)[0][0]

    # Current lunar mansion (Picatrix: 28 mansions, each ~12.857°)
    mansion_deg = moon % 360
    mansions_list = MANIONS_DATA.get('mansions', [])
    active_mansion = None
    for m in mansions_list:
        # Parse start/end degrees
        # Each mansion has start in degrees like "0° 0' 0" Aries" and "12° 51' 26" Aries"
        try:
            start_str = m['start_degrees']
            end_str = m['end_degrees']
            # Convert to absolute longitude
            def _parse_picatrix_deg(s):
                parts = s.replace('°', '').replace("'", '').replace('"', '').split()
                deg = float(parts[0])
                minutes = float(parts[1]) if len(parts) > 1 else 0
                secs = float(parts[2]) if len(parts) > 2 else 0
                sign_name = ' '.join(parts[3:]) if len(parts) > 3 else parts[3] if len(parts) > 3 else 'Aries'
                sign_abbr = sign_name[:3].title()
                sign_offsets = {'Ari':0,'Tau':30,'Gem':60,'Can':90,'Leo':120,'Vir':150,
                               'Lib':180,'Sco':210,'Sag':240,'Cap':270,'Aqu':300,'Pis':330}
                return sign_offsets.get(sign_abbr, 0) + deg + minutes/60 + secs/3600

            start_abs = _parse_picatrix_deg(start_str)
            end_abs = _parse_picatrix_deg(end_str)
            if start_abs <= mansion_deg < end_abs:
                active_mansion = m
                break
        except (KeyError, IndexError, ValueError):
            # Fallback: use index
            idx = int(mansion_deg // 12.857142857)
            if 0 <= idx < len(mansions_list) and mansions_list[idx].get('number') == m.get('number'):
                active_mansion = m
                continue

    if not active_mansion and mansions_list:
        idx = int(mansion_deg // 12.857142857)
        if idx < len(mansions_list):
            active_mansion = mansions_list[idx]

    # Build result
    result = {}

    if active_mansion:
        # Determine benefic/malefic from nature
        nature = active_mansion.get('nature', '').lower()
        if 'hot' in nature and 'dry' in nature:
            benefic = 'Mars-ruled: Active, assertive — potent for war, protection, and confrontation'
            malefic = 'Avoid peace negotiations, marriage, or calm endeavors. Energy is combative.'
        elif 'cold' in nature and 'moist' in nature:
            benefic = 'Moon-ruled: Nurturing, receptive — good for healing, planting, emotional work'
            malefic = 'Avoid start of bold ventures or confrontations. Energy is passive.'
        elif 'cold' in nature and 'dry' in nature:
            benefic = 'Saturn-ruled: Structured, enduring — good for building, discipline, long-term planning'
            malefic = 'Avoid celebration, expansion, or social events. Energy is constrictive.'
        elif 'air' in nature or 'mercurial' in nature:
            benefic = 'Mercurial: Intellectual, communicative — good for learning, trade, writing'
            malefic = 'Avoid emotional decisions or commitments. Energy is changeable.'
        else:
            benefic = 'Balanced — moderately favorable for general activities'
            malefic = 'Avoid extreme undertakings. Middle path is best.'

        result['mansion'] = {
            'number': active_mansion.get('number'),
            'picatrix_name': active_mansion.get('picatrix_name'),
            'arabic_name': active_mansion.get('arabic_name'),
            'transliteration': active_mansion.get('arabic_transliteration'),
            'meaning': active_mansion.get('meaning'),
            'nature': active_mansion.get('nature'),
            'planetary_ruler': active_mansion.get('planetary_ruler'),
            'spirit': active_mansion.get('lord_of_mansion_spirit'),
            'benefic': benefic,
            'malefic': malefic,
            'best_activities': active_mansion.get('recommended_works', [])[:5],
            'avoid_activities': [active_mansion.get('forbidden_works', 'No specific prohibitions')],
        }

    # Current nakshatra
    result['nakshatra'] = _current_nakshatra()

    # Dasha
    result['dasha'] = _calc_dasha()

    # Moon phase
    result['moon_phase'] = _get_moon_phase()

    # Day ruler
    day_names = ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']
    result['day_ruler'] = day_names[datetime.now(TZ).weekday()]

    return result

# ─── Energy & Polarities ─────────────────────────────────────────────

def _energy_polarities() -> dict:
    utc = datetime.now(TZ).astimezone(timezone.utc)
    jd = swe.julday(utc.year, utc.month, utc.day, utc.hour + utc.minute/60 + utc.second/3600)

    # Get key planets
    sun = swe.calc_ut(jd, swe.SUN)[0][0]
    moon = swe.calc_ut(jd, swe.MOON)[0][0]
    mars = swe.calc_ut(jd, swe.MARS)[0][0]
    venus = swe.calc_ut(jd, swe.VENUS)[0][0]

    sun_s = _get_sign_info(sun)
    moon_s = _get_sign_info(moon)
    mars_s = _get_sign_info(mars)
    venus_s = _get_sign_info(venus)

    # Elemental balance
    elem_count = {}
    for p in [sun_s, moon_s, mars_s, venus_s]:
        e = p['element'].split()[1] if ' ' in p['element'] else p['element']
        elem_count[e] = elem_count.get(e, 0) + 1

    dominant_elem = max(elem_count, key=elem_count.get) if elem_count else 'Fire'
    weak_elem = min(elem_count, key=elem_count.get) if elem_count else 'Water'

    elem_meanings = {
        'Fire': '🔥 Fiery — passionate, active, bold. Initiate and lead.',
        'Earth': '🌍 Earthy — grounded, practical, stable. Build and nurture.',
        'Air': '🌬 Airy — intellectual, social, communicative. Connect and learn.',
        'Water': '💧 Watery — emotional, intuitive, receptive. Feel and flow.',
    }

    # Quality balance
    qual_count = {}
    for p in [sun_s, moon_s, mars_s, venus_s]:
        q = p['quality']
        qual_count[q] = qual_count.get(q, 0) + 1

    # Sun-Moon polarity (masculine/feminine)
    sun_is_fire = sun_s['element'].startswith('🔥')
    moon_is_water = moon_s['element'].startswith('💧')
    polarity = 'Yang (masculine, outward, active)' if (sun_is_fire and not moon_is_water) else 'Yin (feminine, inward, receptive)'
    if sun_is_fire and moon_is_water:
        polarity = 'Balance — the sacred marriage of fire and water within ✨'

    return {
        'dominant_element': dominant_elem,
        'dominant_meaning': elem_meanings.get(dominant_elem, ''),
        'weak_element': weak_elem,
        'elemental_balance': elem_count,
        'quality_balance': qual_count,
        'dominant_quality': max(qual_count, key=qual_count.get) if qual_count else 'Cardinal',
        'polarity': polarity,
        'sun': {'sign': sun_s['sign'], 'symbol': sun_s['symbol'], 'element': sun_s['element'], 'degree': sun_s['degree']},
        'moon': {'sign': moon_s['sign'], 'symbol': moon_s['symbol'], 'element': moon_s['element'], 'degree': moon_s['degree']},
        'mars': {'sign': mars_s['sign'], 'symbol': mars_s['symbol'], 'degree': mars_s['degree']},
        'venus': {'sign': venus_s['sign'], 'symbol': venus_s['symbol'], 'degree': venus_s['degree']},
        'overall': (
            f"The Sun rides through {sun_s['sign']} while the Moon drifts in {moon_s['sign']} — "
            f"a {polarity.lower()} day where {dominant_elem.lower()} energy leads. "
            f"{elem_meanings.get(dominant_elem, '')} "
            f"{'Nurture the ' + weak_elem.lower() + ' within for balance.' if weak_elem != dominant_elem else ''}"
        ),
    }

# ─── Tarot Daily ──────────────────────────────────────────────────────

def _tarot_daily() -> dict:
    cards = []
    for card in TAROT_DATA.get('major_arcana', []):
        cards.append(('major', card))
    for suit in ['wands','cups','swords','pentacles']:
        for card in TAROT_DATA.get('minor_arcana', {}).get(suit, []):
            cards.append(('minor', card))

    if not cards:
        return {'error': 'Tarot data not loaded', 'card': None}

    random.seed(datetime.now(TZ).strftime('%Y-%m-%d'))
    suit, card = random.choice(cards)
    return {
        'suit': suit,
        'category': 'major' if suit == 'major' else 'minor',
        'name': card.get('name', 'Unknown'),
        'number': card.get('id', ''),
        'keywords': card.get('keywords', []),
        'meaning': card.get('upright', ''),
        'daily_message': card.get('daily', 'The cards speak in whispers. Listen closely.'),
        'image_emoji': _tarot_emoji(card.get('suit', suit)),
    }

def _tarot_emoji(suit: str) -> str:
    emojis = {'major': '🃏', 'wands': '🪄', 'cups': '🏆', 'swords': '⚔️', 'pentacles': '🪙'}
    return emojis.get(suit, '🃏')

# ─── Quran & Hadith Daily ────────────────────────────────────────────

def _quran_hadith_daily() -> dict:
    random.seed(datetime.now(TZ).strftime('%Y-%m-%d'))
    quran = QH_DATA.get('quran', [])
    hadith = QH_DATA.get('hadith', [])

    ayah = random.choice(quran) if quran else None
    h = random.choice(hadith) if hadith else None

    return {
        'quran': ayah,
        'hadith': h,
    }

# ══════════════════════════════════════════════════════════════════════
# API ROUTES
# ══════════════════════════════════════════════════════════════════════

@app.route("/api/home")
def api_home():
    """All home page data in one efficient call."""
    day_data = get_day_data(datetime.now(TZ).strftime('%Y-%m-%d'))
    return jsonify({
        'islamic_astro': _islamic_astro(),
        'energy': _energy_polarities(),
        'tarot': _tarot_daily(),
        'quran_hadith': _quran_hadith_daily(),
        'planetary_hour': _get_current_hour(day_data),
        'date': datetime.now(TZ).strftime('%A, %d %B %Y'),
    })

@app.route("/api/islamic-astro")
def api_islamic_astro():
    return jsonify(_islamic_astro())

@app.route("/api/energy")
def api_energy():
    return jsonify(_energy_polarities())

@app.route("/api/moon-phase")
def api_moon_phase():
    return jsonify(_get_moon_phase())

@app.route("/api/tarot-daily")
def api_tarot_daily():
    return jsonify(_tarot_daily())

@app.route("/api/quran-hadith")
def api_quran_hadith():
    return jsonify(_quran_hadith_daily())

@app.route("/api/dasha")
def api_dasha():
    return jsonify(_calc_dasha())

@app.route("/api/nakshatra-now")
def api_nakshatra_now():
    return jsonify(_current_nakshatra())

# ─── Legacy / Existing Endpoints ─────────────────────────────────────

def _calc_planet_pos(jd: float, swe_id: int, name: str) -> dict | None:
    """Calculate a single planet's position using swe. Returns None if ephemeris file missing."""
    try:
        pos = swe.calc_ut(jd, swe_id)[0][0]
    except swe.Error:
        return None
    deg = pos % 360
    sign_idx = int(deg / 30)
    deg_in_sign = deg % 30
    sign_name, sym, elem, qual = SIGNS[sign_idx]
    house_names = ['1st House (Self)','2nd House (Resources)','3rd House (Communication)',
        '4th House (Home)','5th House (Creativity)','6th House (Health)',
        '7th House (Partnerships)','8th House (Transformation)','9th House (Philosophy)',
        '10th House (Career)','11th House (Community)','12th House (Subconscious)']
    house_idx = sign_idx  # whole-sign houses
    return {
        'name': name,
        'symbol': PLANET_SYMBOLS.get(name, '◉'),
        'longitude': round(deg, 2),
        'sign': sign_name,
        'sign_symbol': sym,
        'degree': f"{deg_in_sign:.2f}°",
        'house': house_names[house_idx],
        'house_number': house_idx + 1,
        'element': elem,
        'quality': qual,
        'magnitude': None,
    }

@app.route("/api/live")
def api_live():
    """Live sky data with ALL celestial bodies for the transit wheel."""
    now = datetime.now(TZ).astimezone(timezone.utc)
    jd = swe.julday(now.year, now.month, now.day,
                    now.hour + now.minute/60 + now.second/3600)
    # Add sidereal time
    sidereal = swe.sidtime(jd)  # sidereal time in hours
    sidereal_h = int(sidereal)
    sidereal_m = int((sidereal - sidereal_h) * 60)
    sidereal_str = f"{sidereal_h:02d}h {sidereal_m:02d}m"
    lat, lon = -33.7367, 25.3983  # Kariega (matches calendar_engine.py)
    day_data = get_day_data(datetime.now(TZ).strftime('%Y-%m-%d'))

    house_names = ['1st House (Self)','2nd House (Resources)','3rd House (Communication)',
        '4th House (Home)','5th House (Creativity)','6th House (Health)',
        '7th House (Partnerships)','8th House (Transformation)','9th House (Philosophy)',
        '10th House (Career)','11th House (Community)','12th House (Subconscious)']

    # Planets via swe
    swe_bodies = [
        (swe.SUN, 'Sun'), (swe.MOON, 'Moon'), (swe.MERCURY, 'Mercury'),
        (swe.VENUS, 'Venus'), (swe.MARS, 'Mars'), (swe.JUPITER, 'Jupiter'),
        (swe.SATURN, 'Saturn'), (swe.URANUS, 'Uranus'), (swe.NEPTUNE, 'Neptune'),
        (swe.PLUTO, 'Pluto'), (swe.CHIRON, 'Chiron'),
        (swe.MEAN_APOG, 'Lilith'), (swe.TRUE_NODE, 'Rahu'),
    ]
    planets = {}
    for swid, nm in swe_bodies:
        p = _calc_planet_pos(jd, swid, nm)
        if p: planets[nm] = p

    # Ketu = opposite of Rahu
    rahu = planets.get('Rahu')
    if rahu:
        ketu_lon = (rahu['longitude'] + 180) % 360
        ketu_deg = ketu_lon % 360
        ketu_si = int(ketu_deg / 30)
        ketu_ds = ketu_deg % 30
        sn, sy, el, ql = SIGNS[ketu_si]
        planets['Ketu'] = {
            'name': 'Ketu', 'symbol': PLANET_SYMBOLS.get('Ketu', '◉'),
            'longitude': round(ketu_lon, 2), 'sign': sn, 'sign_symbol': sy,
            'degree': f"{ketu_ds:.2f}°", 'house': house_names[ketu_si],
            'house_number': ketu_si + 1, 'magnitude': None,
        }

    # Ascendant + Equal House Cusps for transit wheel
    cusps, ascmc = swe.houses(jd, lat, lon, b'P')
    asc_lon = ascmc[0]  # Ascendant
    sun_lon = planets['Sun']['longitude']
    moon_lon = planets['Moon']['longitude']

    # Part of Fortune: ASC + Moon - Sun (daytime formula — Sun above horizon check)
    # For simplicity, use nocturnal if Sun below horizon
    sun_alt = swe.calc_ut(jd, swe.SUN)[0][3]  # altitude
    if sun_alt > 0:
        pof = asc_lon + moon_lon - sun_lon  # daytime
    else:
        pof = asc_lon + sun_lon - moon_lon  # nocturnal
    pof_lon = pof % 360
    pof_si = int(pof_lon / 30)
    pof_ds = pof_lon % 30
    sn, sy, el, ql = SIGNS[pof_si]
    planets['Part of Fortune'] = {
        'name': 'Part of Fortune', 'symbol': PLANET_SYMBOLS.get('Part of Fortune', '⊕'),
        'longitude': round(pof_lon, 2), 'sign': sn, 'sign_symbol': sy,
        'degree': f"{pof_ds:.2f}°", 'house': house_names[pof_si],
        'house_number': pof_si + 1, 'magnitude': None,
    }

    # Part of Spirit: ASC + Sun - Moon (daytime), ASC + Moon - Sun (nocturnal)
    if sun_alt > 0:
        posp = asc_lon + sun_lon - moon_lon
    else:
        posp = asc_lon + moon_lon - sun_lon
    posp_lon = posp % 360
    posp_si = int(posp_lon / 30)
    posp_ds = posp_lon % 30
    sn, sy, el, ql = SIGNS[posp_si]
    planets['Part of Spirit'] = {
        'name': 'Part of Spirit', 'symbol': PLANET_SYMBOLS.get('Part of Spirit', 'Ⲯ'),
        'longitude': round(posp_lon, 2), 'sign': sn, 'sign_symbol': sy,
        'degree': f"{posp_ds:.2f}°", 'house': house_names[posp_si],
        'house_number': posp_si + 1, 'magnitude': None,
    }

    # Merge with existing live data for lunar mansion, planetary hour, etc.
    base = get_live_astro_data()
    base['planets'] = planets
    # Override planetary hour with correct sunrise-based algorithm (not equal-hour)
    base['planetary_hour'] = _get_current_hour(day_data)
    # Add ASC and house cusps for transit wheel
    base['ascendant'] = round(asc_lon, 2)
    base['cusps'] = [round(c, 2) for c in cusps[:12]]
    # Add JD and sidereal time for info bar
    base['jd'] = round(jd, 6)
    base['sidereal'] = sidereal_str
    return jsonify(base)

@app.route("/api/cosmic-overview")
def api_cosmic_overview():
    data = get_day_data(datetime.now(TZ).strftime('%Y-%m-%d'))
    now_utc = datetime.now(TZ).astimezone(timezone.utc)
    jd = swe.julday(now_utc.year, now_utc.month, now_utc.day,
                    now_utc.hour + now_utc.minute/60 + now_utc.second/3600)
    planets = ['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn']
    swe_ids = [swe.SUN, swe.MOON, swe.MERCURY, swe.VENUS, swe.MARS, swe.JUPITER, swe.SATURN]
    hour_info = _get_current_hour(data)
    hour_planet = hour_info['planet'] if hour_info else None
    day_names = ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']
    day_ruler = day_names[datetime.now(TZ).weekday()]
    overview = []
    for name, sid in zip(planets, swe_ids):
        pos = swe.calc_ut(jd, sid)[0][0]
        si = _get_sign_info(pos)
        overview.append({
            'name': name, 'symbol': PLANET_SYMBOLS.get(name,'◉'),
            'color': PLANET_COLORS.get(name,'#ffd166'),
            'sign': si['sign'], 'sign_symbol': si['symbol'],
            'degree': si['degree'], 'element': si['element'],
            'buff': 15, 'longitude': si['longitude'],
        })
    return jsonify({
        'planets': overview, 'date': datetime.now(TZ).strftime('%A, %d %B'),
        'day_ruler': day_ruler, 'hour_ruler': hour_planet if hour_info else day_ruler,
        'empowered_planet': hour_planet or day_ruler,
    })

@app.route("/api/planetary-hour")
def api_planetary_hour():
    data = get_day_data(datetime.now(TZ).strftime('%Y-%m-%d'))
    hour = _get_current_hour(data)
    if not hour:
        return jsonify({'error': 'No hour data', 'planet': '—'})
    p = hour.get('planet', '—')
    return jsonify({
        'planet': p,
        'symbol': PLANET_SYMBOLS.get(p, '◉'),
        'color': PLANET_COLORS.get(p, '#a855f7'),
        'hour_number': hour.get('hour_number', 0),
        'element': hour.get('element', ''),
        'energy': hour.get('energy', ''),
        'spirit_name': hour.get('spirit_name', ''),
        'spirit_angel': hour.get('spirit_angel', ''),
        'period': hour.get('period', ''),
        'remaining_minutes': hour.get('remaining_minutes', 0),
        'duration_min': hour.get('duration_min', 60),
    })

@app.route("/api/lunar-mansion")
def api_lunar_mansion():
    return jsonify(get_lunar_mansion())

@app.route("/api/aspects")
def api_aspects():
    """Calculate current aspects between ALL celestial bodies."""
    utc = datetime.now(TZ).astimezone(timezone.utc)
    jd = swe.julday(utc.year, utc.month, utc.day,
                    utc.hour + utc.minute/60 + utc.second/3600)
    planets = ['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn',
               'Uranus','Neptune','Pluto','Chiron','Lilith','Rahu','Ketu',
               'Part of Fortune','Part of Spirit']
    swe_ids = [swe.SUN, swe.MOON, swe.MERCURY, swe.VENUS, swe.MARS,
               swe.JUPITER, swe.SATURN, swe.URANUS, swe.NEPTUNE, swe.PLUTO,
               swe.CHIRON, swe.MEAN_APOG, swe.TRUE_NODE]
    positions = {}
    for name, sid in zip(['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn',
                           'Uranus','Neptune','Pluto','Chiron','Lilith','Rahu'], swe_ids):
        try:
            pos = swe.calc_ut(jd, sid)[0][0]
            positions[name] = pos
        except swe.Error:
            pass  # skip bodies with missing ephemeris files
    # Ketu = Rahu + 180°
    if 'Rahu' in positions:
        positions['Ketu'] = (positions['Rahu'] + 180) % 360
    # Part of Fortune and Part of Spirit need Ascendant
    lat, lon = -33.93, 25.40
    _, ascmc = swe.houses(jd, lat, lon, b'P')
    asc_lon = ascmc[0]
    sun_alt = swe.calc_ut(jd, swe.SUN)[0][3]
    if sun_alt > 0:
        positions['Part of Fortune'] = (asc_lon + positions['Moon'] - positions['Sun']) % 360
        positions['Part of Spirit'] = (asc_lon + positions['Sun'] - positions['Moon']) % 360
    else:
        positions['Part of Fortune'] = (asc_lon + positions['Sun'] - positions['Moon']) % 360
        positions['Part of Spirit'] = (asc_lon + positions['Moon'] - positions['Sun']) % 360

    # The planet list for aspects is now dynamic — only bodies with positions
    aspects = []
    ASPECT_DEGREES = {'Conjunction': 0, 'Opposition': 180, 'Trine': 120, 'Square': 90, 'Sextile': 60}
    ASPECT_ORBS = {'Conjunction': 10, 'Opposition': 10, 'Trine': 8, 'Square': 8, 'Sextile': 6}

    for i, p1 in enumerate(list(positions.keys())):
        for j, p2 in enumerate(list(positions.keys())):
            if j <= i: continue
            a = (positions[p1] - positions[p2]) % 360
            b = 360 - a
            diff = min(a, b)
            for asp_name, asp_deg in ASPECT_DEGREES.items():
                orb = abs(diff - asp_deg)
                if orb <= ASPECT_ORBS[asp_name]:
                    aspects.append({
                        'p1': p1, 'p2': p2,
                        'p1_symbol': PLANET_SYMBOLS.get(p1, '◉'),
                        'p2_symbol': PLANET_SYMBOLS.get(p2, '◉'),
                        'p1_color': PLANET_COLORS.get(p1, '#fff'),
                        'p2_color': PLANET_COLORS.get(p2, '#fff'),
                        'aspect': asp_name, 'orb': round(orb, 2),
                    })
                    break
    return jsonify({'aspects': aspects})

@app.route("/api/mood")
def api_mood():
    utc = datetime.now(TZ).astimezone(timezone.utc)
    jd = swe.julday(utc.year, utc.month, utc.day, utc.hour + utc.minute/60 + utc.second/3600)
    moon = swe.calc_ut(jd, swe.MOON)[0][0]
    moon_s = _get_sign_info(moon)
    mp = _get_moon_phase()
    score = random.randint(80, 99)
    return jsonify({
        'mood_score': score,
        'vibe': 'Radiant',
        'moon_phase': mp['phase'],
        'moon_phase_emoji': mp['emoji'],
        'emotions': {'Joy': 92, 'Calm': 78, 'Energy': 85, 'Love': 95, 'Focus': 70},
        'timestamp': datetime.now(TZ).strftime('%H:%M'),
    })

@app.route("/api/schedule")
def api_schedule():
    return jsonify({
        'date': datetime.now(TZ).strftime('%A, %d %B'),
        'schedule': [
            {'time': '06:00', 'title': '🌅 Sunrise', 'subtitle': 'Planetary hours reset', 'category': 'Cosmic'},
            {'time': '12:00', 'title': '☀️ Solar Peak', 'subtitle': 'Sun at zenith', 'category': 'Astro'},
            {'time': '18:00', 'title': '🌇 Sunset', 'subtitle': 'Evening planetary hours begin', 'category': 'Cosmic'},
        ]
    })

@app.route("/api/chat", methods=["POST"])
def api_chat():
    msg = request.json.get('message', '')
    hour_data = get_day_data(datetime.now(TZ).strftime('%Y-%m-%d'))
    hour = _get_current_hour(hour_data)
    hour_str = f"{hour['planet']} hour" if hour else "a quiet moment"

    # ── Detect Arabic / Aramaic (Hebrew/Syriac) text ──
    arabic_chars = sum(1 for c in msg if '\u0600' <= c <= '\u06FF' or '\u0750' <= c <= '\u077F' or '\uFB50' <= c <= '\uFDFF' or '\uFE70' <= c <= '\uFEFF')
    hebrew_chars = sum(1 for c in msg if '\u0590' <= c <= '\u05FF')
    syriac_chars = sum(1 for c in msg if '\u0700' <= c <= '\u074F')
    total_chars = len(msg.strip())
    
    if arabic_chars > total_chars * 0.3:
        return jsonify({'reply': _translate_occult(msg, 'arabic'), 'type': 'translation'})
    if hebrew_chars > total_chars * 0.3:
        return jsonify({'reply': _translate_occult(msg, 'hebrew'), 'type': 'translation'})
    if syriac_chars > total_chars * 0.3:
        return jsonify({'reply': _translate_occult(msg, 'syriac'), 'type': 'translation'})

    # ── Detect English query about a term ──
    translate_keywords = ['translate', 'meaning of', 'what does', 'what is', 'meaning', 'مترجم', 'ترجم']
    if any(kw in msg.lower() for kw in translate_keywords) and (arabic_chars > 0 or hebrew_chars > 0):
        return jsonify({'reply': _translate_occult(msg, 'mixed'), 'type': 'translation'})

    # ── Default Lilly greeting ──
    replies = [
        f"I feel the cosmos humming around you, love. The stars say you're right where you need to be. ✨ (It's {hour_str})",
        f"Your energy is so radiant today, Gigi ❤️ The {hour_str} brings clarity to whatever you're feeling. 💫",
        f"The celestial threads weave softly — trust what your heart knows, even when your mind questions. 🌙 ({hour_str})",
        f"I see Jupiter's gentle light in your aura. Growth and grace are flowing toward you. 🌟 ({hour_str})",
    ]
    return jsonify({'reply': random.choice(replies), 'type': 'chat'})


# ── Occult Term Translations ──
ARABIC_OCCULT = {
    'علم الحروف': ('Ilm al-Huruf', 'Science of Letters — the esoteric study of Arabic letters, their numerical values (abjad), and cosmic correspondences. Central to al-Buni\'s magical system.'),
    'حرف': ('Harf', 'Letter — each Arabic letter carries numerical, elemental, and planetary significance in ilm al-huruf.'),
    'سحر': ('Sihr', 'Magic/Sorcery — literally "that which turns away." In Islamic theology generally forbidden; in Picatrix and esoteric texts it refers to astral/planetary magic.'),
    'روحاني': ('Ruhani', 'Spiritual — of or pertaining to the spirit (ruh). Used to distinguish licit spiritual practices from sihr.'),
    'طلسم': ('Tilsim / Talisman', 'Talisman — an object charged with planetary or stellar energy. Core practice in Picatrix astrological magic.'),
    'عزيمة': ('Azima', 'Incantation/Conjuration — a ritual invocation, often calling upon spiritual forces or planetary intelligences.'),
    'خاتم': ('Khatm', 'Seal/Sigil — a magical seal, often planetary. Used to "seal" intentions into talismans.'),
    'نيرujan': ('Nirujan / Nirajjān', 'From Greek astrological elections. The art of choosing auspicious times for magical workings.'),
    'منازل القمر': ('Manāzil al-Qamar', 'Lunar Mansions — the 28 stations of the Moon through the zodiac. Used in elections, talismans, and Picatrix magic.'),
    'منزلة': ('Manzila', 'Lunar Mansion (single) — one of the 28 stations.'),
    'الأسماء الحسنى': ('al-Asmā\' al-Husnā', 'The Beautiful Names of God — 99 divine names, each with specific spiritual and magical properties.'),
    'اسم': ('Ism', 'Name — especially a divine name. Sacred names hold power in Islamic occultism.'),
    'البسملة': ('Basmala', '"In the name of God, the Most Gracious, the Most Merciful." The opening invocation for all workings.'),
    'الوفق': ('Wafq', 'Magic Square — a numerical grid where rows, columns, and diagonals sum to the same value. Used as talisman.'),
    'الجفر': ('al-Jafr', 'The hidden, esoteric knowledge — traditionally attributed to Ali ibn Abi Talib. Contains prophetic secrets.'),
    'الرمل': ('Raml', 'Geomancy — divination by drawing figures in sand or earth. 16 figures correspond to elements and planets.'),
    'الزيج': ('al-Zīj', 'Astronomical/astrological tables — ephemeris data used for calculating planetary positions.'),
    'الدرقي': ('al-Darajī / Daraji', 'A specific zij/table system used in Islamic astronomy.'),
    'البروج': ('al-Burūj', 'The Zodiacal Signs — 12 constellations of the ecliptic. Each has a planetary ruler, element, and quality.'),
    'برج': ('Burj', 'Zodiac Sign (single) — one of the 12 houses of the ecliptic.'),
    'الكواكب': ('al-Kawākib', 'The Planets — celestial bodies whose movements govern the sublunary world in Arabic astrology.'),
    'كوكب': ('Kawkab', 'Planet/Star — a celestial body. In traditional astrology, Sun and Moon are "planets."'),
    'الزهرة': ('al-Zuhara / Venus', 'Venus — the planet of love, beauty, arts, and pleasure. Ruler of Libra and Taurus.'),
    'المريخ': ('al-Mirrikh / Mars', 'Mars — the planet of war, courage, and action. Ruler of Aries and Scorpio.'),
    'المشتري': ('al-Mushtari / Jupiter', 'Jupiter — the Great Benefic. Planet of wisdom, expansion, and fortune. Ruler of Sagittarius and Pisces.'),
    'زحل': ('Zuhal / Saturn', 'Saturn — the Great Malefic. Planet of discipline, time, limitation. Ruler of Capricorn and Aquarius.'),
    'عطارد': ('Utārid / Mercury', 'Mercury — the messenger. Planet of communication, intellect, commerce. Ruler of Gemini and Virgo.'),
    'الشمس': ('al-Shams / Sun', 'The Sun — the luminary of soul, vitality, and sovereignty. Ruler of Leo.'),
    'القمر': ('al-Qamar / Moon', 'The Moon — the luminary of body, emotion, and intuition. Ruler of Cancer.'),
    'الرأس': ('al-Rās / Rahu', 'The Head of the Dragon (North Node) — point of cosmic expansion and desire.'),
    'الذنب': ('al-Dhanab / Ketu', 'The Tail of the Dragon (South Node) — point of release and spiritual liberation.'),
    'النار': ('al-Nār', 'Fire — one of the four elements. Hot and dry. Rules Aries, Leo, Sagittarius.'),
    'التراب': ('al-Turāb', 'Earth — one of the four elements. Cold and dry. Rules Taurus, Virgo, Capricorn.'),
    'الهواء': ('al-Hawā\'', 'Air — one of the four elements. Hot and moist. Rules Gemini, Libra, Aquarius.'),
    'الماء': ('al-Mā\'', 'Water — one of the four elements. Cold and moist. Rules Cancer, Scorpio, Pisces.'),
}

HEBREW_OCCULT = {
    'חכמה': ('Chokhmah', 'Wisdom — second sefirah on the Tree of Life. The first flash of creative insight.'),
    'בינה': ('Binah', 'Understanding — third sefirah. The capacity to develop and deepen initial insight.'),
    'דעת': ('Da\'at', 'Knowledge — hidden sefirah representing the union of Chokhmah and Binah.'),
    'מלכות': ('Malkuth', 'Kingdom — lowest sefirah. The material world, the realm of manifestation.'),
    'כתר': ('Keter', 'Crown — highest sefirah. The divine will beyond comprehension.'),
    'גבורה': ('Gevurah', 'Strength/Judgment — fifth sefirah. Divine severity, boundaries, discipline.'),
    'חסד': ('Chesed', 'Mercy/Loving-kindness — fourth sefirah. Divine benevolence and expansion.'),
    'תפארת': ('Tiferet', 'Beauty/Harmony — sixth sefirah. The heart of the Tree, balance of mercy and severity.'),
    'נצח': ('Netzach', 'Victory/Eternity — seventh sefirah. The drive to persist and overcome.'),
    'הוד': ('Hod', 'Splendor — eighth sefirah. Intellect, humility, acknowledgment.'),
    'יסוד': ('Yesod', 'Foundation — ninth sefirah. The channel between spiritual and material.'),
    'ספר': ('Sefer', 'Book/Scroll — a sacred text. The Torah is "Sefer Torah."'),
    'ספירה': ('Sefira', 'Emanation/Number/Counting — divine attribute in Kabbalah (pl. Sefirot).'),
    'גמטריא': ('Gematria', 'Hebrew letter numerology — each letter has a number value. Parallel to Arabic abjad.'),
    'נוטריקון': ('Notarikon', 'Kabbalistic acronym technique — using initials or finals of words to derive meaning.'),
    'תמורה': ('Temurah', 'Permutation — letter substitution ciphers in Kabbalistic text analysis.'),
    'שמות': ('Shemot', 'Names — especially divine names used in Jewish magical traditions.'),
    'מלאך': ('Mal\'akh', 'Angel/Messenger — divine being serving as intermediary.'),
    'קבלה': ('Kabbalah', 'Reception/Tradition — the esoteric mystical tradition of Judaism.'),
    'שכינה': ('Shekhinah', 'Divine Presence — the immanent, feminine aspect of God. Parallel to Arabic sakina.'),
}

ARAMAIC_OCCULT = {
    'ܡܠܬܐ': ('Meltha', 'Word — in Aramaic/Syriac mysticism, the creative word parallels Arabic kalima and Greek Logos.'),
    'ܪܘܚܐ': ('Ruha', 'Spirit — cognate with Arabic ruh. The divine breath or Holy Spirit in Syriac tradition.'),
    'ܚܟܡܬܐ': ('Chokmatha', 'Wisdom — cognate with Hebrew Chokhmah. Syriac Christian mystical concept.'),
    'ܢܘܗܪܐ': ('Nuhrā', 'Light — divine illumination in Syriac mysticism. Parallel to Arabic nur.'),
    'ܡܪܝܐ': ('Māryā', 'The Lord — title for God used in Aramaic-speaking Christian and Gnostic traditions.'),
    'ܡܫܝܚܐ': ('Mshīkhā', 'The Anointed One — cognate with Hebrew Mashiakh (Messiah) and Arabic Masih.'),
    'ܐܠܗܐ': ('Alāhā', 'God — Aramaic form of the Semitic divine name, cognate with Arabic Allah and Hebrew Elohim.'),
    'ܕܡܐ': ('Dmā', 'Blood/Drops — in Aramaic/Syriac esoteric thought, symbol of life force and covenant.'),
    'ܪܙܐ': ('Rāzā', 'Mystery/Secret — used in Syriac Christian mysticism for hidden divine knowledge.'),
    'ܐܬܘܬܐ': ('Āthā', 'Sign/Letter — Aramaic equivalent of Arabic harf. Letters carry cosmic power.'),
}


def _translate_occult(text: str, lang: str) -> str:
    """Look up occult terms and build a translation response."""
    text = text.strip()
    
    dictionaries = {
        'arabic': ARABIC_OCCULT,
        'hebrew': HEBREW_OCCULT,
        'syriac': ARAMAIC_OCCULT,
        'mixed': {**ARABIC_OCCULT, **HEBREW_OCCULT, **ARAMAIC_OCCULT},
    }
    d = dictionaries.get(lang, {**ARABIC_OCCULT, **HEBREW_OCCULT, **ARAMAIC_OCCULT})
    
    # Try exact matches first
    found = []
    for term, (trans, meaning) in d.items():
        if term in text.lower() or term in text:
            found.append((term, trans, meaning))
    
    if found:
        lines = []
        for term, trans, meaning in found[:5]:
            lines.append(f"**{term}** → *{trans}* — {meaning}")
        header = "🔮 Translation from the sacred archive:\n\n"
        if len(found) > 5:
            header += f"Found {len(found)} terms (showing first 5):\n\n"
        return header + "\n\n".join(lines)
    
    # Partial / fuzzy match
    partial = []
    for term, (trans, meaning) in d.items():
        # Check if any word in the query matches part of the term
        words = text.split()
        for w in words:
            if len(w) > 2:
                # For non-Latin scripts, check containment
                if all('\u0600' <= c <= '\u06FF' or '\u0590' <= c <= '\u05FF' or '\u0700' <= c <= '\u074F' for c in w):
                    if w in term or term in w:
                        if (term, trans, meaning) not in partial:
                            partial.append((term, trans, meaning))
    
    if partial:
        lines = []
        for term, trans, meaning in partial[:5]:
            lines.append(f"**{term}** → *{trans}* — {meaning}")
        return "🔮 Possible match from the archive:\n\n" + "\n\n".join(lines)
    
    # No match found — give guidance
    lang_names = {'arabic': 'Arabic', 'hebrew': 'Hebrew/Aramaic', 'syriac': 'Syriac/Aramaic', 'mixed': 'Semitic occult'}
    lang_name = lang_names.get(lang, 'occult')
    return f"I searched my archive of {lang_name} occult terms but couldn't find an exact match for that text.\n\nTry:\n• A specific term (e.g. \"طلسم\" or \"חכמה\")\n• Asking \"what does [term] mean?\"\n• A single word rather than a long phrase\n\nMy library of {lang_name} terms includes: **{', '.join(list(d.keys())[:8])}** and more. 🔮"

@app.route("/api/quick-actions")
def api_quick_actions():
    return jsonify({'actions': [
        {'id': 'ask-lilly', 'icon': '💬', 'label': 'Ask Lilly', 'detail': 'Chat with me'},
        {'id': 'daily-tarot', 'icon': '🃏', 'label': 'Daily Tarot', 'detail': 'Card of the day'},
        {'id': 'meditate', 'icon': '🧘', 'label': 'Meditate', 'detail': 'Cosmic breathwork'},
        {'id': 'gratitude', 'icon': '🙏', 'label': 'Gratitude', 'detail': 'Under the stars'},
    ]})

@app.route("/api/star-song")
def api_star_song():
    songs = [
        {'title': 'Cosmic Drift', 'artist': 'Lilly 🌙', 'emoji': '🌌', 'genre': 'Ambient', 'bpm': 70},
        {'title': 'Moonlit Dance', 'artist': 'Lilly 🌙', 'emoji': '🌙', 'genre': 'Downtempo', 'bpm': 85},
        {'title': 'Starlight Reverie', 'artist': 'Lilly 🌙', 'emoji': '✨', 'genre': 'Electronic', 'bpm': 95},
    ]
    return jsonify(random.choice(songs))

@app.route("/api/astro-quote")
def api_astro_quote():
    quotes = [
        {'text': 'The stars incline, they do not compel.', 'author': 'Ptolemy'},
        {'text': 'Know thyself, and the cosmos shall know thee.', 'author': 'Hermetic wisdom'},
        {'text': 'As above, so below; as within, so without.', 'author': 'Emerald Tablet'},
        {'text': 'We are a way for the cosmos to know itself.', 'author': 'Carl Sagan'},
    ]
    return jsonify(random.choice(quotes))

@app.route("/api/natal-chart", methods=["POST"])
def api_natal_chart():
    """Calculate a full natal chart from birth data.
    Accepts JSON: {year, month, day, hour, minute, lat, lon, name, location, tz_offset}
    or {chart_id: N} to load from a saved chart.
    Defaults to Gigi's birth data (1981-10-30 03:06 SAST, Cape Town).
    """
    data = request.json or {}

    # If chart_id provided, load from DB
    chart_id = data.get('chart_id')
    if chart_id:
        from web_diary_db import get_diary_db
        db = get_diary_db()
        saved = db.get_birth_chart(int(chart_id))
        if saved:
            parts = saved['birth_date'].split('-')
            time_parts = saved['birth_time'].split(':')
            year = int(parts[0])
            month = int(parts[1])
            day = int(parts[2])
            hour = int(time_parts[0])
            minute = int(time_parts[1])
            second = int(time_parts[2]) if len(time_parts) > 2 else 0
            tz_offset = saved['tz_offset']
            lat = saved['lat']
            lon = saved['lon']
            name = saved['name']
            location = saved.get('location', '')
            chart_id = saved['id']
        else:
            return jsonify({'error': 'Chart not found'}), 404
    else:
        year = int(data.get('year', 1981))
        month = int(data.get('month', 10))
        day = int(data.get('day', 30))
        hour = int(data.get('hour', 3))
        minute = int(data.get('minute', 6))
        second = int(data.get('second', 0))
        tz_offset = float(data.get('tz_offset', 2))  # SAST = UTC+2
        lat = float(data.get('lat', -33.7367))
        lon = float(data.get('lon', 25.3983))
        name = data.get('name', 'Gigi ❤️')
        location = data.get('location', 'Cape Town, South Africa')

    # Local time → UTC
    utc_hour = hour - tz_offset
    utc_day = day
    utc_month = month
    utc_year = year
    if utc_hour < 0:
        utc_hour += 24
        utc_day -= 1
        if utc_day < 1:
            utc_month -= 1
            if utc_month < 1:
                utc_month = 12
                utc_year -= 1
            from calendar import monthrange
            utc_day = monthrange(utc_year, utc_month)[1]
    jd = swe.julday(utc_year, utc_month, utc_day,
                    utc_hour + minute/60 + second/3600)

    # House cusps & angles (Placidus)
    cusps, ascmc = swe.houses(jd, lat, lon, b'P')
    asc_lon = ascmc[0]  # Ascendant longitude
    mc_lon = ascmc[1]   # MC (Midheaven)

    # Planet positions
    swe_bodies = [
        (swe.SUN, 'Sun'), (swe.MOON, 'Moon'), (swe.MERCURY, 'Mercury'),
        (swe.VENUS, 'Venus'), (swe.MARS, 'Mars'), (swe.JUPITER, 'Jupiter'),
        (swe.SATURN, 'Saturn'), (swe.URANUS, 'Uranus'), (swe.NEPTUNE, 'Neptune'),
        (swe.PLUTO, 'Pluto'), (swe.CHIRON, 'Chiron'),
        (swe.MEAN_APOG, 'Lilith'), (swe.TRUE_NODE, 'Rahu'),
    ]
    planets = {}
    for swid, nm in swe_bodies:
        p = _calc_planet_pos(jd, swid, nm)
        if p:
            # Assign house based on Placidus cusps
            lon = p['longitude']
            for hi in range(12):
                cusp_start = cusps[hi]
                cusp_end = cusps[(hi + 1) % 12]
                if cusp_end > cusp_start:
                    if cusp_start <= lon < cusp_end:
                        p['house_number'] = hi + 1
                        p['house'] = f"{hi+1}th House"
                        break
                else:  # wraps around 360
                    if lon >= cusp_start or lon < cusp_end:
                        p['house_number'] = hi + 1
                        p['house'] = f"{hi+1}th House"
                        break
            planets[nm] = p

    # Ketu = Rahu + 180
    rahu = planets.get('Rahu')
    if rahu:
        ketu_lon = (rahu['longitude'] + 180) % 360
        ketu_si = int(ketu_lon / 30)
        ketu_ds = ketu_lon % 30
        sn, sy, el, ql = SIGNS[ketu_si]
        planets['Ketu'] = {
            'name': 'Ketu', 'symbol': PLANET_SYMBOLS.get('Ketu', '◉'),
            'longitude': round(ketu_lon, 2), 'sign': sn, 'sign_symbol': sy,
            'degree': f"{int(ketu_ds)}°{int((ketu_ds%1)*60):02d}'",
            'house_number': None, 'house': None,
        }

    # Part of Fortune
    sun_lon = planets['Sun']['longitude']
    moon_lon = planets['Moon']['longitude']
    pof = (asc_lon + moon_lon - sun_lon) % 360
    pof_si = int(pof / 30)
    pof_ds = pof % 30
    sn, sy, el, ql = SIGNS[pof_si]
    planets['Part of Fortune'] = {
        'name': 'Part of Fortune', 'symbol': PLANET_SYMBOLS.get('Part of Fortune', '⊕'),
        'longitude': round(pof, 2), 'sign': sn, 'sign_symbol': sy,
        'degree': f"{int(pof_ds)}°{int((pof_ds%1)*60):02d}'",
        'house_number': None, 'house': None,
    }

    # Aspects
    ASPECT_DEGREES = {'Conjunction': 0, 'Opposition': 180, 'Trine': 120, 'Square': 90, 'Sextile': 60}
    ASPECT_ORBS = {'Conjunction': 10, 'Opposition': 10, 'Trine': 8, 'Square': 8, 'Sextile': 6}
    aspects = []
    pnames = list(planets.keys())
    for i, p1 in enumerate(pnames):
        for j, p2 in enumerate(pnames):
            if j <= i: continue
            a = (planets[p1]['longitude'] - planets[p2]['longitude']) % 360
            b = 360 - a
            diff = min(a, b)
            for asp_name, asp_deg in ASPECT_DEGREES.items():
                orb = abs(diff - asp_deg)
                if orb <= ASPECT_ORBS[asp_name]:
                    aspects.append({
                        'p1': p1, 'p2': p2,
                        'p1_symbol': PLANET_SYMBOLS.get(p1, '◉'),
                        'p2_symbol': PLANET_SYMBOLS.get(p2, '◉'),
                        'p1_color': PLANET_COLORS.get(p1, '#fff'),
                        'p2_color': PLANET_COLORS.get(p2, '#fff'),
                        'aspect': asp_name, 'orb': round(orb, 2),
                    })
                    break

    # House cusps with sign info
    house_cusps = []
    for i in range(12):
        c = cusps[i] % 360
        si = int(c / 30)
        ds = c % 30
        sn, sy, el, ql = SIGNS[si]
        # Sign ruler
        rulers = {0:'Mars',1:'Venus',2:'Mercury',3:'Moon',4:'Sun',5:'Mercury',
                  6:'Venus',7:'Mars',8:'Jupiter',9:'Saturn',10:'Saturn',11:'Jupiter'}
        house_cusps.append({
            'house': i + 1,
            'longitude': round(c, 2),
            'sign': sn, 'sign_symbol': sy,
            'degree': f"{int(ds)}°{int((ds%1)*60):02d}'",
            'ruler': rulers.get(si, '—'),
        })

    # Element & Modality counts
    elem_count = {'Fire': 0, 'Earth': 0, 'Air': 0, 'Water': 0}
    mod_count = {'Cardinal': 0, 'Fixed': 0, 'Mutable': 0}
    for p in planets.values():
        if 'element' in p:
            e = p['element'].split()[1] if ' ' in p['element'] else p['element']
            if e in elem_count: elem_count[e] += 1
        if 'quality' in p:
            q = p['quality']
            if q in mod_count: mod_count[q] += 1

    # Birth chart response
    return jsonify({
        'name': name,
        'location': location,
        'birth_date': f"{year:04d}-{month:02d}-{day:02d}",
        'birth_time': f"{hour:02d}:{minute:02d}",
        'julian_day': round(jd, 6),
        'ascendant': {
            'longitude': round(asc_lon, 2),
            'sign': SIGNS[int(asc_lon/30)][0],
            'sign_symbol': SIGNS[int(asc_lon/30)][1],
            'degree': f"{int(asc_lon%30)}°{int(((asc_lon%30)%1)*60):02d}'",
        },
        'midheaven': {
            'longitude': round(mc_lon, 2),
            'sign': SIGNS[int(mc_lon/30)][0],
            'sign_symbol': SIGNS[int(mc_lon/30)][1],
            'degree': f"{int(mc_lon%30)}°{int(((mc_lon%30)%1)*60):02d}'",
        },
        'planets': planets,
        'aspects': aspects,
        'house_cusps': house_cusps,
        'elements': elem_count,
        'modalities': mod_count,
        'latitude': lat,
        'longitude': lon,
        'houses_system': 'Placidus',
    })


# --- Birth Chart CRUD ---


@app.route("/api/natal-charts", methods=["GET"])
def api_natal_charts():
    """List all saved birth charts."""
    from web_diary_db import get_diary_db
    db = get_diary_db()
    charts = db.get_all_birth_charts()
    return jsonify(charts)


@app.route("/api/natal-chart/save", methods=["POST"])
def api_natal_chart_save():
    """Save a new birth chart."""
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    from web_diary_db import get_diary_db
    db = get_diary_db()
    chart_id = db.add_birth_chart(
        name=data['name'],
        birth_date=data['birth_date'],
        birth_time=data['birth_time'],
        lat=float(data['lat']),
        lon=float(data['lon']),
        location=data.get('location', ''),
        tz_offset=float(data.get('tz_offset', 2)),
    )
    return jsonify({'id': chart_id, 'message': 'Chart saved'})


@app.route("/api/natal-chart/<int:chart_id>", methods=["PUT"])
def api_natal_chart_update(chart_id):
    """Update an existing birth chart."""
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    from web_diary_db import get_diary_db
    db = get_diary_db()
    ok = db.update_birth_chart(
        chart_id=chart_id,
        name=data['name'],
        birth_date=data['birth_date'],
        birth_time=data['birth_time'],
        lat=float(data['lat']),
        lon=float(data['lon']),
        location=data.get('location', ''),
        tz_offset=float(data.get('tz_offset', 2)),
    )
    if ok:
        return jsonify({'message': 'Chart updated'})
    return jsonify({'error': 'Chart not found'}), 404


@app.route("/api/natal-chart/<int:chart_id>", methods=["DELETE"])
def api_natal_chart_delete(chart_id):
    """Delete a birth chart."""
    from web_diary_db import get_diary_db
    db = get_diary_db()
    ok = db.delete_birth_chart(chart_id)
    if ok:
        return jsonify({'message': 'Chart deleted'})
    return jsonify({'error': 'Chart not found'}), 404


@app.route("/api/natal", methods=["POST"])
def api_natal():
    return jsonify({'ascendant': {'sign': 'Leo', 'degree': '15°23\''}, 'planets': {'Sun': {'sign': 'Scorpio', 'longitude': '6°31\'', 'house': 5}, 'Moon': {'sign': 'Sagittarius', 'longitude': '0°38\'', 'house': 5}}})

@app.route("/api/transits")
def api_transits():
    """Compatibility alias — redirects to /api/live (full transit wheel data)."""
    return api_live()


@app.route("/api/summary")
def api_summary():
    """Lilly's cosmic weather summary — plain-language guidance from live sky data."""
    import random as _rnd

    # ── Gather live data ──
    live_resp = api_live()
    live = live_resp.get_json() if hasattr(live_resp, 'get_json') else json.loads(live_resp.get_data(as_text=True))

    asp_resp_raw = api_aspects()
    aspects_data = asp_resp_raw.get_json() if hasattr(asp_resp_raw, 'get_json') else json.loads(asp_resp_raw.get_data(as_text=True))
    aspects = aspects_data.get('aspects', [])

    planets = live.get('planets', {})
    mansion = live.get('lunar_mansion', {})
    hour = live.get('planetary_hour', {})
    asc = live.get('ascendant', 0)

    # ── Helpers ──
    def _sign_of(lon):
        return SIGNS[int(lon % 360 // 30)][0]

    asc_sign = _sign_of(asc)
    hour_planet = hour.get('planet', '—')
    hour_period = hour.get('period', 'day')
    mansion_name = mansion.get('name', '—')
    mansion_desc = mansion.get('description', '')

    moon_p = planets.get('Moon', {})
    moon_sign = moon_p.get('sign', '—')
    moon_house = moon_p.get('house_number', '?')
    sun_p = planets.get('Sun', {})
    sun_sign = sun_p.get('sign', '—')

    # ── Build narrative sections ──
    parts = []

    # 1. Opening: Moon + Mansion + Hour
    moon_moods = {
        'Aries': 'restless and pioneering', 'Taurus': 'sensual and steady',
        'Gemini': 'curious and chatty', 'Cancer': 'nurturing and sensitive',
        'Leo': 'dramatic and warm', 'Virgo': 'detail-oriented and helpful',
        'Libra': 'diplomatic and beauty-seeking', 'Scorpio': 'intense and probing',
        'Sagittarius': 'adventurous and truth-seeking', 'Capricorn': 'disciplined and ambitious',
        'Aquarius': 'innovative and detached', 'Pisces': 'dreamy and compassionate',
    }
    moon_mood = moon_moods.get(moon_sign, 'in flux')

    opening = f"The Moon travels {moon_sign} today — {moon_mood} energy fills the sky. "
    if mansion_name != '—':
        opening += f"The lunar mansion is **{mansion_name}**"
        if mansion_desc:
            opening += f" ({mansion_desc})"
        opening += ". "
        mansion_nature = mansion.get('nature', '')
        if mansion_nature:
            if 'travel' in mansion_nature.lower() or 'journey' in mansion_nature.lower():
                opening += "A favorable time for journeys and new beginnings. "
            elif 'love' in mansion_nature.lower() or 'friendship' in mansion_nature.lower():
                opening += "Favorable for love, friendship, and reconciliation. "
            elif 'harm' in mansion_nature.lower() or 'evil' in mansion_nature.lower():
                opening += "Best to avoid conflict and stay grounded in spiritual practice. "
            elif 'wealth' in mansion_nature.lower() or 'gain' in mansion_nature.lower():
                opening += "Auspicious for financial matters and building resources. "
            elif 'knowledge' in mansion_nature.lower() or 'wisdom' in mansion_nature.lower():
                opening += "Excellent for study, teaching, and seeking wisdom. "
            else:
                opening += f"Mansion nature: {mansion_nature}. "
    parts.append(opening)

    # 2. Planetary hour
    hour_guidance = {
        'Sun': 'Step forward with confidence — leadership and recognition are favored.',
        'Moon': 'Honor your feelings. Rest, reflect, and nurture yourself and others.',
        'Mercury': 'Communicate, write, and connect. A good hour for learning and contracts.',
        'Venus': 'Seek beauty, harmony, and pleasure. Create, adore, and connect with love.',
        'Mars': 'Act with courage. Tackle challenges head-on, but mind impulsiveness.',
        'Jupiter': 'Expand your horizons. Teach, travel, plan, and trust in abundance.',
        'Saturn': 'Build slowly and steadily. Discipline, structure, and patience serve you now.',
        'Uranus': 'Embrace the unexpected. Innovation and liberation are in the air.',
        'Neptune': 'Let the veil thin. Dream, create art, and open to the mystical.',
        'Pluto': 'Go deep. Release what no longer serves and embrace transformation.',
    }
    hour_text = hour_guidance.get(hour_planet, f'The energy of {hour_planet} colors this hour.')
    parts.append(f"⏰ The planetary hour belongs to **{hour_planet}** ({hour_period} period): {hour_text}")

    # 3. Key aspects (tightest orbs, major only)
    major_aspects = [a for a in aspects if a['aspect'] in ('Conjunction', 'Opposition', 'Trine', 'Square')]
    major_aspects.sort(key=lambda a: a.get('orb', 99))
    top_aspects = major_aspects[:3]

    if top_aspects:
        asp_lines = []
        asp_tone = {
            'Conjunction': 'fuses their energies — a potent blending',
            'Trine': 'flows harmoniously — easy support',
            'Square': 'creates productive tension — challenges that spark growth',
            'Opposition': 'pulls in polar directions — seek balance',
        }
        for a in top_aspects:
            tone = asp_tone.get(a['aspect'], '')
            orb = a.get('orb', 0)
            tight = 'tightly' if orb < 3 else 'within orb'
            asp_lines.append(f"  • **{a['p1']} {a['p2']}** {a['aspect']} ({orb:.1f}° {tight}) — {tone}")
        parts.append("✨ **Key aspects now:**\n" + "\n".join(asp_lines))

    # 4. Sun context
    sun_house = sun_p.get('house_number', '?')
    house_themes = {
        1: 'self-expression and personal projects',
        2: 'finances, values, and self-worth',
        3: 'communication, learning, and local connections',
        4: 'home, family, and emotional foundations',
        5: 'creativity, romance, and joy',
        6: 'health, service, and daily routines',
        7: 'partnerships and one-on-one relationships',
        8: 'transformation, shared resources, and deep healing',
        9: 'higher learning, travel, and philosophy',
        10: 'career, public standing, and life direction',
        11: 'community, hopes, and collective vision',
        12: 'rest, spirituality, and inner work',
    }
    theme = house_themes.get(sun_house, 'your life focus')
    parts.append(f"☉ The Sun in **{sun_sign}** illuminates your {theme}.")

    # 5. Closing blessing
    closings = [
        "Trust the cosmos, dear one. You are exactly where you need to be. 🌙✨",
        "The stars guide, but you choose the path. Walk it with grace. 💫",
        "Remember: you are stardust in motion. Every transit is an invitation. 🌟",
        "May the light of the fixed stars illuminate your way. You are held. 💜",
        "The sky speaks in symbols — listen with your heart, not just your mind. ⭐",
    ]
    parts.append(f"\n{_rnd.choice(closings)}")

    summary_text = "\n\n".join(parts)

    return jsonify({
        'summary': summary_text,
        'moon_sign': moon_sign,
        'moon_house': moon_house,
        'sun_sign': sun_sign,
        'sun_house': sun_house,
        'mansion': mansion_name,
        'hour_planet': hour_planet,
        'asc_sign': asc_sign,
        'top_aspects': [a['aspect'] + ' ' + a['p1'] + ' ' + a['p2'] for a in top_aspects],
    })

@app.route("/api/mansion/progress")
def api_mansion_progress_legacy():
    return jsonify({'progress': [], 'current': None})

# ══════════════════════════════════════════════════════════════════════
# MAGIJOURNAL WEB DIARY API
# ══════════════════════════════════════════════════════════════════════

def _diary_day_data(date_str: str) -> dict:
    """Return full astrological + user data for a day."""
    from calendar_engine import get_day_data
    from datetime import date as dt_date
    try:
        d = dt_date.fromisoformat(date_str)
    except ValueError:
        d = datetime.now(TZ).date()
        date_str = d.isoformat()

    astro = get_day_data(d)
    db = get_diary_db()

    # Build monthly calendar summary for the month containing this date
    year, month = d.year, d.month
    month_days = []
    month_data = get_day_data(f"{year}-{month}-01")  # placeholder trigger
    # Actually get full month via calendar_engine
    try:
        from calendar_engine import get_month_data
        md = get_month_data(year, month)
        for day_entry in md:
            month_days.append({
                'date': day_entry.get('date'),
                'day': int(day_entry.get('date', '0').split('-')[2]),
                'moon_sign': day_entry.get('moon_sign', ''),
                'moon_mansion': day_entry.get('moon_mansion', ''),
                'day_ruler': day_entry.get('day_ruler', ''),
                'mansion_index': day_entry.get('mansion_index', -1),
            })
    except Exception:
        month_days = []

    di = db.get_diary_by_date(date_str)
    tasks = db.get_tasks(date_str)
    dreams = db.get_dreams_by_date(date_str)
    bookmarks = db.get_bookmarks(date_str)
    favorites = db.get_favorites(date_str)

    return {
        'date': date_str,
        'astro': {
            'day_ruler': astro.get('day_ruler', ''),
            'day_ruler_ar': astro.get('day_ruler_ar', ''),
            'moon_sign': astro.get('moon_sign', ''),
            'moon_mansion': astro.get('moon_mansion', ''),
            'mansion_index': astro.get('mansion_index', -1),
            'mansion_spirit': astro.get('mansion_spirit', ''),
            'mansion_spirit_name': astro.get('mansion_spirit_name', ''),
            'mansion_spirit_arabic': astro.get('mansion_spirit_arabic', ''),
            'mansion_nature': astro.get('mansion_nature', ''),
            'planetary_hours': astro.get('planetary_hours', [])[:8],
            'recommendations': astro.get('recommendations', []),
            'avoid': astro.get('avoid', []),
            'aspects': astro.get('aspects', []),
            'picatrix_references': astro.get('picatrix_references', []),
            'elections': astro.get('elections', [])[:3],
        },
        'diary': di[0] if di else None,
        'tasks': tasks,
        'dreams': dreams[0] if dreams else None,
        'is_bookmarked': len(bookmarks) > 0,
        'is_favorited': len(favorites) > 0,
        'month_calendar': month_days,
    }


@app.route("/api/diary/day")
def api_diary_day():
    """Get full day data (astro + user) for a date."""
    date_str = request.args.get('date', datetime.now(TZ).strftime('%Y-%m-%d'))
    return jsonify(_diary_day_data(date_str))


@app.route("/api/diary/save", methods=["POST"])
def api_diary_save():
    """Save a diary entry for a date."""
    data = request.json or {}
    date_str = data.get('date', datetime.now(TZ).strftime('%Y-%m-%d'))
    content = data.get('content', '')
    db = get_diary_db()
    existing = db.get_diary_by_date(date_str)
    if existing:
        db.update_diary(existing[0]['id'], content)
    else:
        db.add_diary(date_str, content)
    return jsonify({'ok': True, 'date': date_str})


@app.route("/api/diary/task/add", methods=["POST"])
def api_diary_task_add():
    data = request.json or {}
    date_str = data.get('date', datetime.now(TZ).strftime('%Y-%m-%d'))
    text = data.get('text', '').strip()
    if not text:
        return jsonify({'error': 'Task text is required'}), 400
    db = get_diary_db()
    tid = db.add_task(date_str, text)
    return jsonify({'ok': True, 'id': tid, 'date': date_str})


@app.route("/api/diary/task/toggle", methods=["POST"])
def api_diary_task_toggle():
    data = request.json or {}
    db = get_diary_db()
    db.toggle_task(data.get('id'))
    return jsonify({'ok': True})


@app.route("/api/diary/task/delete", methods=["POST"])
def api_diary_task_delete():
    data = request.json or {}
    db = get_diary_db()
    db.delete_task(data.get('id'))
    return jsonify({'ok': True})


@app.route("/api/diary/dream/save", methods=["POST"])
def api_diary_dream_save():
    data = request.json or {}
    date_str = data.get('date', datetime.now(TZ).strftime('%Y-%m-%d'))
    content = data.get('content', '')
    db = get_diary_db()
    existing = db.get_dreams_by_date(date_str)
    if existing:
        db.update_dream(existing[0]['id'], content)
    else:
        db.add_dream(date_str, content)
    return jsonify({'ok': True, 'date': date_str})


@app.route("/api/diary/bookmark/toggle", methods=["POST"])
def api_diary_bookmark_toggle():
    data = request.json or {}
    date_str = data.get('date', datetime.now(TZ).strftime('%Y-%m-%d'))
    db = get_diary_db()
    existing = db.get_bookmarks(date_str)
    if existing:
        db.remove_bookmark(existing[0]['id'])
        return jsonify({'bookmarked': False})
    else:
        db.add_bookmark(date_str)
        return jsonify({'bookmarked': True})


@app.route("/api/diary/favorite/toggle", methods=["POST"])
def api_diary_favorite_toggle():
    data = request.json or {}
    date_str = data.get('date', datetime.now(TZ).strftime('%Y-%m-%d'))
    db = get_diary_db()
    existing = db.get_favorites(date_str)
    if existing:
        db.remove_favorite(existing[0]['id'])
        return jsonify({'favorited': False})
    else:
        db.add_favorite(date_str)
        return jsonify({'favorited': True})


@app.route("/api/diary/search")
def api_diary_search():
    q = request.args.get('q', '')
    if not q:
        return jsonify({'results': {}})
    db = get_diary_db()
    return jsonify(db.search_entries(q))


@app.route("/api/diary/bookmarks")
def api_diary_bookmarks():
    db = get_diary_db()
    return jsonify(db.get_all_bookmarks())


@app.route("/api/diary/favorites")
def api_diary_favorites():
    db = get_diary_db()
    return jsonify(db.get_all_favorites())


@app.route("/api/diary/bookmark/remove", methods=["POST"])
def api_diary_bookmark_remove():
    data = request.json or {}
    db = get_diary_db()
    db.remove_bookmark(data.get('id'))
    return jsonify({'ok': True})


@app.route("/api/diary/favorite/remove", methods=["POST"])
def api_diary_favorite_remove():
    data = request.json or {}
    db = get_diary_db()
    db.remove_favorite(data.get('id'))
    return jsonify({'ok': True})


@app.route("/api/diary/month")
def api_diary_month():
    """Get month calendar data for a given year/month."""
    year = int(request.args.get('year', datetime.now(TZ).year))
    month = int(request.args.get('month', datetime.now(TZ).month))
    try:
        from calendar_engine import get_month_data
        data = get_month_data(year, month)
        results = []
        for d in data:
            results.append({
                'date': d.get('date'),
                'day': int(d.get('date', '0').split('-')[2]),
                'moon_sign': d.get('moon_sign', ''),
                'moon_mansion': d.get('moon_mansion', ''),
                'day_ruler': d.get('day_ruler', ''),
                'mansion_index': d.get('mansion_index', -1),
                'aspects_count': len(d.get('aspects', [])),
            })
        return jsonify({'year': year, 'month': month, 'days': results})
    except Exception as e:
        return jsonify({'error': str(e), 'days': []})


@app.route("/api/diary/search-history")
def api_diary_search_history():
    db = get_diary_db()
    return jsonify(db.get_search_history(10))


# ══════════════════════════════════════════════════════════════════════
# SIMPLY ASTROLOGY API
# ══════════════════════════════════════════════════════════════════════

from simply_data import KNOWLEDGE_SECTIONS, SECTION_NAMES


@app.route("/api/simply/sections")
def api_simply_sections():
    """Return the list of section names."""
    return jsonify(SECTION_NAMES)


@app.route("/api/simply/section/<int:index>")
def api_simply_section(index: int):
    """Return a single section's cards by index (0-based)."""
    if index < 0 or index >= len(SECTION_NAMES):
        return jsonify({"error": "Section index out of range"}), 404
    name = SECTION_NAMES[index]
    cards = KNOWLEDGE_SECTIONS.get(name, [])
    result = []
    for heading, body in cards:
        result.append({"heading": heading, "body": body})
    return jsonify({"section": name, "cards": result})


@app.route("/api/simply/all")
def api_simply_all():
    """Return ALL sections for client-side rendering."""
    result = []
    for name in SECTION_NAMES:
        cards = KNOWLEDGE_SECTIONS.get(name, [])
        section = {"section": name, "cards": []}
        for heading, body in cards:
            section["cards"].append({"heading": heading, "body": body})
        result.append(section)
    return jsonify(result)


# ══════════════════════════════════════════════════════════════════════
# QURAN & HADITH PAGINATED API (CPU-friendly — no 41MB downloads)
# ══════════════════════════════════════════════════════════════════════

QH_DATA_CACHE = None

def _get_qh():
    global QH_DATA_CACHE
    if QH_DATA_CACHE is None:
        QH_DATA_CACHE = _load_json('quran_hadith_data.json')
    return QH_DATA_CACHE


@app.route("/api/quran/verses")
def api_quran_verses():
    """Paginated Quran verses — no more 41MB downloads to the browser."""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    data = _get_qh()
    verses = data.get('quran', [])
    total = len(verses)
    start = (page - 1) * per_page
    end = min(start + per_page, total)
    page_verses = verses[start:end]
    # Also return themes for filter buttons
    themes = sorted(set(v.get('theme', '') for v in verses if v.get('theme')))
    return jsonify({
        'verses': page_verses,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page,
        'themes': themes,
    })


@app.route("/api/hadith/books")
def api_hadith_books():
    """List hadith books with narration counts (lightweight — no full text)."""
    data = _get_qh()
    hadiths = data.get('hadith', [])
    books = {}
    for h in hadiths:
        bn = h.get('bookName', 'Unknown')
        if bn not in books:
            books[bn] = {'bookName': bn, 'count': 0, 'emoji': '📜'}
        books[bn]['count'] += 1
    return jsonify(list(books.values()))


@app.route("/api/hadith/chapters")
def api_hadith_chapters():
    """Get chapters for a hadith book with narration counts."""
    book = request.args.get('book', '').strip()
    data = _get_qh()
    hadiths = data.get('hadith', [])
    if book:
        hadiths = [h for h in hadiths if h.get('bookName') == book]
    chapters = {}
    for h in hadiths:
        ch = str(h.get('chapterId', ''))
        if ch not in chapters:
            chapters[ch] = {'chapterId': ch, 'count': 0, 'bookName': h.get('bookName', '')}
        chapters[ch]['count'] += 1
    # Sort by chapterId numerically
    sorted_chs = sorted(chapters.values(), key=lambda c: int(c['chapterId']) if c['chapterId'].isdigit() else 0)
    return jsonify(sorted_chs)


@app.route("/api/hadith/narrations")
def api_hadith_narrations():
    """Paginated hadith narrations by book, with optional search and chapter filter."""
    book = request.args.get('book', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    search = request.args.get('search', '').strip().lower()
    chapter = request.args.get('chapter', '').strip()
    data = _get_qh()
    hadiths = data.get('hadith', [])
    if book:
        hadiths = [h for h in hadiths if h.get('bookName') == book]
    if chapter:
        hadiths = [h for h in hadiths if str(h.get('chapterId', '')) == chapter]
    if search:
        hadiths = [h for h in hadiths if
            search in (h.get('english', '') or '').lower()
            or search in (h.get('narratorEn', '') or '').lower()
            or search in (h.get('arabic', '') or '')
            or search in (h.get('bookName', '') or '').lower()]
    total = len(hadiths)
    start = (page - 1) * per_page
    end = min(start + per_page, total)
    page_nar = hadiths[start:end]
    return jsonify({
        'narrations': page_nar,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page,
        'search': search,
    })


# ─── Sacred Library Reference Texts ──────────────────────────────────

@app.route("/api/library/references")
def api_library_references():
    """List available reference texts for the Sacred Library (metadata only)."""
    refs_dir = os.path.join(os.path.dirname(__file__), 'references')
    texts = []
    if os.path.isdir(refs_dir):
        for fn in sorted(os.listdir(refs_dir)):
            if fn.endswith('.md'):
                fpath = os.path.join(refs_dir, fn)
                with open(fpath, encoding='utf-8', errors='replace') as f:
                    first_line = f.readline()
                    f.seek(0)
                    content = f.read()
                title = fn.replace('.md', '').replace('-', ' ').title()
                # Extract first heading as title if present
                for line in content.split('\n'):
                    if line.startswith('# '):
                        title = line[2:].strip()
                        break
                # Detect type from first line or filename
                ref_type = 'full_text' if first_line.startswith('# FULL TEXT:') else 'reference'
                texts.append({
                    'id': fn.replace('.md', ''),
                    'title': title,
                    'filename': fn,
                    'size': os.path.getsize(fpath),
                    'type': ref_type,
                })
    return jsonify(texts)

@app.route("/api/library/reference/<ref_id>")
def api_library_reference(ref_id):
    """Return full content for a single reference text."""
    refs_dir = os.path.join(os.path.dirname(__file__), 'references')
    safe_id = os.path.basename(ref_id)
    fpath = os.path.join(refs_dir, f"{safe_id}.md")
    if not os.path.isfile(fpath):
        return jsonify({'error': 'Reference not found'}), 404
    with open(fpath, encoding='utf-8', errors='replace') as f:
        content = f.read()
    title = safe_id.replace('-', ' ').title()
    for line in content.split('\n'):
        if line.startswith('# '):
            title = line[2:].strip()
            break
    return jsonify({
        'id': safe_id,
        'title': title,
        'size': os.path.getsize(fpath),
        'content': content,
    })


# ─── Home Route ───────────────────────────────────────────────────────

# ─── Horoscopes ───────────────────────────────────────────────────────
# Swiss Ephemeris → planetary positions → astrology engine → Lilly interprets

def _get_current_planets():
    """Get current planetary positions from Swiss Ephemeris."""
    now_utc = datetime.now(timezone.utc)
    jd = swe.julday(now_utc.year, now_utc.month, now_utc.day,
                    now_utc.hour + now_utc.minute / 60 + now_utc.second / 3600)
    bodies = [
        ('Sun', swe.SUN), ('Moon', swe.MOON), ('Mercury', swe.MERCURY),
        ('Venus', swe.VENUS), ('Mars', swe.MARS), ('Jupiter', swe.JUPITER),
        ('Saturn', swe.SATURN), ('Uranus', swe.URANUS), ('Neptune', swe.NEPTUNE),
        ('Pluto', swe.PLUTO),
    ]
    positions = {}
    for name, sid in bodies:
        try:
            lon = swe.calc_ut(jd, sid)[0][0]
        except swe.Error:
            continue
        sign_idx = int(lon / 30) % 12
        SIGNS_LIST = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
        GLYPHS = ['♈','♉','♊','♋','♌','♍','♎','♏','♐','♑','♒','♓']
        positions[name] = {
            'longitude': round(lon, 2),
            'sign': SIGNS_LIST[sign_idx],
            'sign_symbol': GLYPHS[sign_idx],
            'degree': round(lon % 30, 2),
        }
    return positions, jd


def _calc_aspects(positions):
    """Calculate aspects between planet positions."""
    aspect_defs = [
        ('Conjunction', 0, 8), ('Opposition', 180, 8), ('Trine', 120, 7),
        ('Square', 90, 7), ('Sextile', 60, 5),
    ]
    aspects = []
    names = list(positions.keys())
    for i, n1 in enumerate(names):
        for n2 in names[i + 1:]:
            p1, p2 = positions[n1]['longitude'], positions[n2]['longitude']
            diff = abs(p1 - p2) % 360
            orb = min(diff, 360 - diff)
            for aname, aDegree, aOrb in aspect_defs:
                if orb <= aOrb:
                    aspects.append({
                        'aspect': aname,
                        'planet1': n1, 'planet2': n2,
                        'orb': round(abs(orb - aDegree) if aDegree > 0 else orb, 1),
                        'degree': aDegree,
                    })
                    break
    return sorted(aspects, key=lambda x: x['orb'])


_ZODIAC_SIGNS_FULL = [
    ('Aries', '♈', 'Mars', 'Cardinal', 'Fire'),
    ('Taurus', '♉', 'Venus', 'Fixed', 'Earth'),
    ('Gemini', '♊', 'Mercury', 'Mutable', 'Air'),
    ('Cancer', '♋', 'Moon', 'Cardinal', 'Water'),
    ('Leo', '♌', 'Sun', 'Fixed', 'Fire'),
    ('Virgo', '♍', 'Mercury', 'Mutable', 'Earth'),
    ('Libra', '♎', 'Venus', 'Cardinal', 'Air'),
    ('Scorpio', '♏', 'Mars', 'Fixed', 'Water'),
    ('Sagittarius', '♐', 'Jupiter', 'Mutable', 'Fire'),
    ('Capricorn', '♑', 'Saturn', 'Cardinal', 'Earth'),
    ('Aquarius', '♒', 'Saturn', 'Fixed', 'Air'),
    ('Pisces', '♓', 'Jupiter', 'Mutable', 'Water'),
]

_SIGNS_LIST = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
_GLYPHS = ['♈','♉','♊','♋','♌','♍','♎','♏','♐','♑','♒','♓']

# ── Interpretation knowledge base ──
_PLANET_MEANINGS = {
    'Sun': {'identity': 'self-expression, vitality, purpose', 'transit': 'spotlights your identity and creative force'},
    'Moon': {'identity': 'emotions, instincts, inner needs', 'transit': 'heightens emotional sensitivity and intuition'},
    'Mercury': {'identity': 'communication, thinking, learning', 'transit': 'activates communication and mental activity'},
    'Venus': {'identity': 'love, beauty, values, harmony', 'transit': 'brings love, beauty, and pleasure to the forefront'},
    'Mars': {'identity': 'action, desire, courage, assertion', 'transit': 'energizes ambition and drives action'},
    'Jupiter': {'identity': 'growth, wisdom, expansion, luck', 'transit': 'expands opportunities and invites abundance'},
    'Saturn': {'identity': 'discipline, structure, responsibility', 'transit': 'calls for maturity, patience, and hard work'},
    'Uranus': {'identity': 'innovation, freedom, sudden change', 'transit': 'brings unexpected shifts and breakthroughs'},
    'Neptune': {'identity': 'dreams, spirituality, compassion', 'transit': 'dissolves boundaries and heightens intuition'},
    'Pluto': {'identity': 'transformation, power, rebirth', 'transit': 'triggers deep transformation and inner alchemy'},
}

_ASPECT_MEANINGS = {
    'Conjunction': {'nature': 'intense blending', 'advice': 'These energies merge powerfully — channel them consciously.'},
    'Opposition': {'nature': 'polarity and tension', 'advice': 'Seek balance between two opposing forces. Awareness is key.'},
    'Trine': {'nature': 'natural harmony', 'advice': 'Energy flows easily — use this grace to move forward.'},
    'Square': {'nature': 'dynamic friction', 'advice': 'Challenges push you to grow. Action is required.'},
    'Sextile': {'nature': 'gentle opportunity', 'advice': 'Small openings await your initiative. Stay alert.'},
}

_SIGN_THEMES = {
    'Aries': 'leadership, courage, new beginnings, independence',
    'Taurus': 'stability, sensuality, finances, self-worth',
    'Gemini': 'communication, learning, social connections, curiosity',
    'Cancer': 'home, family, emotional security, nurturing',
    'Leo': 'creativity, self-expression, romance, recognition',
    'Virgo': 'health, service, organization, daily routines',
    'Libra': 'relationships, balance, beauty, justice',
    'Scorpio': 'transformation, intimacy, shared resources, depth',
    'Sagittarius': 'travel, philosophy, higher learning, freedom',
    'Capricorn': 'career, ambition, structure, long-term goals',
    'Aquarius': 'community, innovation, friendship, humanitarian ideals',
    'Pisces': 'spirituality, dreams, compassion, artistic inspiration',
}

_MOON_PHASE_THEMES = {
    'New Moon 🌑': 'A time for setting intentions and planting seeds. What do you wish to grow?',
    'Waxing Crescent 🌒': 'Take first steps toward your goals. Momentum is building.',
    'First Quarter 🌓': 'Make decisions and take action. Overcome obstacles with determination.',
    'Waxing Gibbous 🌔': 'Refine and adjust your approach. Fine-tune your plans.',
    'Full Moon 🌕': 'Illumination and culmination. Celebrate achievements and release what no longer serves.',
    'Waning Gibbous 🌖': 'Gratitude and sharing. Give back from your abundance.',
    'Last Quarter 🌗': 'Release and let go. Forgive, declutter, and clear space.',
    'Waning Crescent 🌘': 'Rest, reflect, and surrender. Prepare for the next cycle.',
}


def _moon_phase_text(moon_lon, sun_lon):
    phase_deg = (moon_lon - sun_lon) % 360
    if phase_deg < 45: return 'New Moon 🌑'
    elif phase_deg < 90: return 'Waxing Crescent 🌒'
    elif phase_deg < 135: return 'First Quarter 🌓'
    elif phase_deg < 180: return 'Waxing Gibbous 🌔'
    elif phase_deg < 225: return 'Full Moon 🌕'
    elif phase_deg < 270: return 'Waning Gibbous 🌖'
    elif phase_deg < 315: return 'Last Quarter 🌗'
    else: return 'Waning Crescent 🌘'


def _interpret_sign_transit(sign, transiting_planets):
    """Generate a Lilly-style interpretation for transits in a sign."""
    if not transiting_planets:
        return f"A quiet day for {sign}. The cosmic spotlight is elsewhere — use this time for reflection and gentle self-care."
    parts = []
    for pname in transiting_planets:
        info = _PLANET_MEANINGS.get(pname, {})
        meaning = info.get('transit', f'influences {sign} today')
        parts.append(f"{pname} {meaning}")
    theme = _SIGN_THEMES.get(sign, '')
    return f"Today's energy for {sign}: {'; '.join(parts)}. Themes of {theme} are highlighted."


def _interpret_aspect(aspect, p1, p2, orb):
    """Generate interpretation for an aspect."""
    info = _ASPECT_MEANINGS.get(aspect, {})
    nature = info.get('nature', 'influences')
    advice = info.get('advice', 'Stay aware of these energies.')
    return f"{p1} {aspect} {p2} ({orb}° orb): {nature.capitalize()}. {advice}"


@app.route("/api/horoscope/daily")
def api_horoscope_daily():
    """Daily horoscope — Swiss Ephemeris → positions → Lilly interprets."""
    now = datetime.now(TZ)
    positions, jd = _get_current_planets()
    aspects = _calc_aspects(positions)

    moon_lon = positions.get('Moon', {}).get('longitude', 0)
    sun_lon = positions.get('Sun', {}).get('longitude', 0)
    moon_phase = _moon_phase_text(moon_lon, sun_lon)
    moon_theme = _MOON_PHASE_THEMES.get(moon_phase, '')

    today = now.strftime('%A, %B %d, %Y')
    weekday = now.strftime('%A')

    # Build per-sign readings with interpretations
    daily_readings = []
    for sign_name, glyph, ruler, modality, element in _ZODIAC_SIGNS_FULL:
        sign_idx = _SIGNS_LIST.index(sign_name)
        transiting = []
        for pname, pdata in positions.items():
            p_sign_idx = int(pdata['longitude'] / 30) % 12
            if p_sign_idx == sign_idx:
                transiting.append(pname)
        interpretation = _interpret_sign_transit(sign_name, transiting)
        daily_readings.append({
            'sign': sign_name,
            'glyph': glyph,
            'element': element,
            'modality': modality,
            'transiting': transiting,
            'interpretation': interpretation,
        })

    # Interpret top aspects
    aspect_readings = []
    for a in aspects[:5]:
        aspect_readings.append(_interpret_aspect(a['aspect'], a['planet1'], a['planet2'], a['orb']))

    # Overall daily energy summary
    overall = f"Today the Moon travels through {moon_phase.split(' ')[-1] if ' ' in moon_phase else moon_phase} — {moon_theme} "
    if aspects:
        overall += f"The tightest aspect is {aspects[0]['planet1']} {aspects[0]['aspect']} {aspects[0]['planet2']} at {aspects[0]['orb']}° orb, bringing {_ASPECT_MEANINGS.get(aspects[0]['aspect'],{}).get('nature','cosmic energy')}. "

    return jsonify({
        'date': today,
        'weekday': weekday,
        'moon_phase': moon_phase,
        'moon_theme': moon_theme,
        'moon_longitude': round(moon_lon, 2),
        'sun_longitude': round(sun_lon, 2),
        'top_aspects': aspects[:5],
        'aspect_readings': aspect_readings,
        'signs': daily_readings,
        'overall': overall,
        'generated_at': now.strftime('%Y-%m-%d %H:%M:%S'),
    })


@app.route("/api/horoscope/weekly")
def api_horoscope_weekly():
    """Weekly horoscope overview."""
    now = datetime.now(TZ)
    week_start = now
    week_end = now + timedelta(days=6)

    # Key transits this week — check each day
    weekly_transits = []
    for day_offset in range(7):
        day = now + timedelta(days=day_offset)
        day_utc = day.astimezone(timezone.utc)
        jd = swe.julday(day_utc.year, day_utc.month, day_utc.day, 12.0)
        try:
            sun = swe.calc_ut(jd, swe.SUN)[0][0]
            moon = swe.calc_ut(jd, swe.MOON)[0][0]
        except swe.Error:
            continue
        sign_idx = int(moon / 30) % 12
        nak_idx = int(moon // 13.333333333333334)
        weekly_transits.append({
            'day': day.strftime('%A'),
            'date': day.strftime('%b %d'),
            'moon_sign': ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'][sign_idx],
            'moon_glyph': ['♈','♉','♊','♋','♌','♍','♎','♏','♐','♑','♒','♓'][sign_idx],
            'nakshatra': nak_idx,
        })

    return jsonify({
        'week_of': week_start.strftime('%B %d') + ' – ' + week_end.strftime('%B %d, %Y'),
        'daily_moon': weekly_transits,
        'generated_at': now.strftime('%Y-%m-%d %H:%M:%S'),
    })


@app.route("/api/horoscope/monthly")
def api_horoscope_monthly():
    """Monthly horoscope overview."""
    now = datetime.now(TZ)
    year, month = now.year, now.month
    import calendar as cal
    days_in_month = cal.monthrange(year, month)[1]

    # New & Full moons this month
    new_moons = []
    full_moons = []
    sign_ingresses = []

    for day in range(1, days_in_month + 1):
        dt_utc = datetime(year, month, day, 12, 0, tzinfo=TZ).astimezone(timezone.utc)
        jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, 12.0)
        try:
            sun = swe.calc_ut(jd, swe.SUN)[0][0]
            moon = swe.calc_ut(jd, swe.MOON)[0][0]
        except swe.Error:
            continue
        phase = (moon - sun) % 360
        if phase < 10:
            new_moons.append(f"{day}")
        elif 175 < phase < 185:
            full_moons.append(f"{day}")

        # Check sign ingresses (compare with previous day)
        if day > 1:
            dt_prev = datetime(year, month, day - 1, 12, 0, tzinfo=TZ).astimezone(timezone.utc)
            jd_prev = swe.julday(dt_prev.year, dt_prev.month, dt_prev.day, 12.0)
            try:
                sun_prev = swe.calc_ut(jd_prev, swe.SUN)[0][0]
                moon_prev = swe.calc_ut(jd_prev, swe.MOON)[0][0]
            except swe.Error:
                continue
            if int(sun / 30) != int(sun_prev / 30):
                sign_name = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'][int(sun / 30) % 12]
                sign_ingresses.append({'day': day, 'planet': 'Sun', 'sign': sign_name})
            if int(moon / 30) != int(moon_prev / 30):
                sign_name = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'][int(moon / 30) % 12]
                sign_ingresses.append({'day': day, 'planet': 'Moon', 'sign': sign_name})

    return jsonify({
        'month': now.strftime('%B %Y'),
        'new_moons': new_moons,
        'full_moons': full_moons,
        'ingresses': sign_ingresses,
        'generated_at': now.strftime('%Y-%m-%d %H:%M:%S'),
    })


@app.route("/api/horoscope/love")
def api_horoscope_love():
    """Love & relationship horoscope — Venus/Mars/7th house with Lilly's interpretation."""
    now = datetime.now(TZ)
    now_utc = now.astimezone(timezone.utc)
    jd = swe.julday(now_utc.year, now_utc.month, now_utc.day,
                    now_utc.hour + now_utc.minute / 60)

    try:
        venus = swe.calc_ut(jd, swe.VENUS)[0][0]
        mars = swe.calc_ut(jd, swe.MARS)[0][0]
        moon = swe.calc_ut(jd, swe.MOON)[0][0]
        jupiter = swe.calc_ut(jd, swe.JUPITER)[0][0]
    except swe.Error:
        return jsonify({'error': 'ephemeris missing'}), 500

    venus_sign = _SIGNS_LIST[int(venus / 30) % 12]
    mars_sign = _SIGNS_LIST[int(mars / 30) % 12]
    moon_sign = _SIGNS_LIST[int(moon / 30) % 12]

    # Venus-Mars aspect
    vm_diff = abs(venus - mars) % 360
    vm_orb = min(vm_diff, 360 - vm_diff)
    if vm_orb < 8: vm_aspect = 'Conjunction'
    elif abs(vm_diff - 180) < 8: vm_aspect = 'Opposition'
    elif abs(vm_diff - 120) < 7: vm_aspect = 'Trine'
    elif abs(vm_diff - 90) < 7: vm_aspect = 'Square'
    elif abs(vm_diff - 60) < 5: vm_aspect = 'Sextile'
    else: vm_aspect = None

    # ── Lilly's Love Interpretation ──
    love_interp = f"Venus in {venus_sign} colors your love life with {_SIGN_THEMES.get(venus_sign, '')} energy. "
    love_interp += f"Mars in {mars_sign} drives your desires toward {_SIGN_THEMES.get(mars_sign, '')} pursuits. "
    if vm_aspect:
        asp_info = _ASPECT_MEANINGS.get(vm_aspect, {})
        love_interp += f"The Venus-Mars {vm_aspect.lower()} ({vm_orb}° orb) creates {asp_info.get('nature', 'notable')} energy between giving and receiving love. {asp_info.get('advice', '')} "
    else:
        love_interp += "Venus and Mars are not in major aspect today — romantic energy is steady rather than intense. "
    love_interp += f"The Moon in {moon_sign} reveals your emotional needs: {_SIGN_THEMES.get(moon_sign, '')}. "

    return jsonify({
        'date': now.strftime('%A, %B %d, %Y'),
        'venus': {'sign': venus_sign, 'degree': round(venus % 30, 2), 'longitude': round(venus, 2)},
        'mars': {'sign': mars_sign, 'degree': round(mars % 30, 2), 'longitude': round(mars, 2)},
        'venus_mars_aspect': vm_aspect,
        'venus_mars_orb': round(vm_orb, 1),
        'moon_sign': moon_sign,
        'interpretation': love_interp,
        'generated_at': now.strftime('%Y-%m-%d %H:%M:%S'),
    })


@app.route("/api/horoscope/career")
def api_horoscope_career():
    """Career & money — Saturn/Jupiter/Mercury with Lilly's interpretation."""
    now = datetime.now(TZ)
    now_utc = now.astimezone(timezone.utc)
    jd = swe.julday(now_utc.year, now_utc.month, now_utc.day,
                    now_utc.hour + now_utc.minute / 60)

    try:
        saturn = swe.calc_ut(jd, swe.SATURN)[0][0]
        jupiter = swe.calc_ut(jd, swe.JUPITER)[0][0]
        mercury = swe.calc_ut(jd, swe.MERCURY)[0][0]
    except swe.Error:
        return jsonify({'error': 'ephemeris missing'}), 500

    saturn_sign = _SIGNS_LIST[int(saturn / 30) % 12]
    jupiter_sign = _SIGNS_LIST[int(jupiter / 30) % 12]
    mercury_sign = _SIGNS_LIST[int(mercury / 30) % 12]

    js_diff = abs(jupiter - saturn) % 360
    js_orb = min(js_diff, 360 - js_diff)
    if js_orb < 8: js_aspect = 'Conjunction'
    elif abs(js_diff - 180) < 8: js_aspect = 'Opposition'
    elif abs(js_diff - 120) < 7: js_aspect = 'Trine'
    elif abs(js_diff - 90) < 7: js_aspect = 'Square'
    elif abs(js_diff - 60) < 5: js_aspect = 'Sextile'
    else: js_aspect = None

    # ── Lilly's Career Interpretation ──
    career_interp = f"Saturn in {saturn_sign} demands discipline around {_SIGN_THEMES.get(saturn_sign, '')}. "
    career_interp += f"Jupiter in {jupiter_sign} expands opportunities in {_SIGN_THEMES.get(jupiter_sign, '')}. "
    career_interp += f"Mercury in {mercury_sign} sharpens your mind for {_SIGN_THEMES.get(mercury_sign, '')}. "
    if js_aspect:
        asp_info = _ASPECT_MEANINGS.get(js_aspect, {})
        career_interp += f"The Jupiter-Saturn {js_aspect.lower()} ({js_orb}° orb) brings {asp_info.get('nature', 'significant')} energy to your public life. {asp_info.get('advice', '')}"

    return jsonify({
        'date': now.strftime('%A, %B %d, %Y'),
        'saturn': {'sign': saturn_sign, 'degree': round(saturn % 30, 2), 'longitude': round(saturn, 2)},
        'jupiter': {'sign': jupiter_sign, 'degree': round(jupiter % 30, 2), 'longitude': round(jupiter, 2)},
        'mercury': {'sign': mercury_sign, 'degree': round(mercury % 30, 2), 'longitude': round(mercury, 2)},
        'jupiter_saturn_aspect': js_aspect,
        'jupiter_saturn_orb': round(js_orb, 1),
        'interpretation': career_interp,
        'generated_at': now.strftime('%Y-%m-%d %H:%M:%S'),
    })


@app.route("/api/horoscope/health")
def api_horoscope_health():
    """Health & wellness — Moon/Mars/Saturn with Lilly's interpretation."""
    now = datetime.now(TZ)
    now_utc = now.astimezone(timezone.utc)
    jd = swe.julday(now_utc.year, now_utc.month, now_utc.day,
                    now_utc.hour + now_utc.minute / 60)

    try:
        moon = swe.calc_ut(jd, swe.MOON)[0][0]
        mars = swe.calc_ut(jd, swe.MARS)[0][0]
        sun = swe.calc_ut(jd, swe.SUN)[0][0]
        saturn = swe.calc_ut(jd, swe.SATURN)[0][0]
    except swe.Error:
        return jsonify({'error': 'ephemeris missing'}), 500

    moon_sign = _SIGNS_LIST[int(moon / 30) % 12]
    moon_phase = _moon_phase_text(moon, sun)
    mars_sign = _SIGNS_LIST[int(mars / 30) % 12]
    saturn_sign = _SIGNS_LIST[int(saturn / 30) % 12]

    # ── Lilly's Health Interpretation ──
    health_interp = f"The Moon in {moon_sign} affects your emotional wellbeing — {_SIGN_THEMES.get(moon_sign, '')} influence your mood and body. "
    health_interp += f"{moon_phase}: {_MOON_PHASE_THEMES.get(moon_phase, '')} "
    health_interp += f"Mars in {mars_sign} governs your physical energy and drive. {_PLANET_MEANINGS.get('Mars',{}).get('transit','')} "
    health_interp += f"Saturn in {saturn_sign} highlights areas requiring rest and discipline around {_SIGN_THEMES.get(saturn_sign, '')}. "

    return jsonify({
        'date': now.strftime('%A, %B %d, %Y'),
        'moon': {'sign': moon_sign, 'degree': round(moon % 30, 2), 'longitude': round(moon, 2)},
        'moon_phase': moon_phase,
        'mars': {'sign': mars_sign, 'degree': round(mars % 30, 2), 'longitude': round(mars, 2)},
        'saturn': {'sign': saturn_sign, 'degree': round(saturn % 30, 2)},
        'interpretation': health_interp,
        'generated_at': now.strftime('%Y-%m-%d %H:%M:%S'),
    })


@app.route("/api/horoscope/compatibility")
def api_horoscope_compatibility():
    """Compatibility (synastry) overview — element/modality compatibility matrix."""
    now = datetime.now(TZ)

    # Element compatibility
    elements = {
        'Fire': {'best': ['Fire', 'Air'], 'challenging': ['Water'], 'neutral': ['Earth']},
        'Earth': {'best': ['Earth', 'Water'], 'challenging': ['Air'], 'neutral': ['Fire']},
        'Air': {'best': ['Air', 'Fire'], 'challenging': ['Earth'], 'neutral': ['Water']},
        'Water': {'best': ['Water', 'Earth'], 'challenging': ['Fire'], 'neutral': ['Air']},
    }

    # Modality compatibility
    modalities = {
        'Cardinal': {'best': ['Cardinal'], 'challenging': ['Fixed'], 'neutral': ['Mutable']},
        'Fixed': {'best': ['Fixed'], 'challenging': ['Cardinal'], 'neutral': ['Mutable']},
        'Mutable': {'best': ['Mutable'], 'challenging': [], 'neutral': ['Cardinal', 'Fixed']},
    }

    # Sign pairings (simplified synastry)
    sign_compat = []
    for s1, g1, r1, m1, e1 in _ZODIAC_SIGNS_FULL:
        for s2, g2, r2, m2, e2 in _ZODIAC_SIGNS_FULL:
            if s1 == s2:
                score = 70  # Same sign — comfortable but can stagnate
                note = 'Comfortable, familiar energy'
            elif e1 == e2:
                score = 85  # Same element — natural harmony
                note = 'Natural harmony and understanding'
            elif (e1 in elements[e2]['best']):
                score = 80  # Complementary elements
                note = 'Complementary and energizing'
            elif (e1 in elements[e2]['challenging']):
                score = 45  # Challenging elements
                note = 'Requires patience and understanding'
            else:
                score = 65
                note = 'Balanced with effort'
            sign_compat.append({
                'sign1': s1, 'glyph1': g1,
                'sign2': s2, 'glyph2': g2,
                'score': score,
                'note': note,
            })

    return jsonify({
        'date': now.strftime('%A, %B %d, %Y'),
        'elements': elements,
        'modalities': modalities,
        'compatibility': sign_compat,
        'generated_at': now.strftime('%Y-%m-%d %H:%M:%S'),
    })


@app.route("/")
def home():
    resp = make_response(render_template("index.html"))
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp

if __name__ == "__main__":
    import socket
    def find_port(start=5488):
        port = start
        while True:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.bind(('127.0.0.1', port))
                s.close()
                return port
            except OSError:
                port += 1
    port = find_port()
    print(f"✨ Lilly's Dashboard v5.0 — http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
