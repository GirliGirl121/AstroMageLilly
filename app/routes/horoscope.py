"""Horoscopes — daily, weekly, monthly, love, career, health, compatibility."""
from __future__ import annotations

import math
import random
from datetime import datetime, timezone, timedelta

import swisseph as swe
from flask import Blueprint, jsonify, request

from app.config import TZ, SIGNS, PLANET_ENERGY, calc_planet_pos

bp = Blueprint('horoscope', __name__, url_prefix='/api/horoscope')

PLANET_IDS = [
    (swe.SUN, 'Sun'), (swe.MOON, 'Moon'), (swe.MERCURY, 'Mercury'),
    (swe.VENUS, 'Venus'), (swe.MARS, 'Mars'), (swe.JUPITER, 'Jupiter'),
    (swe.SATURN, 'Saturn'), (swe.URANUS, 'Uranus'), (swe.NEPTUNE, 'Neptune'),
    (swe.PLUTO, 'Pluto'), (swe.CHIRON, 'Chiron'),
]

# ─── Calculation Helpers ─────────────────────────────────────────────────

def _get_current_planets():
    """Get current planetary positions via Swiss Ephemeris."""
    utc = datetime.now(TZ).astimezone(timezone.utc)
    jd = swe.julday(utc.year, utc.month, utc.day, utc.hour + utc.minute/60 + utc.second/3600)
    positions = []
    for sid, name in PLANET_IDS:
        p = calc_planet_pos(jd, sid, name)
        if p:
            positions.append(p)
    return positions


def _calc_aspects(positions):
    """Calculate aspects between all planets."""
    aspects_list = []
    major_orbs = {'conjunction': 8.0, 'sextile': 6.0, 'square': 8.0, 'trine': 8.0, 'opposition': 8.0}
    minor_orbs = {'semi-sextile': 2.0, 'semi-square': 2.0, 'quintile': 1.5, 'sesquiquadrate': 2.0, 'biquintile': 1.5, 'quincunx': 3.0}
    aspect_angles = {'conjunction': 0, 'semi-sextile': 30, 'semi-square': 45, 'sextile': 60,
        'quintile': 72, 'square': 90, 'trine': 120, 'sesquiquadrate': 135, 'biquintile': 144, 'quincunx': 150, 'opposition': 180}
    aspect_symbols = {'conjunction': '☌', 'sextile': '⚹', 'square': '□', 'trine': '△', 'opposition': '☍',
        'semi-sextile': '╱', 'semi-square': '∠', 'quintile': 'Q', 'sesquiquadrate': '⚼', 'biquintile': 'BQ', 'quincunx': '⚻'}

    for i, p1 in enumerate(positions):
        for j, p2 in enumerate(positions):
            if j <= i:
                continue
            lon1 = p1['longitude']
            lon2 = p2['longitude']
            diff = abs(lon1 - lon2) % 360
            if diff > 180:
                diff = 360 - diff

            for aspect_name, angle in aspect_angles.items():
                orb = major_orbs.get(aspect_name, minor_orbs.get(aspect_name, 2.0))
                if abs(diff - angle) <= orb:
                    applying = False  # simplified
                    aspects_list.append({
                        'planet1': p1['name'], 'planet2': p2['name'],
                        'aspect': aspect_name, 'symbol': aspect_symbols.get(aspect_name, ''),
                        'orb': round(abs(diff - angle), 2), 'angle': angle,
                        'applying': applying,
                    })
                    break
    return aspects_list


def _moon_phase_text(moon_lon, sun_lon):
    """Simplified moon phase text."""
    diff = (moon_lon - sun_lon) % 360
    if diff < 45 or diff >= 315:
        return 'New Moon', '🌑'
    elif diff < 90:
        return 'Waxing Crescent', '🌒'
    elif diff < 135:
        return 'First Quarter', '🌓'
    elif diff < 180:
        return 'Waxing Gibbous', '🌔'
    elif diff < 225:
        return 'Full Moon', '🌕'
    elif diff < 270:
        return 'Waning Gibbous', '🌖'
    elif diff < 315:
        return 'Last Quarter', '🌗'
    return 'Waning Crescent', '🌘'


def _interpret_sign_transit(sign, transiting_planets):
    """Generate transit interpretation for a sign."""
    sign_name = sign[0]
    interpretations = []
    for p in transiting_planets:
        if p.get('sign') == sign_name:
            energy = PLANET_ENERGY.get(p['name'], ('✨', ''))
            interp = f"{p['name']} ({p.get('symbol','')}) in {sign_name}: {energy[1]}"
            interpretations.append(interp)
    return interpretations


def _interpret_aspect(aspect, p1, p2, orb):
    """Interpret an aspect between two planets."""
    templates = {
        'conjunction': f"{p1} and {p2} are meeting — a fusion of energies within {orb:.1f}° orb",
        'sextile': f"{p1} is flowing harmoniously with {p2} — opportunity within {orb:.1f}°",
        'square': f"{p1} is challenging {p2} — tension and growth within {orb:.1f}°",
        'trine': f"{p1} supports {p2} with grace — ease within {orb:.1f}°",
        'opposition': f"{p1} opposes {p2} — balance needed within {orb:.1f}°",
    }
    return templates.get(aspect, f"{p1} {aspect} {p2}")


# ─── Horoscope Routes ────────────────────────────────────────────────────

@bp.route('/daily')
def api_horoscope_daily():
    """Daily horoscope with planetary transits and aspects."""
    from app.config import get_moon_phase_obj
    planets = _get_current_planets()
    aspects = _calc_aspects(planets)
    moon_data = get_moon_phase_obj()
    sun_pos = next((p for p in planets if p['name'] == 'Sun'), {})
    sun_sign = sun_pos.get('sign', 'Unknown')

    sign_interpretations = {}
    for sign in SIGNS:
        interps = _interpret_sign_transit(sign, planets)
        if interps:
            sign_interpretations[sign[0]] = interps

    major_aspects = [a for a in aspects if a['aspect'] in ('conjunction','sextile','square','trine','opposition')]
    aspect_interpretations = []
    for a in major_aspects[:7]:
        aspect_interpretations.append(
            _interpret_aspect(a['aspect'], a['planet1'], a['planet2'], a['orb'])
        )

    return jsonify({
        'sign': sun_sign,
        'moon_phase': moon_data['phase'],
        'moon_emoji': moon_data['emoji'],
        'transits': planets[:8],
        'aspects': major_aspects[:7],
        'aspect_interpretations': aspect_interpretations,
        'sign_interpretations': sign_interpretations,
    })


@bp.route('/weekly')
def api_horoscope_weekly():
    return jsonify({
        'week': datetime.now(TZ).strftime('%V'),
        'focus': random.choice(['Relationships', 'Career', 'Inner growth', 'Communication', 'Rest', 'Creativity']),
        'message': 'The week ahead — review your Mercury and Venus transits.',
        'summary': 'Notice patterns in your daily rhythm. The cosmos supports reflection.',
    })


@bp.route('/monthly')
def api_horoscope_monthly():
    return jsonify({
        'month': datetime.now(TZ).strftime('%B %Y'),
        'focus': random.choice(['Transformation', 'Expansion', 'Discipline', 'Emotional depth', 'Innovation']),
        'planetary_influences': 'Saturn, Jupiter, and the Moon drive this month\'s themes.',
        'advice': 'Build slowly, trust the process, and journal your dreams.',
    })


@bp.route('/love')
def api_horoscope_love():
    planets = _get_current_planets()
    venus = next((p for p in planets if p['name'] == 'Venus'), None)
    mars = next((p for p in planets if p['name'] == 'Mars'), None)
    return jsonify({
        'venus_sign': venus.get('sign', 'Unknown') if venus else 'Unknown',
        'mars_sign': mars.get('sign', 'Unknown') if mars else 'Unknown',
        'venus_retrograde': 'yes' if (venus and venus.get('retrograde')) else 'no',
        'mars_retrograde': 'yes' if (mars and mars.get('retrograde')) else 'no',
        'message': 'Venus and Mars reveal the dance of love and desire. Their current positions:',
        'advice': 'Look at your natal Venus and Mars for deeper insight.',
    })


@bp.route('/career')
def api_horoscope_career():
    planets = _get_current_planets()
    saturn = next((p for p in planets if p['name'] == 'Saturn'), None)
    jupiter = next((p for p in planets if p['name'] == 'Jupiter'), None)
    return jsonify({
        'saturn_sign': saturn.get('sign', 'Unknown') if saturn else 'Unknown',
        'jupiter_sign': jupiter.get('sign', 'Unknown') if jupiter else 'Unknown',
        'message': 'Saturn governs career, Jupiter governs expansion. Their transits:',
        'advice': 'Discipline meets opportunity — review your 10th house transits.',
    })


@bp.route('/health')
def api_horoscope_health():
    planets = _get_current_planets()
    moon = next((p for p in planets if p['name'] == 'Moon'), None)
    return jsonify({
        'moon_sign': moon.get('sign', 'Unknown') if moon else 'Unknown',
        'moon_phase': _moon_phase_text(
            moon.get('longitude', 0) if moon else 0,
            next((p.get('longitude', 0) for p in planets if p['name'] == 'Sun'), 0)
        ),
        'message': 'The Moon governs your emotional and physical rhythms.',
        'advice': 'Rest when the Moon is in a challenging aspect. Move when she flows.',
    })


@bp.route('/compatibility')
def api_horoscope_compatibility():
    sign1 = request.args.get('sign1', '').strip()
    sign2 = request.args.get('sign2', '').strip()
    if not sign1 or not sign2:
        return jsonify({'error': 'Please provide sign1 and sign2 parameters'}), 400
    compat_map = {
        ('Aries','Libra'): ('Opposition — polarity creates dynamic balance', 70),
        ('Taurus','Scorpio'): ('Opposition — deep transformative potential', 75),
        ('Gemini','Sagittarius'): ('Opposition — shared curiosity, different expression', 80),
        ('Cancer','Capricorn'): ('Opposition — nurture meets structure', 65),
        ('Leo','Aquarius'): ('Opposition — creative self-expression meets collective vision', 85),
        ('Virgo','Pisces'): ('Opposition — detail meets dream', 70),
    }
    key = (sign1.capitalize(), sign2.capitalize())
    rev = (sign2.capitalize(), sign1.capitalize())
    match = compat_map.get(key) or compat_map.get(rev)
    if not match:
        msg = f'{sign1} and {sign2} — a unique combination.'
        score = random.randint(40, 90)
        match = (msg, score)
    return jsonify({
        'sign1': sign1, 'sign2': sign2,
        'compatibility': match[0],
        'score': match[1],
        'aspects': ['Synastry analysis requires full birth charts for accuracy.'],
    })
