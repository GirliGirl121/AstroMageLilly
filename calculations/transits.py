"""AstroMage — Transit calendar engine.

Calculates upcoming transits between transit planets and natal chart
positions using Swiss Ephemeris.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from calculations.ephemeris import (
    get_jd_now, get_planet_positions, get_planet_position_by_name
)
from calculations.aspects import ASPECTS

SAST = timezone(timedelta(hours=2))

TRANSIT_ORB = {
    'conjunction': 6, 'opposition': 6, 'square': 6, 'trine': 6,
    'sextile': 4, 'quincunx': 2, 'semi-sextile': 1.5,
    'semi-square': 1.5, 'sesquiquadrate': 1.5,
}

TRANSIT_SIGNIFICANCE = {
    'conjunction': '🌊 Intensified focus — new cycle begins',
    'sextile':     '🌿 Gentle opportunity — cooperation',
    'square':      '⚡ Challenge — growth through tension',
    'trine':       '🌸 Harmony — effortless flow',
    'opposition':  '⚖️  Polarity — balance and awareness',
    'quincunx':    '🔄 Adjustment — healing and integration',
    'semi-sextile':'🌱 Subtle shift — latent potential',
}


def get_transit_calendar(
    natal_planets: dict[str, dict] | None = None,
    days: int = 30,
) -> list[dict]:
    """Calculate transit aspects for the next N days.

    Args:
        natal_planets: dict of natal positions {name: {longitude, ...}}
                       If None, uses current transit positions only
                       (transit-to-transit aspects).
        days: Number of days to look ahead (max 90).

    Returns:
        List of transit events sorted by date.
    """
    max_days = min(days, 90)
    transits = []
    start = datetime.now(SAST)

    for offset in range(max_days):
        check_date = start + timedelta(days=offset)
        utc_dt = check_date.astimezone(timezone.utc)

        import swisseph as swe
        jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day,
                        utc_dt.hour + utc_dt.minute / 60)

        transit_planets = {
            p['name']: p for p in get_planet_positions(jd)
        }

        if natal_planets:
            # Transit to natal aspects
            for t_name, t_pos in transit_planets.items():
                for n_name, n_pos in natal_planets.items():
                    if t_name == n_name:
                        continue
                    diff = abs(t_pos['longitude'] - n_pos['longitude']) % 360
                    if diff > 180:
                        diff = 360 - diff
                    for aspect_name, defn in ASPECTS.items():
                        if abs(diff - defn['angle']) <= TRANSIT_ORB.get(aspect_name, 6):
                            transits.append({
                                'date': check_date.strftime('%Y-%m-%d'),
                                'day': check_date.strftime('%a'),
                                'transit_planet': t_name,
                                'natal_planet': n_name,
                                'aspect': aspect_name,
                                'symbol': defn['symbol'],
                                'separation': round(diff, 2),
                                'orb': round(abs(diff - defn['angle']), 2),
                                'significance': TRANSIT_SIGNIFICANCE.get(
                                    aspect_name, ''),
                                'transit_sign': t_pos.get('sign', ''),
                                'natal_sign': n_pos.get('sign', ''),
                            })
                            break
        else:
            # Transit-to-transit aspects for current day
            names = list(transit_planets.keys())
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    n1, n2 = names[i], names[j]
                    p1, p2 = transit_planets[n1], transit_planets[n2]
                    diff = abs(p1['longitude'] - p2['longitude']) % 360
                    if diff > 180:
                        diff = 360 - diff
                    for aspect_name, defn in ASPECTS.items():
                        if abs(diff - defn['angle']) <= TRANSIT_ORB.get(aspect_name, 6):
                            transits.append({
                                'date': check_date.strftime('%Y-%m-%d'),
                                'day': check_date.strftime('%a'),
                                'transit_planet': n1,
                                'natal_planet': n2,
                                'aspect': aspect_name,
                                'symbol': defn['symbol'],
                                'separation': round(diff, 2),
                                'orb': round(abs(diff - defn['angle']), 2),
                                'significance': TRANSIT_SIGNIFICANCE.get(
                                    aspect_name, ''),
                            })
                            break

    transits.sort(key=lambda x: (x['date'], x['transit_planet']))
    return transits
