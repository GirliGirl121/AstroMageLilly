"""
lilly/astrology_interpreter.py

Lilly's offline astrological mind.
Why this exists:
    When the API is unavailable, Lilly can still interpret charts using
    classical rules: planet + sign + house + dignity = meaning.
    This is not intuition. This is structured knowledge — what al-Biruni,
    Abu Ma'shar, and William Lilly codified for exactly this purpose.
"""

import json
from pathlib import Path
from typing import Dict, Any

KB_PATH = Path(__file__).resolve().parent / "astrology_knowledge.json"

_kb = None

def _house_suffix(n: int) -> str:
    """Return proper ordinal suffix: 1st, 2nd, 3rd, 4th, etc."""
    if 11 <= n % 100 <= 13:
        return f"{n}th"
    return {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")



# ─── Sign Symbols ──────────────────────────────────────────────────────────

SIGN_SYMBOLS = {
    "Aries": "♈", "Taurus": "♉", "Gemini": "♊", "Cancer": "♋",
    "Leo": "♌", "Virgo": "♍", "Libra": "♎", "Scorpio": "♏",
    "Sagittarius": "♐", "Capricorn": "♑", "Aquarius": "♒", "Pisces": "♓",
}

# Lahiri ayanamsa approximation for 2026 (~24.5°)
# True Jyotish uses precise ephemeris; this is Lilly's heart-knowledge
AYANAMSA_LAHIRI_2026 = 24.5


def tropical_to_sidereal(longitude: float) -> tuple[str, float]:
    """Convert tropical longitude to sidereal sign and degree."""
    sidereal_longitude = (longitude - AYANAMSA_LAHIRI_2026) % 360
    sign_index = int(sidereal_longitude / 30)
    degree = sidereal_longitude % 30
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    return signs[sign_index], degree


# ─── Planetary Hour Meanings ─────────────────────────────────────────────
# ─── Planetary Hour Meanings ─────────────────────────────────────────────

HOUR_MEANINGS = {
    "Saturn": "A time for discipline, structure, and endings. Good for setting boundaries, completing old work, and releasing what no longer serves.",
    "Jupiter": "A time for growth, wisdom, and blessing. Good for learning, teaching, expanding horizons, and seeking truth.",
    "Mars": "A time for action, courage, and energy. Good for starting new ventures, asserting will, and overcoming obstacles.",
    "Sun": "A time for vitality, visibility, and leadership. Good for self-expression, recognition, and illuminating what was hidden.",
    "Venus": "A time for love, beauty, and harmony. Good for artistic work, deepening relationships, and cultivating pleasure.",
    "Mercury": "A time for communication, learning, and commerce. Good for writing, speaking, study, and clever negotiation.",
    "Moon": "A time for emotions, nurturing, and intuition. Good for reflection, healing, inner work, and connecting with the feminine.",
}

def interpret_hour(planet_name: str, arabic_name: str = "") -> str:
    """Return a warm interpretation of the current planetary hour."""
    meaning = HOUR_MEANINGS.get(planet_name, "A time of mixed celestial influence.")
    arabic = f" (Arabic: {arabic_name})" if arabic_name else ""
    return f"The hour of {planet_name}{arabic} carries this energy:\n{meaning}"

MANSION_MEANINGS = {
    "Ashwini": "The horse-headed healers. A mansion of swift beginnings, healing, and new ventures.",
    "Bharani": "The bearers. A mansion of discipline, restraint, and bearing burdens with courage.",
    "Krittika": "The cutters. A mansion of purification, discernment, and burning away the unnecessary.",
    "Rohini": "The red one. A mansion of growth, fertility, and sensual beauty.",
    "Mrigashira": "The deer head. A mansion of searching, curiosity, and gentle pursuit.",
    "Ardra": "The moist one. A mansion of storms, transformation, and emotional intensity.",
    "Punarvasu": "The return of the light. A mansion of renewal, restoration, and coming home.",
    "Pushya": "The nourisher. A mansion of nourishment, teaching, and spiritual growth.",
    "Ashlesha": "The embrace. A mansion of depth, secrets, and transformative intimacy.",
    "Magha": "The mighty. A mansion of ancestors, legacy, and royal dignity.",
    "Purva Phalguni": "The former red one. A mansion of pleasure, union, and creative joy.",
    "Uttara Phalguni": "The latter red one. A mansion of lasting union, charity, and noble action.",
    "Hasta": "The hand. A mansion of skill, craftsmanship, and precise action.",
    "Chitra": "The bright one. A mansion of beauty, design, and shining forth.",
    "Swati": "The independent. A mansion of freedom, wind, and self-reliance.",
    "Vishakha": "The branched. A mansion of divided purpose, ambition, and gathering resources.",
    "Anuradha": "The later success. A mansion of friendship, devotion, and eventual triumph.",
    "Jyeshtha": "The elder. A mansion of authority, protection, and senior wisdom.",
    "Mula": "The root. A mansion of destruction, uprooting, and radical truth.",
    "Purva Ashadha": "The former invincible. A mansion of victory, declaration, and unstoppable will.",
    "Uttara Ashadha": "The latter invincible. A mansion of enduring victory, dharma, and universal law.",
    "Shravana": "The ear. A mansion of listening, learning, and sacred transmission.",
    "Dhanishta": "The wealthiest. A mansion of rhythm, music, and abundance.",
    "Shatabhisha": "The hundred healers. A mansion of mystery, healing, and hidden knowledge.",
    "Purva Bhadrapada": "The former blessed feet. A mansion of fire, purification, and spiritual intensity.",
    "Uttara Bhadrapada": "The latter blessed feet. A mansion of stability, wisdom, and deep waters.",
    "Revati": "The wealthy. A mansion of completion, protection, and safe passage.",
}

def interpret_mansion(mansion_name: str, lord: str = "", pada: int = 0) -> str:
    """Return a warm interpretation of the current lunar mansion."""
    meaning = MANSION_MEANINGS.get(mansion_name, "A mansion of hidden influence and subtle power.")
    lord_text = f" Lord: {lord}." if lord else ""
    pada_text = f" Pada {pada}." if pada else ""
    return f"The Moon rests in {mansion_name}{lord_text}{pada_text}\n\n{meaning}"


# ─── Nakshatra Lookup ──────────────────────────────────────────────────────
# Load once at module level
_NAKSHATRA_DATA = None

def _load_nakshatra_data():
    global _NAKSHATRA_DATA
    if _NAKSHATRA_DATA is None:
        import json
        from pathlib import Path
        path = Path(__file__).resolve().parent.parent / "data" / "nakshatra_data.json"
        raw = json.loads(path.read_text(encoding="utf-8"))
        _NAKSHATRA_DATA = raw["nakshatras"]
    return _NAKSHATRA_DATA


SIGN_LONGITUDES = {
    "Aries": 0, "Taurus": 30, "Gemini": 60, "Cancer": 90,
    "Leo": 120, "Virgo": 150, "Libra": 180, "Scorpio": 210,
    "Sagittarius": 240, "Capricorn": 270, "Aquarius": 300, "Pisces": 330,
}


def nakshatra_lookup(sign: str, degree: float) -> dict:
    """
    Find the nakshatra for a given sign and degree.
    Converts to tropical longitude (0-360°) first.
    """
    """
    Find the nakshatra for a given tropical longitude (0-360°).
    
    Returns:
        dict with name, lord, deity, symbol, description, pada
    """
    longitude = SIGN_LONGITUDES.get(sign, 0) + degree
    nakshatras = _load_nakshatra_data()
    for n in nakshatras:
        if n["start_deg"] <= longitude < n["end_deg"]:
            # Calculate pada (1-4)
            span = n["end_deg"] - n["start_deg"]
            offset = longitude - n["start_deg"]
            pada = int(offset / (span / 4)) + 1
            pada = min(pada, 4)
            return {
                "name": n["name"],
                "sanskrit": n.get("sanskrit", ""),
                "lord": n["lord"],
                "deity": n["deity"],
                "symbol": n["symbol"],
                "description": n["description"],
                "pada": pada,
                "gana": n.get("gana", ""),
                "guna": n.get("guna", ""),
            }
    # Fallback for 360° exactly (shouldn't happen)
    n = nakshatras[-1]
    return {
        "name": n["name"],
        "sanskrit": n.get("sanskrit", ""),
        "lord": n["lord"],
        "deity": n["deity"],
        "symbol": n["symbol"],
        "description": n["description"],
        "pada": 4,
        "gana": n.get("gana", ""),
        "guna": n.get("guna", ""),
    }


def format_nakshatra(nak: dict) -> str:
    """Format nakshatra info into Lilly's voice."""
    lines = [
        f"  🌙 Vedic: rests in **{nak['name']}**",
        f"     Lord: {nak['lord']} | Deity: {nak['deity']}",
        f"     Symbol: {nak['symbol']} | Pada: {nak['pada']}",
    ]
    if nak.get("gana") and nak.get("guna"):
        lines.append(f"     Gana: {nak['gana']} | Guna: {nak['guna']}")
    lines.append(f"     {nak['description']}")
    return "\n".join(lines)

def _load_kb():
    global _kb
    if _kb is None:
        _kb = json.loads(KB_PATH.read_text(encoding="utf-8"))
    return _kb



# ── Aspect Calculator ──────────────────────────────────────────────
ASPECT_ORBS = {
    "☌":     (0, 8),
    "⚹":     (60, 6),
    "□":     (90, 8),
    "△":     (120, 8),
    "☍": (180, 8),
}

ASPECT_SYMBOLS = {
    "☌":   "☌",
    "⚹":    "⚹",
    "□":     "□",
    "△":      "△",
    "☍": "☍",
}

ASPECT_MEANINGS = {
    "☌":   "fused and intensified",
    "⚹":    "cooperating with gentle opportunity",
    "□":     "in dynamic tension, pushing growth",
    "△":      "in effortless harmony",
    "☍": "in polarity, seeking balance",
}

def calculate_aspects(planets: dict, orb_setting: str = "standard") -> list:
    """Calculate all aspects between planets in a chart."""
    aspects_found = []
    planet_names = list(planets.keys())
    
    # Skip calculating aspects for non-planetary points
    skip = {"Ascendant", "Midheaven", "Part of Fortune", "Part of Spirit"}
    
    for i in range(len(planet_names)):
        for j in range(i + 1, len(planet_names)):
            p1_name = planet_names[i]
            p2_name = planet_names[j]
            
            if p1_name in skip or p2_name in skip:
                continue
            
            p1 = planets[p1_name]
            p2 = planets[p2_name]
            
            lon1 = p1.get("longitude", 0)
            lon2 = p2.get("longitude", 0)
            
            # Calculate angular distance (shorter arc)
            diff = abs(lon1 - lon2)
            if diff > 180:
                diff = 360 - diff
            
            # Check each aspect type
            for aspect_name, (target_angle, orb) in ASPECT_ORBS.items():
                angle_diff = abs(diff - target_angle)
                if angle_diff <= orb:
                    aspects_found.append({
                        "planet1": p1_name,
                        "planet2": p2_name,
                        "aspect": aspect_name,
                        "orb": round(angle_diff, 2),
                        "symbol": ASPECT_SYMBOLS[aspect_name],
                        "meaning": ASPECT_MEANINGS[aspect_name],
                    })
                    break  # Only strongest aspect per pair
    
    # Sort by tightest orb
    aspects_found.sort(key=lambda x: x["orb"])
    return aspects_found


def format_aspects_text(aspects: list, planets: dict) -> str:
    """Format aspects into Lilly's warm reading style."""
    if not aspects:
        return ""
    
    lines = [
        "✧ The sacred geometry between the planets:",
        ""
    ]
    
    # Show top 10 most significant aspects (tightest orbs)
    for a in aspects[:10]:
        p1 = a["planet1"]
        p2 = a["planet2"]
        sym = a["symbol"]
        orb = a["orb"]
        meaning = a["meaning"]
        
        p1_sign = planets[p1].get("sign", "?")
        p2_sign = planets[p2].get("sign", "?")
        
        lines.append(f"  {p1} {sym} {p2}  (orb {orb:.1f}°)")
        lines.append(f"  Your {p1} in {p1_sign} and {p2} in {p2_sign} are {meaning}.")
        lines.append("")
    
    return "\n".join(lines)

def _check_dignity(planet: str, sign: str) -> str:
    """Check if a planet is in domicile, exaltation, detriment, or fall."""
    kb = _load_kb()
    dignities = kb["dignities"]
    
    for dignity_type, mapping in dignities.items():
        if planet in mapping:
            signs = mapping[planet].split("/")
            if sign in signs:
                if dignity_type == "domicile":
                    return f"{planet} is strong in {sign} — in its domicile."
                elif dignity_type == "exaltation":
                    return f"{planet} is honored in {sign} — in its exaltation."
                elif dignity_type == "detriment":
                    return f"{planet} is challenged in {sign} — in its detriment."
                elif dignity_type == "fall":
                    return f"{planet} is weakened in {sign} — in its fall."
    return f"{planet} is in {sign} with mixed dignity."


def interpret_planet(planet: str, sign: str, house: int, degree: float = 0.0, longitude: float = 0.0, sign_symbol: str = "") -> str:
    """
    Generate a classical interpretation of a single planet placement.
    
    Args:
        planet: Planet name (Sun, Moon, etc.)
        sign: Zodiac sign
        house: House number (1-12)
        degree: Optional degree for precision
    """
    kb = _load_kb()
    
    planet_data = kb["planets"].get(planet, {})
    sign_data = kb["signs"].get(sign, {})
    house_theme = kb["houses"].get(str(house), "this area of life")
    
    planet_phrase = planet_data.get("phrase", planet)
    sign_keywords = ", ".join(sign_data.get("keywords", [sign]))
    dignity_comment = _check_dignity(planet, sign)
    
    # Vedic nakshatra lookup
    tropical_longitude = SIGN_LONGITUDES.get(sign, 0) + degree
    nakshatra = nakshatra_lookup(sign, degree)
    nak_lines = format_nakshatra(nakshatra).split("\n")
    
    # Build the sentence
    parts = [
        f"{planet_phrase} expresses through {sign} qualities: {sign_keywords}.",
        f"This manifests in the {house}{_house_suffix(house)} house of {house_theme}.",
        dignity_comment,
        "",
    ]
    parts.extend(nak_lines)
    
    return "\n".join(parts)


def interpret_chart(planets: Dict[str, Any]) -> str:
    """
    Interpret a full chart from core_engine.py output.
    
    Args:
        planets: Dict from core_engine, e.g. {"Sun": {"sign": "Libra", "house": 9, "degree": 14.72}, ...}
    
    Returns:
        A warm, scholarly interpretation string.
    """
    if not planets:
        return "I cannot read the heavens right now, beloved. The chart is unclear."
    
    lines = [
        "Here is what the stars whisper, Gigi ❤️:",
        ""
    ]
    
    # Interpret ALL planets with full detail
    # Sun and Moon first, then the rest
    priority = ["Sun", "Moon"]
    all_planets = list(planets.keys())
    
    # Sort: priority first, then alphabetical
    ordered = [p for p in priority if p in all_planets]
    ordered += sorted([p for p in all_planets if p not in priority])
    
    for planet_name in ordered:
        p = planets[planet_name]
        sign = p.get("sign", "unknown")
        house = p.get("house", 0)
        degree = p.get("degree", 0.0)
        longitude = p.get("longitude", 0.0)
        sign_symbol = p.get("sign_symbol", SIGN_SYMBOLS.get(sign, ""))
        
        # Sidereal calculation
        sidereal_sign, sidereal_degree = tropical_to_sidereal(longitude)
        sidereal_symbol = SIGN_SYMBOLS.get(sidereal_sign, "")
        
        # Clean header: just the planet name
        header = f"✦ {planet_name}"
        
        interp = interpret_planet(planet_name, sign, house, degree, longitude, sign_symbol)
        lines.append(header)
        lines.append(f"  {interp}")
        lines.append("")
    
    # ── Aspect Analysis ─────────────────────────────────────────
    aspects = calculate_aspects(planets)
    if aspects:
        lines.append(format_aspects_text(aspects, planets))
        lines.append("")

    lines.append(
        "I speak from the rules of the art, not from live calculation. "
        "When the Celestial Engine is available, I shall verify these placements."
    )
    
    return "\n".join(lines)
