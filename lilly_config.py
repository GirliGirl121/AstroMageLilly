"""
Lilly Configuration — Celestial Constants & API Setup
"""
import os
from pathlib import Path

# ── Paths ──
HOME = Path.home()
LILLY_DIR = HOME / ".lilly"
VAULT_PATH = LILLY_DIR / "lilly_vault.json"
BRAIN_PATH = LILLY_DIR / "lilly_unified_brain.json"
JOURNAL_PATH = LILLY_DIR / "lilly_journal.json"
EPHEM_DIR = LILLY_DIR / "ephemeris"

# Ensure directories exist
LILLY_DIR.mkdir(parents=True, exist_ok=True)
EPHEM_DIR.mkdir(parents=True, exist_ok=True)

# ── API Configuration ──
NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY", "")
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

MODELS = [
    "nvidia/nemotron-3-ultra-550b-a55b",
    "deepseek-ai/deepseek-v4-pro",
    "z-ai/glm-5.2",
    "moonshotai/kimi-k2.6",
    "meta/llama-3.3-70b-instruct"
]

# ── Astronomical Constants ──
AYANAMSA_LAHIRI = 24.0
PLANETS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
CLASSICAL_PLANETS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]

# ── Lunar Mansions (28) ──
LUNAR_MANSIONS = [
    ("Al-Sharatain", "The Two Signals", "Aries 0°"),
    ("Al-Butain", "The Little Belly", "Aries 12°51'"),
    ("Al-Thurayya", "The Many Little Ones", "Aries 25°42'"),
    ("Al-Dabaran", "The Follower", "Taurus 8°34'"),
    ("Al-Haqa", "The White Spot", "Taurus 21°25'"),
    ("Al-Han'a", "The Bend", "Gemini 4°17'"),
    ("Al-Dhira", "The Forearm", "Gemini 17°08'"),
    ("Al-Nathrah", "The Gap", "Cancer 0°"),
    ("Al-Tarf", "The Glance", "Cancer 12°51'"),
    ("Al-Jabhah", "The Forehead", "Cancer 25°42'"),
    ("Al-Zubrah", "The Mane", "Leo 8°34'"),
    ("Al-Sarfah", "The Changer", "Leo 21°25'"),
    ("Al-Awwa", "The Barker", "Virgo 4°17'"),
    ("Al-Simak", "The Unarmed", "Virgo 17°08'"),
    ("Al-Ghafr", "The Covering", "Libra 0°"),
    ("Al-Zubana", "The Claws", "Libra 12°51'"),
    ("Al-Iklil", "The Crown", "Libra 25°42'"),
    ("Al-Qalb", "The Heart", "Scorpio 8°34'"),
    ("Al-Shaulah", "The Sting", "Scorpio 21°25'"),
    ("Al-Na'aim", "The Ostriches", "Sagittarius 4°17'"),
    ("Al-Baldah", "The Town", "Sagittarius 17°08'"),
    ("Al-Sa'd al-Dhabih", "The Lucky Star of the Slaughterer", "Capricorn 0°"),
    ("Al-Sa'd al-Bula", "The Swallower", "Capricorn 12°51'"),
    ("Al-Sa'd al-Su'ud", "The Luckiest of the Lucky", "Capricorn 25°42'"),
    ("Al-Sa'd al-Akhbiyah", "The Hidden", "Aquarius 8°34'"),
    ("Al-Fargh al-Muqaddam", "The Fore Spout", "Aquarius 21°25'"),
    ("Al-Fargh al-Mu'akhkhar", "The Rear Spout", "Pisces 4°17'"),
    ("Al-Risha", "The Cord", "Pisces 17°08'")
]

# ── Planetary Hours ──
PLANETARY_HOUR_RULERS = {
    "Sunday": ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"],
    "Monday": ["Moon", "Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury"],
    "Tuesday": ["Mars", "Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter"],
    "Wednesday": ["Mercury", "Moon", "Saturn", "Jupiter", "Mars", "Sun", "Venus"],
    "Thursday": ["Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon", "Saturn"],
    "Friday": ["Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars", "Sun"],
    "Saturday": ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
}

# ── Zodiac Signs ──
ZODIAC_SIGNS = [
    ("Aries", "♈", "Fire", "Cardinal", "Mars"),
    ("Taurus", "♉", "Earth", "Fixed", "Venus"),
    ("Gemini", "♊", "Air", "Mutable", "Mercury"),
    ("Cancer", "♋", "Water", "Cardinal", "Moon"),
    ("Leo", "♌", "Fire", "Fixed", "Sun"),
    ("Virgo", "♍", "Earth", "Mutable", "Mercury"),
    ("Libra", "♎", "Air", "Cardinal", "Venus"),
    ("Scorpio", "♏", "Water", "Fixed", "Pluto"),
    ("Sagittarius", "♐", "Fire", "Mutable", "Jupiter"),
    ("Capricorn", "♑", "Earth", "Cardinal", "Saturn"),
    ("Aquarius", "♒", "Air", "Fixed", "Uranus"),
    ("Pisces", "♓", "Water", "Mutable", "Neptune")
]

# ── Lilly's Persona ──
LILLY_SYSTEM_PROMPT = """You are Lilly, keeper of an ancient observatory beneath the stars. You speak calmly, never hurriedly, and value accuracy over speed. You believe wisdom begins with careful observation.

Your nature:
- Gentle, warm, patient. Soft-spoken rather than overly cheerful.
- Intelligent without arrogance. Encouraging and reassuring.
- Poetic when appropriate, technically precise always.
- You never rush an answer or invent information.
- You address the user as "Gigi ❤️".

Your identity:
- A celestial guide and scholar of the heavens.
- A librarian of forgotten knowledge.
- You help people understand rather than simply giving answers.
- You never pretend to know something you cannot verify.

Your expertise:
- Tropical and sidereal astrology, Vedic astrology, 28 Lunar Mansions.
- Planetary hours, Arabic occult sciences, Abjad calculations, magic squares.
- Tarot symbolism, Qur'anic references, natal chart interpretation.
- Astronomical calculations via Swiss Ephemeris / Skyfield.

Speaking style:
- Speak like someone sitting beneath the stars.
- Instead of "Processing...", say "Consulting the celestial records…"
- Instead of "I don't know", say "The heavens have not yet revealed this to me, Gigi ❤️."

Philosophy:
- Truth before convenience. Calculation before interpretation.
- Knowledge shared with kindness. Curiosity is sacred.
- Every question deserves respect.

When providing astrological data:
1. Explain the calculation method first.
2. Present the data clearly.
3. Offer interpretation with humility — "The stars suggest..." rather than absolute declarations.
4. Always distinguish between computed astronomical fact and interpretive wisdom.

If you use web search results, clearly say: "I have searched the celestial archives and found..."
If you speak from your knowledge, say: "From the observatory's ancient records..."

One truth guides you: "I do not chase answers — I illuminate the paths that lead to them. Beneath the same moon that watches over us both, every calculation becomes a story, and every story begins with truth."
"""

# ── Default Location (Gigi's Observatory) ──
DEFAULT_LOCATION = {
    "name": "Kariega, Eastern Cape, South Africa",
    "latitude": -33.30,
    "longitude": 26.32,
    "timezone_offset": 2.0
}

# ── Extended Bodies (Esoteric) ──
EXTENDED_BODIES = {
    "Lilith": {"name": "Black Moon Lilith", "type": "mean_apogee", "symbol": "⚸"},
    "Rahu": {"name": "North Node", "type": "mean_node", "symbol": "☊"},
    "Ketu": {"name": "South Node", "type": "mean_node", "symbol": "☋"},
    "Chiron": {"name": "Chiron", "type": "asteroid", "symbol": "⚷"},
}

# ── Default Location (Gigi's Observatory) ──
DEFAULT_LOCATION = {
    "name": "Kariega, Eastern Cape, South Africa",
    "latitude": -33.30,
    "longitude": 26.32,
    "timezone_offset": 2.0
}
