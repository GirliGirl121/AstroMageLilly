#!/usr/bin/env python3
"""
Calendar Engine for MagiJournal
Reads from picatrix_calendar.db and computes live astrological data using pyswisseph.

Location: Kariega, SA (lat -33.7367, lon 25.3983, alt 360m, tz UTC+2)

Provides: get_day_data, get_month_data, get_week_data, get_year_data
"""

import sqlite3
import json
import os
import sys
from datetime import datetime, timedelta, timezone

# Ensure swisseph is importable
sys.path.insert(0, '/home/ladylefey')

import swisseph as swe

# ─── Paths ────────────────────────────────────────────────────────────────────
DB_PATH = '/home/ladylefey/AstroMage/picatrix_calendar/picatrix_calendar.db'
EPHE_PATH = '/home/ladylefey/ephe'
MANSIONS_JSON = '/home/ladylefey/AstroMage/picatrix_mansions.json'
ELECTIONS_JSON = '/home/ladylefey/AstroMage/picatrix_elections.json'
CORRESP_JSON = '/home/ladylefey/AstroMage/picatrix_planetary_correspondences.json'

# ─── Research JSON Data Loader ──────────────────────────────────────────────
_RICH_MANSIONS = None
_RICH_ELECTIONS = None
_RICH_CORRESP = None

def _load_research_data():
    """Load Picatrix research JSON data from the AstroMage project."""
    global _RICH_MANSIONS, _RICH_ELECTIONS, _RICH_CORRESP
    if _RICH_MANSIONS is None and os.path.exists(MANSIONS_JSON):
        try:
            with open(MANSIONS_JSON, 'r') as f:
                _RICH_MANSIONS = json.load(f)
        except Exception:
            _RICH_MANSIONS = {}
    if _RICH_ELECTIONS is None and os.path.exists(ELECTIONS_JSON):
        try:
            with open(ELECTIONS_JSON, 'r') as f:
                _RICH_ELECTIONS = json.load(f)
        except Exception:
            _RICH_ELECTIONS = {}
    if _RICH_CORRESP is None and os.path.exists(CORRESP_JSON):
        try:
            with open(CORRESP_JSON, 'r') as f:
                _RICH_CORRESP = json.load(f)
        except Exception:
            _RICH_CORRESP = {}
    return _RICH_MANSIONS is not None


def _get_rich_mansion(mansion_index):
    """Get the rich mansion data from the research JSON (0-indexed to 1-indexed)."""
    _load_research_data()
    if not _RICH_MANSIONS:
        return None
    mansions = _RICH_MANSIONS.get('mansions', [])
    # json is 1-indexed
    for m in mansions:
        if m.get('number') == mansion_index + 1:
            return m
    return None


def _get_mansion_pliny_image(mansion_index):
    """Get the Pliny image data for a mansion from the research JSON."""
    m = _get_rich_mansion(mansion_index)
    if m and 'pliny_image' in m:
        return m['pliny_image']
    return None


def _get_mansion_spirit_name(mansion_index):
    """Get the lord of the mansion spirit from the research JSON."""
    m = _get_rich_mansion(mansion_index)
    if m:
        return m.get('lord_of_mansion_spirit', '')
    return ''


def _get_mansion_nature(mansion_index):
    """Get the nature (hot/cold/moist/dry) of a mansion."""
    m = _get_rich_mansion(mansion_index)
    if m:
        return m.get('nature', '')
    return ''


def _get_elections_for_day_category(date_str, day_ruler, moon_sign):
    """Get electional entries matching the day's astrological features."""
    matches = []
    _load_research_data()
    if not _RICH_ELECTIONS:
        return matches
    rules = _RICH_ELECTIONS.get('electional_timing_rules', {})
    # Check by day
    for category, elections_list in rules.items():
        if isinstance(elections_list, list):
            for e in elections_list:
                planet_match = e.get('planet', '') == day_ruler
                sign_match = e.get('sign', '') == moon_sign
                if planet_match or sign_match:
                    matches.append({
                        'category': category,
                        'operation': e.get('operation', e.get('text', ''))[:80],
                        'description': e.get('description', '') or e.get('text', '')[:120],
                        'citation': e.get('citation', ''),
                    })
    return matches[:5]


# ─── Location: Kariega, South Africa ─────────────────────────────────────────
LAT = -(33 + 44 / 60 + 7 / 3600)  # -33.7367
LON = 25 + 23 / 60 + 49 / 3600    # 25.3983
ALT = 360
TZ = timezone(timedelta(hours=2))

# ─── Chaldean Order ───────────────────────────────────────────────────────────
CHALEDEAN = ['Saturn', 'Jupiter', 'Mars', 'Sun', 'Venus', 'Mercury', 'Moon']
CHALEDEAN_AR = ['Zuhal زحل', 'Mushtari المشتري', 'Mirih المريخ', 'Shams الشمس',
                'Zuhra الزهرة', 'Utarid عطارد', 'Qamar القمر']
VEDIC_NAMES = ['Shani', 'Guru/Brihaspati', 'Mangala/Kuja', 'Surya',
                'Shukra', 'Budha', 'Chandra']

# ─── Day Rulers (Monday=Moon, Tuesday=Mars, etc.) ────────────────────────────
DAY_RULERS = {
    0: 'Moon', 1: 'Mars', 2: 'Mercury', 3: 'Jupiter',
    4: 'Venus', 5: 'Saturn', 6: 'Sun'
}

# ─── Picatrix Spirits (from Picatrix Book II) ────────────────────────────────
PICATRIX_SPIRITS = {
    'Sun':    {'name': 'Beydeluz',   'arabic': 'Bandalus بندلوس',    'angel': 'Nakkiel'},
    'Venus':  {'name': 'Deydez',    'arabic': 'Didas ديداس',        'angel': 'Beyteyl'},
    'Mercury': {'name': 'Merhuyez',  'arabic': 'Barhujas برحوجاس',   'angel': 'Taphthartharath'},
    'Moon':   {'name': 'Harnuz',    'arabic': 'Garnus قرنوس',       'angel': 'Arquyl'},
    'Saturn': {'name': 'Redimez',   'arabic': 'Tus طوس',            'angel': 'Myndis'},
    'Jupiter': {'name': 'Demehuz',   'arabic': 'Damahas داماحاس',    'angel': 'Raucahehil'},
    'Mars':   {'name': 'Deharayuz', 'arabic': 'Dagdijus داجداس',    'angel': 'Graphiel'},
}

# ─── Zodiac Signs ─────────────────────────────────────────────────────────────
ZODIAC_SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

# ─── Aspect Definitions ──────────────────────────────────────────────────────
ASPECT_TYPES = {0: 'Conjunction', 60: 'Sextile', 90: 'Square', 120: 'Trine', 180: 'Opposition'}
ASPECT_SYMBOLS = {0: '☌', 60: '✶', 90: '□', 120: '△', 180: '☍'}

# ─── Planet IDs for swisseph ─────────────────────────────────────────────────
PLANET_IDS = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mercury': swe.MERCURY,
    'Venus': swe.VENUS, 'Mars': swe.MARS, 'Jupiter': swe.JUPITER,
    'Saturn': swe.SATURN,
}
PLANET_NAMES = list(PLANET_IDS.keys())


def _julday(dt):
    """Convert a datetime to Julian Day (UTC)."""
    utc = dt.astimezone(timezone.utc)
    return swe.julday(utc.year, utc.month, utc.day,
                      utc.hour + utc.minute / 60 + utc.second / 3600)


def _revjul(jd):
    """Convert Julian Day back to (year, month, day, hour_fraction)."""
    return swe.revjul(jd)


# ─── Database helpers ─────────────────────────────────────────────────────────
def _get_db():
    """Get a database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _get_mansion_reference(mansion_idx):
    """Get mansion details from the database lunar_mansions_reference table."""
    conn = _get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM lunar_mansions_reference WHERE mansion_index = ?",
        (mansion_idx,)
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        result = dict(row)
        # Enrich with research JSON data
        spirit_name = _get_mansion_spirit_name(mansion_idx)
        if spirit_name:
            result['mansion_spirit_name'] = spirit_name
        nature = _get_mansion_nature(mansion_idx)
        if nature:
            result['mansion_nature'] = nature
        pliny = _get_mansion_pliny_image(mansion_idx)
        if pliny:
            result['pliny_image'] = pliny
        return result
    return None


def _get_elections_for_day(date_str, day_ruler):
    """Get electional entries matching a specific day."""
    conn = _get_db()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT operation, rating, description, picatrix_reference 
           FROM elections 
           WHERE date = ? OR day_ruler = ? OR planet = ?
           ORDER BY rating DESC LIMIT 5""",
        (date_str, day_ruler, day_ruler)
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def _get_correspondences(planet):
    """Get planetary correspondences from DB."""
    conn = _get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT category, item FROM planetary_correspondences WHERE planet = ? ORDER BY category, item",
        (planet,)
    )
    result = {}
    for row in cursor.fetchall():
        cat = row['category']
        if cat not in result:
            result[cat] = []
        result[cat].append(row['item'])
    conn.close()
    return result


def _get_talismanic_timing(planet, day_ruler, hour_ruler):
    """Get talismanic timing rules matching the current configuration."""
    conn = _get_db()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT operation, required_day, required_hour, description, picatrix_reference
           FROM talismanic_timings 
           WHERE planet = ? OR required_day = ? OR required_hour = ?
           LIMIT 5""",
        (planet, day_ruler, hour_ruler)
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


# ─── Core Calculations ────────────────────────────────────────────────────────
def compute_sunrise_sunset(date):
    """Compute sunrise, sunset, next sunrise for a date at Kariega."""
    jd = swe.julday(date.year, date.month, date.day, 0.0)
    geopos = (LON, LAT, ALT)

    rise_result = swe.rise_trans(jd, swe.SUN, swe.CALC_RISE, geopos, 0, 0, swe.FLG_SWIEPH)
    set_result = swe.rise_trans(jd, swe.SUN, swe.CALC_SET, geopos, 0, 0, swe.FLG_SWIEPH)
    next_rise_result = swe.rise_trans(jd + 1, swe.SUN, swe.CALC_RISE, geopos, 0, 0, swe.FLG_SWIEPH)

    sunrise_jd = rise_result[1][0]
    sunset_jd = set_result[1][0]
    next_sunrise_jd = next_rise_result[1][0]

    return sunrise_jd, sunset_jd, next_sunrise_jd


def compute_moon_position(dt):
    """Get Moon's tropical longitude, sign, and mansion for a given datetime."""
    jd = _julday(dt)
    moon = swe.calc_ut(jd, swe.MOON)
    moon_lon = moon[0][0]

    sign_idx = int(moon_lon / 30)
    sign_deg = moon_lon % 30
    sign = ZODIAC_SIGNS[sign_idx]

    # 27 lunar mansions, each 13°20' (360/27 ≈ 13.333°)
    mansion_idx = int(moon_lon / (360 / 27))
    mansion_start = mansion_idx * (360 / 27)
    mansion_deg_in = moon_lon - mansion_start

    return {
        'longitude': round(moon_lon, 4),
        'sign': sign,
        'sign_degree': round(sign_deg, 2),
        'mansion_index': mansion_idx,
        'mansion_degree_in': round(mansion_deg_in, 2),
    }


def compute_aspects(dt, orb=3.0):
    """Compute major aspects between transiting planets."""
    jd = _julday(dt)

    positions = {}
    for name, pid in PLANET_IDS.items():
        pos = swe.calc_ut(jd, pid)
        positions[name] = pos[0][0]

    aspects = []
    names = list(positions.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            p1, p2 = names[i], names[j]
            diff = abs(positions[p1] - positions[p2])
            if diff > 180:
                diff = 360 - diff
            for angle, aspect_name in ASPECT_TYPES.items():
                actual_orb = abs(diff - angle)
                if actual_orb <= orb:
                    # Determine applying vs separating
                    raw_diff = (positions[p1] - positions[p2]) % 360
                    applying = 'applying' if raw_diff < 180 else 'separating'
                    aspects.append({
                        'p1': p1,
                        'p2': p2,
                        'aspect': aspect_name,
                        'symbol': ASPECT_SYMBOLS[angle],
                        'orb': round(actual_orb, 2),
                        'applying': applying,
                    })

    # Sort by orb (tightest first)
    aspects.sort(key=lambda x: x['orb'])
    return aspects


def compute_planetary_hours(dt):
    """Calculate all 24 planetary hours for a given datetime."""
    utc = dt.astimezone(timezone.utc)
    jd = swe.julday(utc.year, utc.month, utc.day,
                     utc.hour + utc.minute / 60 + utc.second / 3600)

    sunrise_jd, sunset_jd, next_sunrise_jd = compute_sunrise_sunset(utc)

    day_length = (sunset_jd - sunrise_jd) * 86400
    night_length = (next_sunrise_jd - sunset_jd) * 86400
    day_hour_len = day_length / 12
    night_hour_len = night_length / 12

    dow = dt.weekday()  # Monday=0
    day_ruler = DAY_RULERS[dow]
    day_idx = CHALEDEAN.index(day_ruler)

    hours = []

    # Day hours (0-11)
    for i in range(12):
        h_start_jd = sunrise_jd + (i * day_hour_len / 86400)
        h_end_jd = h_start_jd + (day_hour_len / 86400)
        ruler_idx = (day_idx + i) % 7
        planet = CHALEDEAN[ruler_idx]
        spirit = PICATRIX_SPIRITS[planet]

        hours.append({
            'hour_number': i,
            'period': 'day',
            'planet': planet,
            'planet_ar': CHALEDEAN_AR[ruler_idx],
            'planet_vedic': VEDIC_NAMES[ruler_idx],
            'spirit_name': spirit['name'],
            'spirit_arabic': spirit['arabic'],
            'spirit_angel': spirit['angel'],
            'start_jd': h_start_jd,
            'end_jd': h_end_jd,
            'duration_min': round(day_hour_len / 60, 1),
        })

    # Night hours (12-23)
    for i in range(12):
        h_start_jd = sunset_jd + (i * night_hour_len / 86400)
        h_end_jd = h_start_jd + (night_hour_len / 86400)
        overall = 12 + i
        ruler_idx = (day_idx + overall) % 7
        planet = CHALEDEAN[ruler_idx]
        spirit = PICATRIX_SPIRITS[planet]

        hours.append({
            'hour_number': overall,
            'period': 'night',
            'planet': planet,
            'planet_ar': CHALEDEAN_AR[ruler_idx],
            'planet_vedic': VEDIC_NAMES[ruler_idx],
            'spirit_name': spirit['name'],
            'spirit_arabic': spirit['arabic'],
            'spirit_angel': spirit['angel'],
            'start_jd': h_start_jd,
            'end_jd': h_end_jd,
            'duration_min': round(night_hour_len / 60, 1),
        })

    return hours, sunrise_jd, sunset_jd, next_sunrise_jd


def compute_recommendations(dt, moon_info, aspects, day_ruler):
    """Generate recommendations and avoidances based on astrological data."""
    recommendations = []
    avoid = []

    # Moon mansion-based recommendations
    mansion_idx = moon_info['mansion_index']
    mansion_ref = _get_mansion_reference(mansion_idx)
    if mansion_ref:
        works = mansion_ref.get('recommended_works', '')
        if works:
            if isinstance(works, str):
                try:
                    works = json.loads(works)
                except (json.JSONDecodeError, TypeError):
                    works = [works]
            if isinstance(works, list):
                recommendations.extend(works[:3])

        forbidden = mansion_ref.get('forbidden_works', '')
        if forbidden:
            if isinstance(forbidden, str) and forbidden.strip():
                avoid.append(forbidden)

    # Day ruler recommendations (from DB correspondences)
    correspondences = _get_correspondences(day_ruler)
    if correspondences:
        if 'colors' in correspondences:
            recommendations.append(f"Wear: {', '.join(correspondences['colors'][:3])}")
        if 'incense' in correspondences:
            recommendations.append(f"Incense: {', '.join(correspondences['incense'][:2])}")
        if 'stone' in correspondences:
            recommendations.append(f"Stone: {', '.join(correspondences['stone'][:2])}")

    # Day ruler recommendations from rich research JSON
    _load_research_data()
    if _RICH_CORRESP and 'planets' in _RICH_CORRESP:
        planet_data = _RICH_CORRESP['planets'].get(day_ruler, {})
        if planet_data:
            # Colors
            colors = planet_data.get('colors', {})
            garment = colors.get('garment_colors', '')
            if garment:
                recommendations.append(f"Garment: {garment}")
            # Incenses
            incenses = planet_data.get('incenses_suffumigations', [])
            if incenses and len(incenses) > 0:
                recommendations.append(f"Suffumigation: {incenses[0][:40]}")
            # Nature
            nature = planet_data.get('nature', '')
            if nature:
                recommendations.append(f"Nature: {nature}")

    # Aspect-based advice
    for aspect in aspects:
        if aspect['orb'] < 1.5:
            if aspect['aspect'] in ('Trine', 'Sextile'):
                recommendations.append(
                    f"Strong {aspect['aspect']} {aspect['p1']}-{aspect['p2']} (orb {aspect['orb']}°): favorable for new endeavors"
                )
            elif aspect['aspect'] in ('Square', 'Opposition'):
                avoid.append(
                    f"Tense {aspect['aspect']} {aspect['p1']}-{aspect['p2']} (orb {aspect['orb']}°): avoid conflicts"
                )
            elif aspect['aspect'] == 'Conjunction':
                recommendations.append(
                    f"Powerful {aspect['p1']}-{aspect['p2']} conjunction (orb {aspect['orb']}°): potent time for intention"
                )

    # Talismanic timing check
    talismans = _get_talismanic_timing(day_ruler, day_ruler, day_ruler)
    for t in talismans:
        if t.get('required_day') == day_ruler:
            recommendations.append(f"Talismanic: {t['operation']} — {t.get('description', '')[:80]}")

    # Deduplicate
    seen_rec = set()
    seen_avoid = set()
    unique_rec = []
    unique_avoid = []
    for r in recommendations:
        if r not in seen_rec:
            seen_rec.add(r)
            unique_rec.append(r)
    for a in avoid:
        if a not in seen_avoid:
            seen_avoid.add(a)
            unique_avoid.append(a)

    return unique_rec[:8], unique_avoid[:5]


def _jd_to_local_str(jd):
    """Convert Julian Day to local time string (HH:MM SAST)."""
    y, m, d, h_float = _revjul(jd)
    hours = int(h_float)
    minutes = int((h_float % 1) * 60)
    return f"{hours:02d}:{minutes:02d} SAST"


# ─── Public API ───────────────────────────────────────────────────────────────
def get_day_data(date):
    """
    Get complete astrological data for a single day.

    Parameters:
        date: datetime.date or datetime.datetime or str 'YYYY-MM-DD'

    Returns:
        dict with keys:
            date, day_of_week, day_ruler, day_ruler_ar,
            sunrise, sunset,
            moon_sign, moon_mansion, mansion_spirit,
            aspects (list of {p1, p2, symbol, orb}),
            planetary_hours (list),
            recommendations (list), avoid (list)
    """
    # Parse date input
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d').date()
    if isinstance(date, datetime):
        date = date.date() if hasattr(date, 'date') else date

    dt = datetime(date.year, date.month, date.day, 12, 0, 0, tzinfo=TZ)

    # Day ruler
    dow = dt.weekday()
    day_ruler = DAY_RULERS[dow]
    day_ruler_ar = CHALEDEAN_AR[CHALEDEAN.index(day_ruler)]

    # Sunrise/sunset
    sunrise_jd, sunset_jd, next_sunrise_jd = compute_sunrise_sunset(date)
    sunrise_str = _jd_to_local_str(sunrise_jd)
    sunset_str = _jd_to_local_str(sunset_jd)

    # Moon position
    moon = compute_moon_position(dt)

    # Mansion reference from DB (enriched with research JSON)
    mansion_ref = _get_mansion_reference(moon['mansion_index'])
    moon_mansion = ''
    mansion_spirit = ''
    mansion_spirit_name = ''
    mansion_nature = ''
    pliny_image = None
    if mansion_ref:
        moon_mansion = mansion_ref.get('picatrix_name', '') or mansion_ref.get('name', '')
        mansion_spirit = mansion_ref.get('ruler_sign', '') or ''
        mansion_spirit_name = mansion_ref.get('mansion_spirit_name', '')
        mansion_nature = mansion_ref.get('mansion_nature', '')
        pliny_image = mansion_ref.get('pliny_image', None)

    # Aspects
    aspects = compute_aspects(dt)

    # Planetary hours
    hours, _, _, _ = compute_planetary_hours(dt)

    # Recommendations
    recommendations, avoid = compute_recommendations(dt, moon, aspects, day_ruler)

    # Electional data from DB + research JSON
    elections = _get_elections_for_day(date.isoformat(), day_ruler)
    rich_elections = _get_elections_for_day_category(date.isoformat(), day_ruler, moon['sign'])
    if rich_elections:
        # Merge, avoiding duplicates
        seen_ops = {e['operation'] for e in elections}
        for e in rich_elections:
            if e['operation'] not in seen_ops:
                elections.append(e)

    # Planetary correspondences
    correspondences = _get_correspondences(day_ruler)

    # Build dynamic Picatrix references
    picatrix_refs = []
    picatrix_refs.append("Picatrix Book IV, Ch.5 (Lunar Mansions)")
    picatrix_refs.append("Picatrix Book IV, Ch.9 (Spirits & Pliny Images)")
    picatrix_refs.append("Picatrix Book III (Planetary Properties & Operations)")
    if mansion_ref:
        refs = mansion_ref.get('picatrix_reference', '')
        if refs:
            for r in refs.split(';'):
                r = r.strip()
                if r and r not in picatrix_refs:
                    picatrix_refs.append(r)
    if elections:
        for e in elections:
            if e.get('citation') and e['citation'] not in picatrix_refs:
                picatrix_refs.append(e['citation'])
    # Deduplicate but keep order
    seen_refs = set()
    picatrix_refs = [r for r in picatrix_refs if not (r in seen_refs or seen_refs.add(r))]

    return {
        'date': date.isoformat(),
        'day_of_week': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][dow],
        'day_ruler': day_ruler,
        'day_ruler_ar': day_ruler_ar,
        'sunrise': sunrise_str,
        'sunset': sunset_str,
        'moon_sign': moon['sign'],
        'moon_mansion': moon_mansion,
        'mansion_spirit': mansion_spirit,
        'mansion_spirit_name': mansion_spirit_name,
        'mansion_nature': mansion_nature,
        'pliny_image': pliny_image,
        'moon_longitude': moon['longitude'],
        'moon_sign_degree': moon['sign_degree'],
        'mansion_index': moon['mansion_index'],
        'mansion_degree_in': moon['mansion_degree_in'],
        'aspects': aspects,
        'planetary_hours': hours,
        'recommendations': recommendations,
        'avoid': avoid,
        'elections': elections,
        'correspondences': correspondences,
        'picatrix_references': picatrix_refs,
    }


def get_month_data(year, month):
    """
    Get astrological data for every day in a month.

    Parameters:
        year: int
        month: int (1-12)

    Returns:
        list of day_data dicts (same format as get_day_data)
    """
    first_day = datetime(year, month, 1, tzinfo=TZ)
    if month == 12:
        last_day = datetime(year + 1, 1, 1, tzinfo=TZ) - timedelta(days=1)
    else:
        last_day = datetime(year, month + 1, 1, tzinfo=TZ) - timedelta(days=1)

    days = []
    current = first_day.date()
    end = last_day.date()
    while current <= end:
        day_data = get_day_data(current)
        days.append(day_data)
        current += timedelta(days=1)

    return days


def get_week_data(start_date):
    """
    Get astrological data for a 7-day week starting from start_date.

    Parameters:
        start_date: datetime.date or str 'YYYY-MM-DD'

    Returns:
        list of 7 day_data dicts
    """
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(start_date, datetime):
        start_date = start_date.date() if hasattr(start_date, 'date') else start_date

    days = []
    for i in range(7):
        d = start_date + timedelta(days=i)
        days.append(get_day_data(d))

    return days


def get_year_data(year):
    """
    Get monthly summaries for an entire year.

    Parameters:
        year: int

    Returns:
        list of 12 month summaries, each containing:
            year, month, month_name, days (list of day_data)
    """
    months = []
    for month in range(1, 13):
        month_days = get_month_data(year, month)
        months.append({
            'year': year,
            'month': month,
            'month_name': datetime(year, month, 1).strftime('%B'),
            'days': month_days,
        })

    return months


# ─── CLI / Testing ────────────────────────────────────────────────────────────
if __name__ == '__main__':
    import sys

    # Ensure ephe path exists
    if os.path.isdir(EPHE_PATH):
        swe.set_ephe_path(EPHE_PATH)

    print("🔮 Picatrix Calendar Engine")
    print("=" * 50)

    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == 'day':
            date_str = sys.argv[2] if len(sys.argv) > 2 else datetime.now(TZ).strftime('%Y-%m-%d')
            data = get_day_data(date_str)
            print(json.dumps(data, indent=2, ensure_ascii=False, default=str))
        elif cmd == 'month':
            now = datetime.now(TZ)
            year = int(sys.argv[2]) if len(sys.argv) > 2 else now.year
            month = int(sys.argv[3]) if len(sys.argv) > 3 else now.month
            data = get_month_data(year, month)
            print(f"Month: {year}-{month:02d} ({len(data)} days)")
            for d in data:
                print(f"  {d['date']} | {d['day_ruler']:8s} | Moon {d['moon_sign']:10s} | {len(d['aspects'])} aspects")
        elif cmd == 'week':
            date_str = sys.argv[2] if len(sys.argv) > 2 else datetime.now(TZ).strftime('%Y-%m-%d')
            data = get_week_data(date_str)
            print(f"Week starting {date_str}:")
            for d in data:
                print(f"  {d['date']} {d['day_of_week'][:3]} | {d['day_ruler']:8s} | Moon {d['moon_sign']:10s} | {len(d['aspects'])} aspects")
        elif cmd == 'year':
            year = int(sys.argv[2]) if len(sys.argv) > 2 else datetime.now(TZ).year
            data = get_year_data(year)
            print(f"Year {year}:")
            for m in data:
                print(f"  {m['month_name']:10s} ({len(m['days'])} days)")
    else:
        # Default: show today
        today = datetime.now(TZ).date()
        print(f"\n📅 Today: {today}")
        data = get_day_data(today)
        print(f"  Day Ruler: {data['day_ruler']} ({data['day_ruler_ar']})")
        print(f"  Sunrise: {data['sunrise']} | Sunset: {data['sunset']}")
        print(f"  Moon: {data['moon_sign']} {data['moon_sign_degree']}° | Mansion: {data['moon_mansion']}")
        print(f"  Aspects: {len(data['aspects'])}")
        for a in data['aspects'][:5]:
            print(f"    {a['symbol']} {a['p1']} {a['aspect']} {a['p2']} (orb {a['orb']}°)")
        print(f"  Recommendations: {len(data['recommendations'])}")
        for r in data['recommendations'][:3]:
            print(f"    ✓ {r[:60]}")
        print(f"  Avoid: {len(data['avoid'])}")
        for a in data['avoid'][:3]:
            print(f"    ✗ {a[:60]}")
        print(f"  Planetary Hours: {len(data['planetary_hours'])}")
