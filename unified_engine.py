#!/usr/bin/env python3
# unified_engine.py — The Convergence of Two Skies
# Primary: Swiss Ephemeris (astrology) | Secondary: Skyfield (astronomy + validation)

import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from rich.console import Console

console = Console()

# ── Graceful engine imports ───────────────────────────────────────
try:
    from astro_core import CelestialEngine as SwissEngine
    _swiss_ok = True
except Exception as e:
    console.print(f"[yellow]⚠️  Swiss Ephemeris unavailable: {e}[/yellow]")
    _swiss_ok = False

try:
    from skyfield_core import SkyfieldEngine
    _sky_ok = True
except Exception as e:
    console.print(f"[yellow]⚠️  Skyfield unavailable: {e}[/yellow]")
    _sky_ok = False

if not _swiss_ok and not _sky_ok:
    raise ImportError("No astronomical engine available.")


class UnifiedEngine:
    """
    One engine to rule them all.
    • Astrology (houses, aspects, arabic parts) → Swiss Ephemeris
    • Astronomy (RA/Dec, rise/set, conjunctions) → Skyfield
    • Planet positions → Swiss primary, Skyfield validation when both present
    """

    def __init__(self, primary: str = "swisseph"):
        self.swiss = SwissEngine() if _swiss_ok else None
        self.sky = SkyfieldEngine() if _sky_ok else None

        self.astrology = self.swiss
        self.astronomy = self.sky

        self.primary_name = "swisseph" if _swiss_ok else "skyfield"
        self.secondary_name = "skyfield" if _sky_ok and _swiss_ok else None

    @property
    def ephe_name(self) -> str:
        return self.sky.ephe_name if self.sky else "N/A"

    # ── Julian Day ───────────────────────────────────────────────────
    def jd_from_datetime(self, dt: datetime, tz_offset: float = 0.0) -> float:
        """Convert datetime to Julian Day."""
        if self.swiss:
            return self.swiss.jd_from_datetime(dt, tz_offset)
        utc_dt = dt - timedelta(hours=tz_offset)
        a = (14 - utc_dt.month) // 12
        y = utc_dt.year + 4800 - a
        m = utc_dt.month + 12 * a - 3
        jdn = (utc_dt.day + ((153 * m + 2) // 5) + 365 * y
               + y // 4 - y // 100 + y // 400 - 32045)
        return float(jdn - 0.5 + (utc_dt.hour + utc_dt.minute/60 + utc_dt.second/3600) / 24)

    # ── Planet positions (Swiss primary, Skyfield validates) ────────
    def get_planet_pos(self, planet_name: str, jd: float) -> Optional[Dict]:
        """Get planet position. Swiss primary, Skyfield validation."""
        result = None
        sky_result = None

        if self.swiss:
            try:
                result = self.swiss.get_planet_pos(planet_name, jd)
            except Exception:
                pass

        if self.sky:
            try:
                sky_result = self.sky.get_planet_pos(planet_name, jd)
            except Exception:
                pass

        if not result and sky_result:
            result = sky_result

        if result and sky_result and self.swiss:
            lon_diff = abs(result["longitude"] - sky_result["longitude"])
            if lon_diff > 180:
                lon_diff = 360 - lon_diff
            result["_validation"] = {
                "skyfield_longitude": sky_result["longitude"],
                "diff_arcmin": round(lon_diff * 60, 2),
                "agreement": lon_diff < 0.0083,
            }
        return result

    def get_all_planets(self, jd: float) -> Dict[str, Dict]:
        """Get all planets with optional validation."""
        planets = ["Sun", "Moon", "Mercury", "Venus", "Mars",
                   "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto",
                   "North Node"]
        result = {}
        for p in planets:
            pos = self.get_planet_pos(p, jd)
            if pos:
                result[p] = pos

        if "North Node" in result:
            node = result["North Node"]
            lon = (node["longitude"] + 180) % 360
            from astro_core import SIGNS, SIGN_ELEMENTS, SIGN_MODALITIES
            sign_idx = int(lon / 30) % 12
            sign = SIGNS[sign_idx]
            result["South Node"] = {
                "name": "South Node",
                "symbol": "☋",
                "longitude": round(lon, 4),
                "latitude": round(-node["latitude"], 4),
                "distance": node["distance"],
                "sign": sign,
                "element": SIGN_ELEMENTS[sign],
                "modality": SIGN_MODALITIES[sign],
                "degree_in_sign": round(lon % 30, 2),
                "retrograde": True,
                "speed": 0,
            }

        chiron = self.get_planet_pos("Chiron", jd)
        if chiron:
            result["Chiron"] = chiron

        return result

    # ── Houses ─────────────────────────────────────────────────────
    def calculate_houses(self, jd: float, lat: float, lon: float,
                         hsys: bytes = b'P') -> List[Dict]:
        """Calculate houses. Only Swiss supports this."""
        if self.swiss:
            return self.swiss.calculate_houses(jd, lat, lon, hsys)
        return []

    def get_house_for_longitude(self, longitude: float, houses: List[Dict]) -> int:
        """Determine house for a longitude."""
        if self.swiss:
            return self.swiss.get_house_for_longitude(longitude, houses)
        cusps = [(h['house'], float(h['cusp'])) for h in houses]
        n = len(cusps)
        for i in range(n):
            cusp_i = cusps[i][1]
            cusp_next = cusps[(i + 1) % n][1]
            house_num = cusps[i][0]
            if cusp_next > cusp_i:
                if cusp_i <= longitude < cusp_next:
                    return house_num
            else:
                if longitude >= cusp_i or longitude < cusp_next:
                    return house_num
        return 1

    # ── Arabic Parts ───────────────────────────────────────────────
    def calculate_arabic_parts(self, jd: float, lat: float, lon: float) -> Dict[str, Dict]:
        """Calculate Arabic Parts. Delegates to Swiss."""
        if self.swiss:
            return self.swiss.calculate_arabic_parts(jd, lat, lon)
        return {}

    # ── Aspects ─────────────────────────────────────────────────────
    def calculate_aspects(self, positions: Dict[str, Dict], orb: float = 8.0) -> List[Dict]:
        """Calculate aspects. Delegates to Swiss."""
        if self.swiss:
            return self.swiss.calculate_aspects(positions, orb)
        ASPECTS = {
            "Conjunction": 0, "Sextile": 60, "Square": 90,
            "Trine": 120, "Opposition": 180,
        }
        planets = list(positions.keys())
        aspects = []
        for i, p1 in enumerate(planets):
            for p2 in planets[i+1:]:
                lon1 = positions[p1]["longitude"]
                lon2 = positions[p2]["longitude"]
                diff = abs(((lon1 - lon2 + 180) % 360) - 180)
                for name, angle in ASPECTS.items():
                    orb_val = abs(diff - angle)
                    if orb_val <= orb:
                        aspects.append({
                            "planet1": p1, "planet2": p2,
                            "aspect": name, "angle": round(diff, 2),
                            "orb": round(orb_val, 2),
                            "applying": False,
                        })
        return aspects

    # ── Moon Phase ───────────────────────────────────────────────────
    def get_moon_phase(self, jd: float) -> Dict:
        """Calculate moon phase. Delegates to Swiss."""
        if self.swiss:
            return self.swiss.get_moon_phase(jd)
        sun = self.get_planet_pos("Sun", jd)
        moon = self.get_planet_pos("Moon", jd)
        if not sun or not moon:
            return {"phase": "Unknown", "illumination": 0, "age": 0, "elongation": 0}
        elongation = (moon["longitude"] - sun["longitude"] + 360) % 360
        illumination = (1 - math.cos(math.radians(elongation))) / 2
        if elongation < 45: phase = "New Moon"
        elif elongation < 90: phase = "Waxing Crescent"
        elif elongation < 135: phase = "First Quarter"
        elif elongation < 180: phase = "Waxing Gibbous"
        elif elongation < 225: phase = "Full Moon"
        elif elongation < 270: phase = "Waning Gibbous"
        elif elongation < 315: phase = "Last Quarter"
        else: phase = "Waning Crescent"
        return {
            "elongation": round(elongation, 2),
            "illumination": round(illumination * 100, 2),
            "phase": phase,
            "age": round(elongation / 360 * 29.53, 2),
        }

    # ── Full Chart Builder ───────────────────────────────────────────
    def get_full_chart(self, dt: datetime, lat: float, lon: float,
                       tz_offset: float = 0.0, name: str = "Unknown") -> Dict:
        """Calculate a complete natal / event chart."""
        jd = self.jd_from_datetime(dt, tz_offset)
        planets = self.get_all_planets(jd)
        houses = self.calculate_houses(jd, lat, lon)
        arabic = self.calculate_arabic_parts(jd, lat, lon)
        aspects = self.calculate_aspects(planets)
        moon_phase = self.get_moon_phase(jd)

        for p_name, p_data in planets.items():
            p_data["house"] = self.get_house_for_longitude(p_data["longitude"], houses)

        return {
            "name": name,
            "datetime": dt.isoformat(),
            "tz_offset": tz_offset,
            "latitude": lat,
            "longitude": lon,
            "julian_day": jd,
            "planets": planets,
            "houses": houses,
            "arabic_parts": arabic,
            "aspects": aspects,
            "moon_phase": moon_phase,
            "calculation_engine": self.primary_name,
            "validation_available": self.secondary_name is not None,
        }

    # ── Synastry ─────────────────────────────────────────────────────
    def synastry(self, chart1: Dict, chart2: Dict, orb: float = 8.0) -> Dict:
        """Inter-aspects and house overlays between two charts."""
        p1 = chart1.get("planets", {})
        p2 = chart2.get("planets", {})
        ASPECTS = {
            "Conjunction": 0, "Sextile": 60, "Square": 90,
            "Trine": 120, "Opposition": 180,
        }

        inter_aspects = []
        for n1, pos1 in p1.items():
            for n2, pos2 in p2.items():
                if n1 == n2:
                    continue
                diff = abs(((pos1["longitude"] - pos2["longitude"] + 180) % 360) - 180)
                for asp_name, angle in ASPECTS.items():
                    orb_val = abs(diff - angle)
                    if orb_val <= orb:
                        inter_aspects.append({
                            "planet1": n1,
                            "chart1": chart1.get("name", "Chart 1"),
                            "planet2": n2,
                            "chart2": chart2.get("name", "Chart 2"),
                            "aspect": asp_name,
                            "angle": round(diff, 2),
                            "orb": round(orb_val, 2),
                        })

        inter_aspects.sort(key=lambda x: x["orb"])

        house_overlays = []
        houses1 = chart1.get("houses", [])
        for n2, pos2 in p2.items():
            h = self.get_house_for_longitude(pos2["longitude"], houses1)
            house_overlays.append({
                "planet": n2,
                "planet_owner": chart2.get("name", "Chart 2"),
                "house": h,
                "house_owner": chart1.get("name", "Chart 1"),
                "house_sign": houses1[h-1]["sign"] if houses1 and 1 <= h <= 12 else "Unknown",
            })

        return {
            "chart1": chart1.get("name", "Chart 1"),
            "chart2": chart2.get("name", "Chart 2"),
            "inter_aspects": inter_aspects,
            "house_overlays": house_overlays,
        }

    # ── Transits ─────────────────────────────────────────────────────
    def transits(self, natal_chart: Dict, current_jd: float, orb: float = 5.0) -> Dict:
        """Current planets transiting natal chart."""
        current_positions = self.get_all_planets(current_jd)
        current_chart = {
            "name": "Transits",
            "planets": current_positions,
        }
        result = self.synastry(natal_chart, current_chart, orb=orb)
        result["type"] = "transits"
        result["jd"] = current_jd
        return result

    # ── Engine Comparison ───────────────────────────────────────────
    def compare_engines(self, dt: datetime, lat: float, lon: float,
                        tz_offset: float = 0.0) -> Dict:
        """Validate Swiss vs Skyfield planet positions."""
        if not (self.sky and self.swiss):
            return {"error": "Both engines not available"}

        jd = self.jd_from_datetime(dt, tz_offset)
        diffs = {}
        for p in ["Sun", "Moon", "Mercury", "Venus", "Mars",
                  "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]:
            pos_s = self.swiss.get_planet_pos(p, jd)
            pos_w = self.sky.get_planet_pos(p, jd)
            if pos_s and pos_w:
                d = abs(((pos_s["longitude"] - pos_w["longitude"] + 180) % 360) - 180)
                diffs[p] = round(d * 60, 2)

        max_diff = max(diffs.values()) if diffs else 0
        return {
            "jd": jd,
            "datetime": dt.isoformat(),
            "longitude_diffs_arcmin": diffs,
            "max_diff_arcmin": max_diff,
            "agreement": "PASS" if max_diff < 0.5 else "CHECK",
            "message": "Engines agree within 0.5 arcmin" if max_diff < 0.5 else f"Max diff: {max_diff} arcmin — investigate",
        }

    # ── Astronomical API (pass-through to Skyfield) ────────────────
    def high_precision_pos(self, body_name: str, lat: float, lon: float) -> Optional[Dict]:
        """RA/Dec/Alt/Az from Skyfield."""
        return self.sky.high_precision_pos(body_name, lat, lon) if self.sky else None

    def riset_transit(self, body_name: str, date: datetime, lat: float, lon: float) -> List[Dict]:
        """Rise/set/transit times from Skyfield."""
        return self.sky.riset_transit(body_name, date, lat, lon) if self.sky else []

    def find_conjunction(self, body1: str, body2: str, start: datetime, end: datetime,
                         max_deg: float = 10.0) -> Optional[Dict]:
        """Find conjunctions via Skyfield."""
        return self.sky.find_conjunction(body1, body2, start, end, max_deg) if self.sky else None

    def angular_separation(self, body1: str, body2: str) -> Optional[Dict]:
        """Angular separation via Skyfield."""
        return self.sky.angular_separation(body1, body2) if self.sky else None

    def precise_moon_phase(self) -> Optional[Dict]:
        """High-precision moon phase via Skyfield."""
        return self.sky.precise_moon_phase() if self.sky else None

    def print_positions_table(self, positions: List[Dict]):
        """Display high-precision positions via Skyfield."""
        if self.sky and hasattr(self.sky, 'print_positions_table'):
            self.sky.print_positions_table(positions)


engine = UnifiedEngine()

