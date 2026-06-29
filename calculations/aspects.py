"""AstroMage — Aspect calculation engine.

Single source of truth for astrological aspect calculations.
All aspect logic uses Swiss Ephemeris positions.
"""
from __future__ import annotations

import math

# ─── Aspect Definitions ──────────────────────────────────────────────────

ASPECTS = {
    'conjunction':   {'angle': 0,   'orb': 8.0,  'symbol': '☌', 'type': 'major'},
    'semi-sextile':  {'angle': 30,  'orb': 2.0,  'symbol': '╱', 'type': 'minor'},
    'semi-square':   {'angle': 45,  'orb': 2.0,  'symbol': '∠', 'type': 'minor'},
    'sextile':       {'angle': 60,  'orb': 6.0,  'symbol': '⚹', 'type': 'major'},
    'quintile':      {'angle': 72,  'orb': 1.5,  'symbol': 'Q',  'type': 'minor'},
    'square':        {'angle': 90,  'orb': 8.0,  'symbol': '□', 'type': 'major'},
    'trine':         {'angle': 120, 'orb': 8.0,  'symbol': '△', 'type': 'major'},
    'sesquiquadrate':{'angle': 135, 'orb': 2.0,  'symbol': '⚼', 'type': 'minor'},
    'biquintile':    {'angle': 144, 'orb': 1.5,  'symbol': 'BQ', 'type': 'minor'},
    'quincunx':      {'angle': 150, 'orb': 3.0,  'symbol': '⚻', 'type': 'minor'},
    'opposition':    {'angle': 180, 'orb': 8.0,  'symbol': '☍', 'type': 'major'},
}

ASPECT_MEANINGS = {
    'conjunction':   'Powerful focus — energies merge and amplify',
    'sextile':       'Opportunity — cooperation and gentle flow',
    'square':        'Tension — challenge that drives growth',
    'trine':         'Harmony — natural ease and effortless flow',
    'opposition':    'Polarity — balance needed between two forces',
    'quincunx':      'Adjustment — requires fine-tuning and healing',
    'semi-sextile':  'Subtle connection — latent potential',
    'semi-square':   'Friction — minor irritation, motivation to act',
    'sesquiquadrate':'Aggravation — ongoing adjustment required',
    'quintile':      'Talent — creative flair and inspired expression',
    'biquintile':    'Genius — deep creative and spiritual insight',
}


def calculate_aspects(
    planet_positions: dict[str, dict],
) -> list[dict]:
    """Calculate aspects between a dict of planet positions.

    Args:
        planet_positions: dict like {'Sun': {'longitude': 123.4}, ...}

    Returns:
        List of aspect dicts sorted by orb (tightest first).
    """
    aspects = []
    names = list(planet_positions.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            n1, n2 = names[i], names[j]
            p1 = planet_positions[n1]
            p2 = planet_positions[n2]

            lon1 = p1.get('longitude', 0)
            lon2 = p2.get('longitude', 0)
            diff = abs(lon1 - lon2) % 360
            if diff > 180:
                diff = 360 - diff

            for name, defn in ASPECTS.items():
                angle = defn['angle']
                orb = defn['orb']
                separation = abs(diff - angle)
                if separation <= orb:
                    aspects.append({
                        'planet1': n1,
                        'planet2': n2,
                        'aspect': name,
                        'symbol': defn['symbol'],
                        'angle': angle,
                        'separation': round(diff, 2),
                        'orb': round(separation, 2),
                        'type': defn['type'],
                        'meaning': ASPECT_MEANINGS.get(name, ''),
                    })
                    break

    aspects.sort(key=lambda a: a['orb'])
    return aspects


def get_aspect_symbol(aspect_name: str) -> str:
    return ASPECTS.get(aspect_name.lower(), {}).get('symbol', '')


def get_aspect_meaning(aspect_name: str) -> str:
    return ASPECT_MEANINGS.get(aspect_name.lower(), '')
