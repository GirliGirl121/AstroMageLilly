"""
Lilly's Astronomical & Ephemeris Engine
"""
import math
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Tuple

try:
    from skyfield.api import Loader, Topos
    from skyfield import almanac
    SKYFIELD_AVAILABLE = True
except ImportError:
    SKYFIELD_AVAILABLE = False

from lilly_config import (
    EPHEM_DIR, CLASSICAL_PLANETS, ZODIAC_SIGNS,
    LUNAR_MANSIONS, PLANETARY_HOUR_RULERS
)


class CelestialEngine:
    def __init__(self):
        self.load = Loader(str(EPHEM_DIR))
        self.planets_data = None
        self.earth = None
        self.ts = None
        self._init_ephemeris()

    def _init_ephemeris(self):
        if not SKYFIELD_AVAILABLE:
            print("⚠️  Skyfield not installed. Run: pip install skyfield")
            return
        try:
            self.planets_data = self.load('de421.bsp')
            self.earth = self.planets_data['earth']
            self.ts = self.load.timescale()
            print("✨ Celestial engine initialized. The ephemeris is loaded.")
        except Exception as e:
            print(f"⚠️  Could not load ephemeris: {e}")

    def _get_planet(self, name: str):
        mapping = {
            "Sun": "sun", "Moon": "moon", "Mercury": "mercury",
            "Venus": "venus", "Mars": "mars", "Jupiter": "jupiter barycenter",
            "Saturn": "saturn barycenter", "Uranus": "uranus barycenter",
            "Neptune": "neptune barycenter", "Pluto": "pluto barycenter"
        }
        if name in mapping and self.planets_data:
            return self.planets_data[mapping[name]]
        return None

    def compute_planet_position(self, planet_name: str, dt: datetime,
                                 lat: float = 0.0, lon: float = 0.0) -> Dict:
        if not SKYFIELD_AVAILABLE or not self.planets_data:
            return {"error": "Skyfield ephemeris not available"}

        t = self.ts.from_datetime(dt.replace(tzinfo=timezone.utc))
        planet = self._get_planet(planet_name)
        if not planet:
            return {"error": f"Unknown planet: {planet_name}"}

        observer = self.earth + Topos(latitude_degrees=lat, longitude_degrees=lon)
        astrometric = observer.at(t).observe(planet)
        app = astrometric.apparent()

        lat_ecl, lon_ecl, distance = app.ecliptic_latlon(epoch=None)

        t_later = self.ts.from_datetime(
            dt.replace(tzinfo=timezone.utc) + timedelta(hours=1)
        )
        astrometric_later = observer.at(t_later).observe(planet)
        app_later = astrometric_later.apparent()
        _, lon_later, _ = app_later.ecliptic_latlon(epoch=None)

        speed = lon_later.degrees - lon_ecl.degrees
        if speed < -180:
            speed += 360
        elif speed > 180:
            speed -= 360

        tropical_deg = lon_ecl.degrees % 360
        sidereal_deg = (tropical_deg - 24.0) % 360

        sign_info = self._get_zodiac_sign(tropical_deg)
        nakshatra = self._get_lunar_mansion(sidereal_deg)

        return {
            "planet": planet_name,
            "datetime_utc": dt.isoformat(),
            "tropical_longitude": round(tropical_deg, 4),
            "sidereal_longitude": round(sidereal_deg, 4),
            "latitude": round(lat_ecl.degrees, 4),
            "distance_au": round(distance.au, 6),
            "speed_deg_per_hour": round(speed, 4),
            "retrograde": bool(speed < 0),
            "tropical_sign": sign_info[0],
            "tropical_sign_symbol": sign_info[1],
            "element": sign_info[2],
            "modality": sign_info[3],
            "ruler": sign_info[4],
            "degree_in_sign": round(tropical_deg % 30, 2),
            "sidereal_sign": self._get_zodiac_sign(sidereal_deg)[0],
            "lunar_mansion": nakshatra[0],
            "mansion_meaning": nakshatra[1],
        }

    def _get_zodiac_sign(self, longitude: float) -> Tuple[str, str, str, str, str]:
        sign_index = int(longitude / 30) % 12
        return ZODIAC_SIGNS[sign_index]

    def _get_lunar_mansion(self, sidereal_longitude: float) -> Tuple[str, str]:
        mansion_index = int(sidereal_longitude / (360 / 28)) % 28
        return LUNAR_MANSIONS[mansion_index][:2]

    def _days_since_j2000(self, dt: datetime) -> float:
        """Julian days since J2000.0 for approximate calculations."""
        t = self.ts.from_datetime(dt.replace(tzinfo=timezone.utc))
        return t.tt - 2451545.0

    def compute_ascendant(self, dt: datetime, lat: float, lon: float) -> Dict:
        """Calculate the Ascendant (Rising Sign)."""
        t = self.ts.from_datetime(dt.replace(tzinfo=timezone.utc))
        d = self._days_since_j2000(dt)

        gast = t.gast * 15.0
        lst = (gast + lon) % 360

        T = d / 36525.0
        eps = 23.439291 - 0.0130042 * T

        lst_rad = math.radians(lst)
        lat_rad = math.radians(lat)
        eps_rad = math.radians(eps)

        y = math.cos(lst_rad)
        x = -(math.sin(eps_rad) * math.tan(lat_rad) + math.cos(eps_rad) * math.sin(lst_rad))

        asc_deg = math.degrees(math.atan2(y, x)) % 360
        sign_info = self._get_zodiac_sign(asc_deg)

        return {
            "body": "Ascendant",
            "longitude": round(asc_deg, 4),
            "sign": sign_info[0],
            "symbol": sign_info[1],
            "element": sign_info[2],
            "modality": sign_info[3],
            "degree_in_sign": round(asc_deg % 30, 2)
        }

    def compute_extended_body(self, name: str, dt: datetime) -> Dict:
        """Calculate esoteric bodies: Lilith, Rahu, Ketu, Chiron."""
        d = self._days_since_j2000(dt)
        T = d / 36525.0

        if name == "Rahu":
            omega = 125.0445479 - 0.05295377 * d
            lon = omega % 360
            sign = self._get_zodiac_sign(lon)
            return {
                "body": "Rahu", "name": "North Node", "symbol": "☊",
                "longitude": round(lon, 4), "sign": sign[0],
                "element": sign[2], "degree_in_sign": round(lon % 30, 2),
                "meaning": "Karma, destiny, spiritual lessons, obsessions"
            }

        elif name == "Ketu":
            omega = 125.0445479 - 0.05295377 * d
            lon = (omega + 180.0) % 360
            sign = self._get_zodiac_sign(lon)
            return {
                "body": "Ketu", "name": "South Node", "symbol": "☋",
                "longitude": round(lon, 4), "sign": sign[0],
                "element": sign[2], "degree_in_sign": round(lon % 30, 2),
                "meaning": "Liberation, past lives, detachment, spiritual gifts"
            }

        elif name == "Lilith":
            L = 218.3164477 + 13.17639648 * d
            lon = (L + 318.15 + 0.164357 * T * 36525 + 180.0) % 360
            sign = self._get_zodiac_sign(lon)
            return {
                "body": "Lilith", "name": "Black Moon Lilith", "symbol": "⚸",
                "longitude": round(lon, 4), "sign": sign[0],
                "element": sign[2], "degree_in_sign": round(lon % 30, 2),
                "meaning": "Repressed desires, raw feminine power, shadow self, independence"
            }

        elif name == "Chiron":
            return {
                "body": "Chiron", "name": "Chiron", "symbol": "⚷",
                "error": "Chiron requires Swiss Ephemeris extended asteroid files (sepl_18.se1).",
                "meaning": "The wounded healer, deep soul wounds, teaching through pain"
            }

        return {"error": f"Unknown extended body: {name}"}

    def compute_parts(self, sun_lon: float, moon_lon: float, asc_lon: float, is_day: bool) -> Dict:
        """Calculate Part of Fortune and Part of Spirit."""
        def norm(x):
            return x % 360

        if is_day:
            pof = norm(asc_lon + moon_lon - sun_lon)
            pos = norm(asc_lon + sun_lon - moon_lon)
        else:
            pof = norm(asc_lon + sun_lon - moon_lon)
            pos = norm(asc_lon + moon_lon - sun_lon)

        pof_sign = self._get_zodiac_sign(pof)
        pos_sign = self._get_zodiac_sign(pos)

        return {
            "Part_of_Fortune": {
                "longitude": round(pof, 4), "sign": pof_sign[0],
                "degree_in_sign": round(pof % 30, 2),
                "meaning": "Material blessing, worldly success, bodily health"
            },
            "Part_of_Spirit": {
                "longitude": round(pos, 4), "sign": pos_sign[0],
                "degree_in_sign": round(pos % 30, 2),
                "meaning": "Spiritual purpose, soul's intention, divine will"
            }
        }

    def compute_natal_chart(self, birth_dt: datetime, lat: float, lon: float) -> Dict:
        """Compute a complete natal chart."""
        chart = {
            "birth_data": {
                "datetime": birth_dt.isoformat(),
                "latitude": lat,
                "longitude": lon
            },
            "planets": {},
            "extended": {},
            "points": {},
            "summary": {}
        }

        for planet in CLASSICAL_PLANETS + ["Uranus", "Neptune", "Pluto"]:
            chart["planets"][planet] = self.compute_planet_position(planet, birth_dt, lat, lon)

        # Extended bodies
        for body in ["Rahu", "Ketu", "Lilith", "Chiron"]:
            chart["extended"][body] = self.compute_extended_body(body, birth_dt)

        # Ascendant + Parts
        asc = self.compute_ascendant(birth_dt, lat, lon)
        chart["points"]["Ascendant"] = asc

        sun_lon = chart["planets"]["Sun"].get("tropical_longitude", 0)
        moon_lon = chart["planets"]["Moon"].get("tropical_longitude", 0)
        local_hour = birth_dt.hour + int(lon / 15)
        is_day = 6 <= local_hour % 24 <= 18
        parts = self.compute_parts(sun_lon, moon_lon, asc["longitude"], is_day)
        chart["points"].update(parts)

        chart["summary"]["dominant_element"] = self._dominant_element(chart["planets"])
        chart["summary"]["moon_mansion"] = chart["planets"]["Moon"]["lunar_mansion"]
        return chart

    def _dominant_element(self, planets: Dict) -> str:
        elements = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
        for p, data in planets.items():
            if "element" in data:
                elements[data["element"]] += 1
        return max(elements, key=elements.get)

    def compute_planetary_hours(self, dt: datetime, lat: float, lon: float) -> List[Dict]:
        """Calculate planetary hours for a given day."""
        if not SKYFIELD_AVAILABLE:
            return [{"error": "Skyfield not available"}]

        t0 = self.ts.from_datetime(dt.replace(hour=0, minute=0, tzinfo=timezone.utc))
        t1 = self.ts.from_datetime(dt.replace(hour=23, minute=59, tzinfo=timezone.utc))

        topos = Topos(latitude_degrees=lat, longitude_degrees=lon)

        # Fix: almanac needs the raw Topos, not earth + Topos
        f = almanac.dark_twilight_day(self.planets_data, topos)
        times, events = almanac.find_discrete(t0, t1, f)

        weekday = dt.strftime("%A")
        rulers = PLANETARY_HOUR_RULERS.get(weekday, PLANETARY_HOUR_RULERS["Sunday"])

        hours = []
        for i in range(24):
            ruler = rulers[i % 7]
            hours.append({
                "hour_number": i + 1,
                "planetary_ruler": ruler,
                "period": "day" if 6 <= i < 18 else "night",
                "significance": self._hour_significance(ruler)
            })
        return hours

    def _hour_significance(self, planet: str) -> str:
        meanings = {
            "Sun": "Success, vitality, authority, health",
            "Moon": "Emotions, journeys, dreams, fertility",
            "Mercury": "Communication, study, travel, commerce",
            "Venus": "Love, beauty, art, friendship, pleasure",
            "Mars": "Courage, conflict, surgery, physical strength",
            "Jupiter": "Wealth, expansion, wisdom, legal matters",
            "Saturn": "Discipline, endings, structure, meditation"
        }
        return meanings.get(planet, "Unknown")

    def current_sky_snapshot(self, lat: float = 0.0, lon: float = 0.0) -> Dict:
        """Get a real-time snapshot of the sky — classical, outer, and esoteric bodies."""
        now = datetime.now(timezone.utc)
        snapshot = {"timestamp": now.isoformat(), "planets": {}, "extended": {}, "points": {}}

        # Classical + Outer planets
        for planet in CLASSICAL_PLANETS + ["Uranus", "Neptune", "Pluto"]:
            snapshot["planets"][planet] = self.compute_planet_position(planet, now, lat, lon)

        # Extended esoteric bodies
        for body in ["Rahu", "Ketu", "Lilith", "Chiron"]:
            snapshot["extended"][body] = self.compute_extended_body(body, now)

        # Ascendant + Parts
        asc = self.compute_ascendant(now, lat, lon)
        snapshot["points"]["Ascendant"] = asc

        sun_lon = snapshot["planets"]["Sun"].get("tropical_longitude", 0)
        moon_lon = snapshot["planets"]["Moon"].get("tropical_longitude", 0)
        is_day = 6 <= (now.hour + int(lon/15)) % 24 <= 18
        parts = self.compute_parts(sun_lon, moon_lon, asc["longitude"], is_day)
        snapshot["points"].update(parts)

        return snapshot
