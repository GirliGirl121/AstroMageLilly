from datetime import datetime
from typing import Dict, Any
import swisseph as swe

from calculations.ephemeris import get_planet_positions, get_sign_info, get_moon_phase, get_current_nakshatra
from calculations.houses import get_house_cusps, get_whole_sign_houses

class Engine:
    def __init__(self):
        self.location = "Kariega, South Africa"
        self.lat = -33.72
        self.lon = 25.97
        self.timezone = 2.0
        self.house_system = "W"  # "W" = Whole Sign, "E" = Equal, "P" = Placidus

    def set_house_system(self, system: str):
        """Set house system: 'W' Whole Sign, 'E' Equal, 'P' Placidus."""
        self.house_system = system

    def live(self) -> Dict[str, Any]:
        now = datetime.now()
        jd = swe.julday(now.year, now.month, now.day, now.hour + now.minute/60.0)

        # 1. Fetch planetary positions (already has sign, degree, symbol, retrograde)
        planets_list = get_planet_positions(jd)

        if not planets_list:
            print("CRITICAL: get_planet_positions returned an empty list!")
            planets = {}
        else:
            planets = {planet["name"]: planet for planet in planets_list}

        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M")

        # 2. Calculate houses based on selected system
        if self.house_system == "W":
            house_data = get_whole_sign_houses(date_str, time_str, self.lat, self.lon)
        else:
            house_data = get_house_cusps(date_str, time_str, self.lat, self.lon, self.house_system)

        house_cusps = [h["longitude"] for h in house_data["houses"]]

        asc_data = house_data["ascendant"]
        mc_data = house_data["midheaven"]

        # 3. Assign houses to each planet
        asc_sign_idx = int(asc_data["longitude"] / 30) % 12

        for planet in planets.values():
            lon = planet.get("longitude", 0)
            planet_sign_idx = int(lon / 30) % 12

            if self.house_system == "W":
                # Whole Sign: house = which sign relative to Ascendant
                house = ((planet_sign_idx - asc_sign_idx) % 12) + 1
            else:
                # Quadrant systems (Placidus, Equal, Koch, etc.)
                house = 12
                for i in range(11):
                    if house_cusps[i] <= lon < house_cusps[i + 1]:
                        house = i + 1
                        break
            planet["house"] = house

        # 4. Add Moon phase and Nakshatra
        moon_phase = get_moon_phase()
        nakshatra = get_current_nakshatra(jd)

        # 5. Calculate planetary hour (simplified)
        planetary_hour = self._get_planetary_hour(now)

        return {
            "location": self.location,
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S SAST"),
            "planets": planets,
            "houses": house_data["houses"],
            "ascendant": asc_data,
            "midheaven": mc_data,
            "moon_phase": moon_phase,
            "lunar_mansion": {
                "name": nakshatra["nakshatra"],
                "index": nakshatra["index"],
                "pada": nakshatra["pada"],
                "lord": nakshatra["lord"],
            },
            "planetary_hour": planetary_hour,
            "house_system": self.house_system,
        }

    def _get_planetary_hour(self, dt: datetime) -> Dict[str, Any]:
        """Calculate current planetary hour (Chaldean order)."""
        chaldean = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
        day_of_week = dt.weekday()
        first_hour_planet = chaldean[(day_of_week * 3) % 7]
        hour = dt.hour
        current_planet = chaldean[(chaldean.index(first_hour_planet) + hour) % 7]

        return {
            "planet": current_planet,
            "planet_ar": self._planet_arabic(current_planet),
            "time": dt.strftime("%H:%M"),
            "system": "Chaldean Planetary Hours",
        }

    def _planet_arabic(self, planet: str) -> str:
        arabic_names = {
            "Sun": "Shams (☉)",
            "Moon": "Qamar (☽)",
            "Mercury": "Utarid (☿)",
            "Venus": "Zuhra (♀)",
            "Mars": "Mirrikh (♂)",
            "Jupiter": "Mushtari (♃)",
            "Saturn": "Zuhal (♄)",
        }
        return arabic_names.get(planet, planet)

    def planet(self, name: str) -> Dict[str, Any]:
        """Get a single planet's current position."""
        from calculations.ephemeris import get_planet_position_by_name
        return get_planet_position_by_name(name) or {}

    def transit_calendar(self, days: int = 7, natal_planets: Dict = None) -> list:
        """Generate transit calendar for next N days."""
        from calculations.transits import get_major_transits
        return get_major_transits(days=days, natal_planets=natal_planets)

