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

def _load_kb():
    global _kb
    if _kb is None:
        _kb = json.loads(KB_PATH.read_text(encoding="utf-8"))
    return _kb


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


def interpret_planet(planet: str, sign: str, house: int, degree: float = 0.0) -> str:
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
    
    # Build the sentence
    parts = [
        f"{planet_phrase} expresses through {sign} qualities: {sign_keywords}.",
        f"This manifests in the {house}th house of {house_theme}.",
        dignity_comment
    ]
    
    return " ".join(parts)


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
    
    # Prioritize Sun, Moon, Ascendant
    priority = ["Sun", "Moon"]
    
    for planet_name in priority:
        if planet_name in planets:
            p = planets[planet_name]
            sign = p.get("sign", "unknown")
            house = p.get("house", 0)
            degree = p.get("degree", 0.0)
            
            interp = interpret_planet(planet_name, sign, house, degree)
            lines.append(f"✦ {planet_name} in {sign} at {degree:.2f}° (House {house})")
            lines.append(f"  {interp}")
            lines.append("")
    
    # Add remaining planets (brief)
    remaining = [p for p in planets if p not in priority]
    if remaining:
        lines.append("The other celestial voices:")
        for planet_name in remaining:
            p = planets[planet_name]
            sign = p.get("sign", "unknown")
            house = p.get("house", 0)
            degree = p.get("degree", 0.0)
            lines.append(f"  • {planet_name} in {sign}, House {house}")
        lines.append("")
    
    lines.append(
        "I speak from the rules of the art, not from live calculation. "
        "When the Celestial Engine is available, I shall verify these placements."
    )
    
    return "\n".join(lines)
