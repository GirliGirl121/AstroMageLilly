#!/usr/bin/env python3
# skyfield_core.py — High-Precision Modern Astronomy

import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from skyfield.api import Loader, wgs84
from skyfield import almanac
from skyfield.magnitudelib import planetary_magnitude

from config import EPHE_DIR, COLORS

console = Console()


class SkyfieldEngine:
    """High-precision astronomical calculations using Skyfield/JPL ephemerides."""

    def __init__(self):
        self.load = Loader(str(EPHE_DIR))
        try:
            self.planets = self.load('de440.bsp')
            self.ephe_name = 'DE440'
        except Exception:
            try:
                self.planets = self.load('de421.bsp')
                self.ephe_name = 'DE421'
            except Exception as e:
                console.print(f"[bold red]Could not load ephemeris: {e}[/bold red]")
                raise

        self.earth = self.planets['earth']
        self.ts = self.load.timescale()

        self._body_map = {
            'Sun': 10, 'Moon': 301, 'Mercury': 199, 'Venus': 299,
            'Mars': 4, 'Jupiter': 5, 'Saturn': 6,
            'Uranus': 7, 'Neptune': 8, 'Pluto': 9,
        }

    def _get_body(self, name: str):
        code = self._body_map.get(name, name)
        return self.planets[code]

    def _to_float(self, val):
        """Convert Skyfield numpy scalar/array to Python float."""
        if hasattr(val, 'item'):
            return float(val.item())
        return float(val)

    # ── Astrological position (ecliptic tropical) ──────────────────
    def get_planet_pos(self, planet_name: str, jd: float) -> Optional[Dict]:
        """Astrological ecliptic position (tropical) at given Julian Day (UT)."""
        if planet_name not in self._body_map:
            return None
        try:
            t = self.ts.ut1_jd(jd)
            t_later = self.ts.ut1_jd(jd + 1/24)
            body = self._get_body(planet_name)

            astrometric = self.earth.at(t).observe(body)
            apparent = astrometric.apparent()
            lat, lon, dist = apparent.ecliptic_latlon(epoch=None)

            astrometric2 = self.earth.at(t_later).observe(body)
            apparent2 = astrometric2.apparent()
            _, lon2, _ = apparent2.ecliptic_latlon(epoch=None)

            speed = lon2.degrees - lon.degrees
            if speed < -180:
                speed += 360
            elif speed > 180:
                speed -= 360

            tropical_deg = lon.degrees % 360
            sign_idx = int(tropical_deg / 30) % 12

            _SIGNS = [
                "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
            ]
            _ELEMENTS = {
                "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
                "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
                "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
                "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water",
            }
            _MODALITIES = {
                "Aries": "Cardinal", "Cancer": "Cardinal", "Libra": "Cardinal", "Capricorn": "Cardinal",
                "Taurus": "Fixed", "Leo": "Fixed", "Scorpio": "Fixed", "Aquarius": "Fixed",
                "Gemini": "Mutable", "Virgo": "Mutable", "Sagittarius": "Mutable", "Pisces": "Mutable",
            }
            _SYMBOLS = {
                "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀",
                "Mars": "♂", "Jupiter": "♃", "Saturn": "♄",
                "Uranus": "♅", "Neptune": "♆", "Pluto": "♇",
            }

            sign = _SIGNS[sign_idx]

            return {
                "name": planet_name,
                "symbol": _SYMBOLS.get(planet_name, ""),
                "longitude": round(tropical_deg, 4),
                "latitude": round(lat.degrees, 4),
                "distance": round(dist.au, 6),
                "sign": sign,
                "element": _ELEMENTS[sign],
                "modality": _MODALITIES[sign],
                "degree_in_sign": round(tropical_deg % 30, 2),
                "retrograde": speed < 0,
                "speed": round(speed, 6),
            }
        except Exception:
            return None

    # ── High-precision astronomical position ──────────────────────────
    def high_precision_pos(self, body_name: str, lat: float = -33.9249,
                           lon: float = 18.4241) -> Dict:
        """Get high-precision position for a body from a location."""
        t = self.ts.now()
        body = self._get_body(body_name)
        topos = wgs84.latlon(lat, lon)
        observer = self.earth + topos

        astrometric = observer.at(t).observe(body)
        apparent = astrometric.apparent()

        ra, dec, dist = apparent.radec(epoch=None)
        alt, az, _ = apparent.altaz()

        mag = None
        try:
            mag = planetary_magnitude(astrometric)
        except Exception:
            pass

        return {
            'name': body_name,
            'ra_hours': round(self._to_float(ra.hours), 5),
            'dec_degrees': round(self._to_float(dec.degrees), 5),
            'distance_au': round(self._to_float(dist.au), 6),
            'distance_km': round(self._to_float(dist.au) * 149597870.7, 1),
            'altitude': round(self._to_float(alt.degrees), 2),
            'azimuth': round(self._to_float(az.degrees), 2),
            'magnitude': round(self._to_float(mag), 2) if mag is not None else None,
            'ephemeris': self.ephe_name,
            'timestamp': t.utc_iso(),
        }

    def riset_transit(self, body_name: str, date: datetime,
                      lat: float, lon: float) -> List[Dict]:
        """Calculate precise rise, set, and transit times."""
        t0 = self.ts.utc(date.year, date.month, date.day)
        t1 = self.ts.utc(date.year, date.month, date.day + 1)
        topos = wgs84.latlon(lat, lon)
        body = self._get_body(body_name)

        f = almanac.risings_and_settings(self.planets, body, topos)
        times, events = almanac.find_discrete(t0, t1, f)

        results = []
        for t_i, is_rising in zip(times, events):
            event = "Rise" if is_rising else "Set"
            results.append({
                'time': t_i.utc_strftime('%H:%M:%S'),
                'event': event,
                'body': body_name,
            })

        f_transit = almanac.meridian_transits(self.planets, body, topos)
        times_t, events_t = almanac.find_discrete(t0, t1, f_transit)
        for t_i, ev in zip(times_t, events_t):
            if ev == 0:
                results.append({
                    'time': t_i.utc_strftime('%H:%M:%S'),
                    'event': 'Transit',
                    'body': body_name,
                })

        results.sort(key=lambda x: x['time'])
        return results

    def find_conjunction(self, body1: str, body2: str,
                         start: datetime, end: datetime,
                         max_deg: float = 10.0) -> Optional[Dict]:
        """Find the closest approach of two bodies within a date range."""
        t0 = self.ts.utc(start.year, start.month, start.day)
        t1 = self.ts.utc(end.year, end.month, end.day)

        hours = int((end - start).total_seconds() / 3600)
        if hours < 1:
            hours = 1
        times = self.ts.linspace(t0, t1, hours * 2 + 1)

        b1 = self._get_body(body1)
        b2 = self._get_body(body2)

        p1 = self.earth.at(times).observe(b1).apparent()
        p2 = self.earth.at(times).observe(b2).apparent()

        sep = p1.separation_from(p2)
        min_idx = sep.degrees.argmin()
        min_sep = sep.degrees[min_idx]

        if min_sep <= max_deg:
            return {
                'time': times[min_idx].utc_iso(),
                'separation_deg': round(self._to_float(min_sep), 4),
                'body1': body1,
                'body2': body2,
            }
        return None

    def angular_separation(self, body1: str, body2: str) -> Dict:
        """Current precise angular separation between two bodies."""
        t = self.ts.now()
        b1 = self._get_body(body1)
        b2 = self._get_body(body2)

        p1 = self.earth.at(t).observe(b1).apparent()
        p2 = self.earth.at(t).observe(b2).apparent()
        sep = p1.separation_from(p2)

        return {
            'body1': body1,
            'body2': body2,
            'separation_deg': round(self._to_float(sep.degrees), 4),
            'separation_arcmin': round(self._to_float(sep.degrees) * 60, 2),
            'timestamp': t.utc_iso(),
        }

    def precise_moon_phase(self) -> Dict:
        """High-precision moon phase and libration."""
        t = self.ts.now()
        sun = self._get_body('Sun')
        moon = self._get_body('Moon')

        e = self.earth.at(t)
        s = e.observe(sun).apparent()
        m = e.observe(moon).apparent()

        sep = s.separation_from(m)
        elongation = self._to_float(sep.degrees)
        illumination = (1 - math.cos(math.radians(elongation))) / 2
        _, _, dist = m.radec(epoch=None)

        return {
            'elongation_deg': round(elongation, 4),
            'illumination_percent': round(illumination * 100, 2),
            'phase_name': self._phase_name(elongation),
            'distance_km': round(self._to_float(dist.au) * 149597870.7, 1),
            'age_days': round(elongation / 360 * 29.53059, 2),
            'timestamp': t.utc_iso(),
        }

    def _phase_name(self, elongation: float) -> str:
        if elongation < 22.5:
            return "New Moon"
        elif elongation < 67.5:
            return "Waxing Crescent"
        elif elongation < 112.5:
            return "First Quarter"
        elif elongation < 157.5:
            return "Waxing Gibbous"
        elif elongation < 202.5:
            return "Full Moon"
        elif elongation < 247.5:
            return "Waning Gibbous"
        elif elongation < 292.5:
            return "Last Quarter"
        else:
            return "Waning Crescent"

    def print_positions_table(self, positions: List[Dict]):
        """Display high-precision positions."""
        table = Table(
            title="[bold " + COLORS['sky'] + "]🔭 Skyfield Positions (" + positions[0]['ephemeris'] + ")[/bold " + COLORS['sky'] + "]",
            border_style=COLORS["azure"],
        )
        table.add_column("Body", style=COLORS["gold"])
        table.add_column("RA", justify="right", style=COLORS["rose"])
        table.add_column("Dec", justify="right", style=COLORS["coral"])
        table.add_column("Alt°", justify="right", style=COLORS["azure"])
        table.add_column("Az°", justify="right", style=COLORS["sky"])
        table.add_column("Dist (AU)", justify="right", style="dim")

        for p in positions:
            table.add_row(
                p['name'],
                f"{p['ra_hours']:.3f}h",
                f"{p['dec_degrees']:.3f}°",
                f"{p['altitude']:.1f}°",
                f"{p['azimuth']:.1f}°",
                f"{p['distance_au']:.4f}",
            )
        console.print(table)


skyfield = SkyfieldEngine()

