"""Natal Charts — CRUD, calculation, transit overlay."""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone, timedelta
from pathlib import Path

import swisseph as swe
from flask import Blueprint, jsonify, request

from app.config import (
    ROOT, TZ, SIGNS, PLANET_SYMBOLS, PLANET_COLORS, PLANET_ENERGY,
    load_json, get_sign_info, calc_planet_pos,
)

bp = Blueprint('natal', __name__, url_prefix='/api/natal')

PROFILES_FILE = ROOT / 'data' / 'profiles.json'


def _load_profiles() -> list:
    if PROFILES_FILE.exists():
        with open(PROFILES_FILE) as f:
            return json.load(f)
    return []


def _save_profiles(profiles: list) -> None:
    PROFILES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PROFILES_FILE, 'w') as f:
        json.dump(profiles, f, indent=2)


def _calc_aspects(results: dict) -> list:
    """Calculate aspects between all planets in results dict."""
    aspects_list = []
    major_orbs = {'conjunction': 8.0, 'sextile': 6.0, 'square': 8.0, 'trine': 8.0, 'opposition': 8.0}
    minor_orbs = {'semi-sextile': 2.0, 'semi-square': 2.0, 'quintile': 1.5, 'sesquiquadrate': 2.0, 'biquintile': 1.5, 'quincunx': 3.0}
    aspect_angles = {'conjunction': 0, 'semi-sextile': 30, 'semi-square': 45, 'sextile': 60,
        'quintile': 72, 'square': 90, 'trine': 120, 'sesquiquadrate': 135, 'biquintile': 144, 'quincunx': 150, 'opposition': 180}
    aspect_symbols = {'conjunction': '☌', 'sextile': '⚹', 'square': '□', 'trine': '△', 'opposition': '☍',
        'semi-sextile': '╱', 'semi-square': '∠', 'quintile': 'Q', 'sesquiquadrate': '⚼', 'biquintile': 'BQ', 'quincunx': '⚻'}

    planet_names = list(results.keys())
    for i, p1_name in enumerate(planet_names):
        for j, p2_name in enumerate(planet_names):
            if j <= i:
                continue
            p1 = results[p1_name]
            p2 = results[p2_name]
            lon1 = p1['longitude']
            lon2 = p2['longitude']
            diff = abs(lon1 - lon2) % 360
            if diff > 180:
                diff = 360 - diff

            for aspect_name, angle in aspect_angles.items():
                orb = major_orbs.get(aspect_name, minor_orbs.get(aspect_name, 2.0))
                if abs(diff - angle) <= orb:
                    aspects_list.append({
                        'p1': p1_name, 'p2': p2_name,
                        'aspect': aspect_name.capitalize(),  # Frontend expects capitalized
                        'symbol': aspect_symbols.get(aspect_name, ''),
                        'orb': round(abs(diff - angle), 2),
                        'angle': angle,
                        'p1_color': PLANET_COLORS.get(p1_name, '#fff'),
                        'p2_color': PLANET_COLORS.get(p2_name, '#fff'),
                        'p1_symbol': PLANET_SYMBOLS.get(p1_name, ''),
                        'p2_symbol': PLANET_SYMBOLS.get(p2_name, ''),
                    })
                    break
    return aspects_list


@bp.route('/chart', methods=['POST'])
def api_calc_natal():
    """Calculate a full natal chart from birth data."""
    data = request.json or {}
    try:
        year = int(data.get('year', 1981))
        month = int(data.get('month', 10))
        day = int(data.get('day', 30))
        hour = float(data.get('hour', 3.1))
        lat = float(data.get('lat', -33.7367))
        lon = float(data.get('lon', 25.3983))
        tz_offset = float(data.get('tz_offset', 2))
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid birth data'}), 4000

    # If chart_id provided, load from profiles
    chart_id = data.get('chart_id')
    if chart_id:
        profiles = _load_profiles()
        for p in profiles:
            if p.get('id') == chart_id:
                year = int(p['birth_date'][:4])
                month = int(p['birth_date'][5:7])
                day = int(p['birth_date'][8:10])
                hour = float(p['birth_time'][:2]) + float(p['birth_time'][3:]) / 60
                lat = float(p.get('latitude', p.get('lat', -33.7367)))
                lon = float(p.get('longitude', p.get('lon', 25.3983)))
                tz_offset = float(p.get('timezone_offset', p.get('tz_offset', 2)))
                chart_name = p.get('name', 'Unnamed')
                chart_location = p.get('location', '')
                break
        else:
            chart_name = 'Unnamed'
            chart_location = ''
    else:
        chart_name = data.get('name', 'Unnamed')
        chart_location = data.get('location', '')

    ut = hour - tz_offset
    jd = swe.julday(year, month, day, ut)
    delta_t = swe.deltat(jd)
    jd_et = jd + delta_t

    planets = [
        (swe.SUN, 'Sun'), (swe.MOON, 'Moon'), (swe.MERCURY, 'Mercury'),
        (swe.VENUS, 'Venus'), (swe.MARS, 'Mars'), (swe.JUPITER, 'Jupiter'),
        (swe.SATURN, 'Saturn'), (swe.URANUS, 'Uranus'), (swe.NEPTUNE, 'Neptune'),
        (swe.PLUTO, 'Pluto'), (swe.CHIRON, 'Chiron'),
    ]
    results = {}
    for sid, name in planets:
        p = calc_planet_pos(jd_et, sid, name)
        if p:
            results[name] = p

    # House cusps (Placidus)
    cusps, ascmc = swe.houses_ex(jd_et, lat, lon, b'P')
    asc_deg = ascmc[0]
    mc_deg = ascmc[1]
    houses = {}
    for i in range(12):
        houses[f'house_{i+1}'] = get_sign_info(cusps[i])

    # Calculate aspects
    aspects = _calc_aspects(results)

    return jsonify({
        'planets': results,
        'ascendant': get_sign_info(asc_deg),
        'midheaven': get_sign_info(mc_deg),
        'houses': houses,
        'aspects': aspects,
        'name': chart_name,
        'birth_date': f"{year:04d}-{month:02d}-{day:02d}",
        'birth_time': f"{int(hour):02d}:{int((hour % 1) * 60):02d}",
        'location': chart_location,
        'latitude': lat,
        'longitude': lon,
        'tz_offset': tz_offset,
    })


@bp.route('/charts', methods=['GET'])
def api_natal_charts():
    profiles = _load_profiles()
    return jsonify(profiles)


@bp.route('/chart/save', methods=['POST'])
def api_natal_chart_save():
    profiles = _load_profiles()
    data = request.json or {}
    data['id'] = len(profiles) + 1
    data['created'] = datetime.now(TZ).isoformat()
    profiles.append(data)
    _save_profiles(profiles)
    return jsonify({'ok': True, 'id': data['id']})


@bp.route('/chart/<int:chart_id>', methods=['PUT'])
def api_natal_chart_update(chart_id):
    profiles = _load_profiles()
    data = request.json or {}
    for i, p in enumerate(profiles):
        if p.get('id') == chart_id:
            profiles[i].update(data)
            _save_profiles(profiles)
            return jsonify({'ok': True})
    return jsonify({'error': 'Chart not found'}), 404


@bp.route('/chart/<int:chart_id>', methods=['DELETE'])
def api_natal_chart_delete(chart_id):
    profiles = _load_profiles()
    profiles = [p for p in profiles if p.get('id') != chart_id]
    _save_profiles(profiles)
    return jsonify({'ok': True})