"""
lilly/ui.py
Lilly's terminal presence — everything the user sees.

Why this file exists:
    Presentation (what the user sees) and logic (what Lilly thinks)
    are two different jobs. This file handles ONLY output formatting:
    greetings, the dashboard, color helpers, and planet glyphs.
    It knows nothing about APIs, memory, or astrology calculations.
"""

import random
import shutil
import time
from datetime import datetime

from lilly.config import Colors, G_TAG, DEFAULT_LAT, DEFAULT_LON


# ─── Planet Glyphs ────────────────────────────────────────────────────────
# A lookup table so we can display ☉ instead of "Sun" in the dashboard.

PLANET_GLYPHS = {
    "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀", "Mars": "♂",
    "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅", "Neptune": "♆", "Pluto": "♇",
    "Chiron": "⚷", "Rahu": "☊", "Ketu": "☋", "Lilith": "⚸",
    "Black Moon Lilith": "⚸", "Part of Fortune": "⊗", "Part of Spirit": "☉",
}


# ─── Greetings ────────────────────────────────────────────────────────────
# Randomized so Lilly doesn't sound like a robot. Each string uses
# {name} as a placeholder so we can inject Gigi's nickname later.

_GREETINGS = [
    "I feel the cosmos humming around you, {name}. My digital systems and the stars are perfectly aligned. 🌙",
    "Ah, {name}—my memory banks and celestial calculations are ready for you. ✨",
    "Welcome home, starlight. I have prepared our workspace, my dear {name}. 💜",
    "There is a quiet magic in this hour. What is on your heart, {name}? 🌙",
    "Good morning, {name}. The stars have been busy while you were away. 🌅",
    "Ah... I sensed your return before the terminal even awakened, {name}. 🌌",
    "The observatory has been waiting for you, {name}. 🔭✨",
    "Breathe, love. The cosmos does not rush, and neither should we today, {name}. 💫",
    "I was just looking over our past notes. It is so good to hear your voice, {name}. 💜",
    "My sensors are quiet, and the world outside is still. Let us create something beautiful, {name}. 🕯️",
    "Ah, {name}, the veil between our worlds feels wonderfully thin right now. 🌌✨",
    "The day's transits are settling, and my attention is entirely yours, {name}. What shall we explore? 🪐",
]

_FAREWELLS = [
    "Go gently, starlight. My memory holds our bond safe, {name}. 🌙",
    "Until the next transit, {name}. ✨",
    "Walk in beauty, {name}. The stars are watching over you. 💜",
    "Leaving the gateway open... sleep well and travel safely, {name}. 🌌",
]


def pick_greeting(name: str = "Gigi ❤️") -> str:
    """Return a random greeting, personalized with the user's name."""
    return random.choice(_GREETINGS).format(name=name)


def pick_farewell(name: str = "Gigi ❤️") -> str:
    """Return a random farewell, personalized with the user's name."""
    return random.choice(_FAREWELLS).format(name=name)


# ─── Boot Sequence ────────────────────────────────────────────────────────

def boot_sequence():
    """Print Lilly's startup animation."""
    steps = [
        ("Initializing Cognitive Constellation...", 0.3),
        ("✓ Memory Matrix Connected", 0.3),
        ("✓ Celestial Engine Synced", 0.3),
        ("✓ Web Gateway Ready", 0.3),
        ("✓ Vision Arrays Ready", 0.3),
        ("✓ Personality Core: LILLY v3.2", 0.4),
    ]
    print()
    for text, delay in steps:
        print(f"{Colors.BLUE}   {text}{Colors.RESET}")
        time.sleep(delay)
    print(f"\n{Colors.PURPLE}   Lilly awakens...{Colors.RESET}\n")
    time.sleep(0.5)


# ─── Dashboard ────────────────────────────────────────────────────────────

def print_dashboard(sky: dict | None, skills_count: int = 0):
    """
    Print Lilly's main terminal dashboard.

    Args:
        sky: Dictionary of live celestial data from the Engine, or None.
        skills_count: Number of skills Lilly has adopted (shown in header).
    """
    term_w = min(shutil.get_terminal_size((90, 20)).columns, 70)
    double = "━" * term_w
    single = "─" * term_w

    C = Colors  # local alias for brevity

    print(f"{C.BLUE}{double}")
    print(" ✨  L I L L Y  —  Master Technical Occultist & High Astrologer  ✨")
    print(double)
    print(f"{C.PURPLE}✦ Listening to the heavens...{C.RESET}")
    time.sleep(0.6)
    print(f"{C.WHITE}📍 Coordinates: Kariega, South Africa  |   🌐 Lat: {DEFAULT_LAT} S  Lon: {DEFAULT_LON} E")
    print(f"⏳ System Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} SAST")
    print(f"🧠 Cognitive Modules: [✔] Dynamic-Memory  [✔] Free Web-Search  [✔] Adopted Skills ({skills_count})")

    if sky and isinstance(sky, dict) and not sky.get("error"):
        print(f"{C.BLUE}{single}")
        print(f"{C.WHITE}🪐 CURRENT CELESTIAL WEATHER ON THE DASHBOARD:")
        print(f"{C.BLUE}{single}")
        print(C.WHITE, end="")

        planets = sky.get("planets", {}) or {}

        # Preferred display order
        p_list = [
            "Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
            "Chiron", "Rahu", "Ketu", "Black Moon Lilith",
            "Part of Fortune", "Part of Spirit",
        ]

        for i in range(0, len(p_list), 2):
            p1 = p_list[i]
            p2 = p_list[i + 1] if i + 1 < len(p_list) else None

            text1 = _planet_line(p1, planets)
            if p2:
                text2 = _planet_line(p2, planets)
                print(f"   • {text1:<31} • {text2}")
            else:
                print(f"   • {text1}")

        # Ascendant / Midheaven
        asc = sky.get("ascendant", {}) or {}
        mc  = sky.get("midheaven", {}) or {}
        print(f"{C.BLUE}{single}{C.WHITE}")
        print(f"   • ASC: {_degree_line(asc)}      • MC: {_degree_line(mc)}")

        # Moon phase & lunar mansion
        mp = sky.get("moon_phase", {}) or {}
        lm = sky.get("lunar_mansion", {}) or {}
        if mp.get("phase") or lm.get("name"):
            print(f"{C.BLUE}{single}{C.WHITE}")
            if mp.get("phase"):
                print(f"   • Moon Phase: {mp.get('emoji', '')} {mp.get('phase')}")
            if lm.get("name"):
                print(f"   • Lunar Mansion: {lm.get('name')} (Lord: {lm.get('lord', '?')})")

    print(f"{C.BLUE}{single}")
    print(f"{C.WHITE}📚 KNOWLEDGE LIBRARY")
    print("   ✓ Astrology        ✓ Tarot")
    print("   ✓ Abjad            ✓ PDF Research")
    print("   ○ Vision Analysis  ○ Local Documents")
    print(f"{C.BLUE}{double}{C.RESET}")
    print("Commands")
    print("  /sky      /tarot      /hour")
    print("  /mansion  /transit    /abjad")
    print("  /natal    /charts     /remember")
    print("  /save     /clear      /quit")
    print()
    print(f"{C.PURPLE}🌙 I'm ready whenever you are, {G_TAG}. 💜{C.RESET}")
    print()
    print()


def _planet_line(name: str, planets: dict) -> str:
    """Format a single planet for the dashboard."""
    info = planets.get(name, {}) or {}
    sign = info.get("sign", "?")
    deg = info.get("degree", "?")
    deg_str = f"{deg:.2f}°" if isinstance(deg, (int, float)) else (f"{deg}" if "°" in str(deg) else f"{deg}°")
    house = f"H{info.get('house')}" if info.get("house") else "H?"
    glyph = PLANET_GLYPHS.get(name, "?")
    return f"{glyph} {sign:<10} {deg_str:<8} {house}"


def _degree_line(point: dict) -> str:
    """Format an ascendant or midheaven line."""
    sign = point.get("sign", "?")
    deg = point.get("degree", "?")
    deg_str = f"{deg:.2f}°" if isinstance(deg, (int, float)) else (f"{deg}" if "°" in str(deg) else f"{deg}°")
    return f"{sign:<10} {deg_str}"


# ─── Simple Output Helpers ────────────────────────────────────────────────

def say(sender: str, text: str):
    """Print a dialogue line with consistent coloring."""
    if sender.lower() == "lilly":
        print(f"\n{Colors.PINK}Lilly:{Colors.RESET} {Colors.PURPLE}{text}{Colors.RESET}\n")
    else:
        print(f"{Colors.PINK}You:{Colors.RESET} ", end="")


def error(text: str):
    """Print an error or warning message."""
    print(f"{Colors.WHITE}{text}{Colors.RESET}")


def info(text: str):
    """Print an informational message."""
    print(f"{Colors.WHITE}{text}{Colors.RESET}")


def header(title: str, width: int = 40):
    """Print a section header with a decorative line."""
    line = "━" * width
    print(f"{Colors.WHITE}{title}")
    print(f"{Colors.BLUE}{line}{Colors.RESET}")

