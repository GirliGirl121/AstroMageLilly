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
        return jsonify({'error': 'Invalid birth data'}), 400

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

    return jsonify({
        'planets': results,
        'ascendant': get_sign_info(asc_deg),
        'midheaven': get_sign_info(mc_deg),
        'houses': houses,
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
