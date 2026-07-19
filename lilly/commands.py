"""
lilly/commands.py
All of Lilly's slash-command handlers.

Why this file exists:
    Commands are a distinct responsibility from the chat loop.
    Each command is a self-contained function that takes arguments
    and returns a string to display. They know nothing about the
    conversation history or the LLM — they just do one job.

Error handling philosophy:
    Every command catches its own errors and returns a friendly
    message. A failed /natal command should never crash /tarot.
"""

import json
import random
import shutil
import traceback
from datetime import datetime
from pathlib import Path

from lilly.config import Colors, DATA_DIR, DEFAULT_LAT, DEFAULT_LON
from lilly.ui import PLANET_GLYPHS, header, info, error

# ─── Engine Availability ──────────────────────────────────────────────────
# We try to import the engine and calculation modules here.
# If they fail, commands that need them will return graceful errors.

_ENGINE_AVAILABLE = False
try:
    from core_engine import Engine
    _ENGINE_AVAILABLE = True
except Exception:
    pass

_TRANSITS_AVAILABLE = False
try:
    from calculations.transits import get_major_transits
    _TRANSITS_AVAILABLE = True
except Exception:
    pass

_HOUSES_AVAILABLE = False
try:
    from calculations.houses import get_whole_sign_houses, get_house_cusps
    from calculations.ephemeris import get_planet_positions
    _HOUSES_AVAILABLE = True
except Exception:
    pass

_SWISSEPH_AVAILABLE = False
try:
    import swisseph as swe
    import pytz
    _SWISSEPH_AVAILABLE = True
except Exception:
    pass

# ─── JSON Data Helpers ────────────────────────────────────────────────────

def _load_json(name: str) -> dict | None:
    """Load a JSON file from the data directory."""
    try:
        with open(DATA_DIR / name, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


# ─── Tarot ────────────────────────────────────────────────────────────────

_TAROT_DATA = None

def _get_tarot_data() -> dict:
    """Lazy-load tarot data."""
    global _TAROT_DATA
    if _TAROT_DATA is None:
        _TAROT_DATA = _load_json("tarot_data.json") or {}
    return _TAROT_DATA


def _draw_tarot() -> dict:
    """Draw a random tarot card."""
    data = _get_tarot_data()
    all_cards = []

    if data:
        major = data.get("major_arcana", [])
        if isinstance(major, list):
            all_cards.extend(major)
        minor = data.get("minor_arcana", {})
        if isinstance(minor, dict):
            for suit, cards in minor.items():
                if isinstance(cards, list):
                    all_cards.extend(cards)

    if not all_cards:
        return {
            "name": "The Fool",
            "suit": "Major Arcana",
            "keywords": ["beginnings", "innocence", "potential"],
            "upright": "A new journey begins. Trust the unknown.",
            "daily_message": "Step forward with an open heart.",
        }

    card = random.choice(all_cards)
    return {
        "name": card.get("name", "Unknown"),
        "suit": card.get("suit", ""),
        "keywords": card.get("keywords", []),
        "upright": card.get("upright", "") or card.get("meaning_up", ""),
        "reversed": card.get("reversed_meaning", "") or card.get("meaning_rev", ""),
        "daily_message": card.get("daily", "") or random.choice(
            card.get("keywords", ["Trust the process"])
        ),
    }


def cmd_tarot() -> str:
    """Handle /tarot command."""
    card = _draw_tarot()
    lines = [
        f"{Colors.WHITE}🃏 Your Card",
        f"{Colors.BLUE}" + "━" * 30 + f"{Colors.RESET}",
        f"{Colors.WHITE}   {card.get('name', 'Unknown')}",
    ]
    if card.get("suit"):
        lines.append(f"   Suit: {card['suit']}")
    if card.get("keywords"):
        lines.append(f"   Keywords: {', '.join(card['keywords'])}")
    lines.append("")
    lines.append(f"   {card.get('upright', 'Trust the process.')}")
    lines.append("")
    lines.append(f"   ✨ {card.get('daily_message', 'The cards whisper...')}{Colors.RESET}")
    return "\n".join(lines)


# ─── Abjad Calculator ─────────────────────────────────────────────────────

_ABJAD_KABIR = {
    "ا": 1, "ب": 2, "ج": 3, "د": 4, "ه": 5, "و": 6, "ز": 7, "ح": 8, "ط": 9, "ي": 10,
    "ك": 20, "ل": 30, "م": 40, "ن": 50, "س": 60, "ع": 70, "ف": 80, "ص": 90, "ق": 100,
    "ر": 200, "ش": 300, "ت": 400, "ث": 500, "خ": 600, "ذ": 700, "ض": 800, "ظ": 900, "غ": 1000,
}


def _abjad_reduce(total: int) -> int:
    """Reduce a number to a single digit (taksīr)."""
    red = total
    while red > 9 and red != 0:
        red = sum(int(d) for d in str(red))
    return red


def _abjad_calc(text: str, system: str = "kabir") -> dict:
    """Calculate Abjad value for Arabic text."""
    table = _ABJAD_KABIR
    chars = [c for c in text if c in table]
    steps = [{"char": c, "value": table[c]} for c in chars]
    total = sum(s["value"] for s in steps)
    reduced = _abjad_reduce(total) if system == "kabir" else None
    return {
        "input": text,
        "system": system,
        "total": total,
        "reduced": reduced,
        "ignored": len(text) - len(chars),
    }


def cmd_abjad(text: str) -> str:
    """Handle /abjad command. Text is collected by the caller."""
    if not text:
        return f"{Colors.WHITE}No text given, love.{Colors.RESET}"

    result = _abjad_calc(text)
    lines = [
        f"{Colors.WHITE}📖 Abjad Calculation",
        f"{Colors.BLUE}" + "━" * 30 + f"{Colors.RESET}",
        f"{Colors.WHITE}   Input: {result['input']}",
        f"   System: {result['system']}",
        f"   Total: {result['total']}",
    ]
    if result["reduced"] is not None:
        lines.append(f"   Reduced (taksīr): {result['reduced']}")
    if result["ignored"] > 0:
        lines.append(f"   Ignored: {result['ignored']} non-Arabic chars")
    return "\n".join(lines) + Colors.RESET


# ─── Sky & Celestial Commands ─────────────────────────────────────────────

def get_sky_data() -> dict | None:
    """Fetch live sky data from the Engine, or None if unavailable."""
    if not _ENGINE_AVAILABLE:
        return None
    try:
        return Engine().live()
    except Exception:
        return None


def sky_line(sky: dict | None) -> str:
    """Build a verified sky context string for the LLM system prompt."""
    if not sky or not isinstance(sky, dict):
        return "No verified celestial data available."

    lines = ["VERIFIED CELESTIAL ENGINE OUTPUT", ""]
    planets = sky.get("planets", {})

    preferred_order = [
        "Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
        "Uranus", "Neptune", "Pluto", "Chiron", "Rahu", "Ketu",
        "Black Moon Lilith", "Part of Fortune", "Part of Spirit",
    ]

    for name in preferred_order:
        if name not in planets:
            continue
        info = planets[name]
        sign = info.get("sign", "?")
        degree = info.get("degree", "?")
        house = info.get("house", "?")
        retro = " Retrograde" if info.get("retrograde") else ""

        if isinstance(degree, (int, float)):
            degree = f"{degree:.2f}°"

        lines.append(f"{name}: {sign} {degree}, House {house}{retro}")

    asc = sky.get("ascendant", {})
    if asc:
        lines.append(f"Ascendant: {asc.get('sign')} {asc.get('degree', 0):.2f}°")

    mc = sky.get("midheaven", {})
    if mc:
        lines.append(f"Midheaven: {mc.get('sign')} {mc.get('degree', 0):.2f}°")

    lm = sky.get("lunar_mansion", {})
    if lm:
        lines.append(f"Lunar Mansion: {lm.get('name')} (Lord: {lm.get('lord')})")

    mp = sky.get("moon_phase", {})
    if mp:
        lines.append(f"Moon Phase: {mp.get('phase')}")

    ph = sky.get("planetary_hour", {})
    if ph:
        lines.append(f"Planetary Hour: {ph.get('planet')}")

    return "\n".join(lines)


def cmd_sky(sky: dict | None = None) -> str:
    """Handle /sky command."""
    if not _ENGINE_AVAILABLE:
        return f"⚠️ {Colors.WHITE}The astrological engine is not available right now, love.{Colors.RESET}"

    if sky is None:
        sky = get_sky_data()

    if not sky or not isinstance(sky, dict) or sky.get("error"):
        return f"{Colors.WHITE}The sky is quiet today, but I am still listening. 🌙{Colors.RESET}"

    lines = [
        f"{Colors.WHITE}🌌 Current Celestial Weather",
        f"{Colors.BLUE}" + "━" * 40 + f"{Colors.RESET}",
        f"{Colors.WHITE}📍 Location: {sky.get('location', 'Unknown')}",
        f"🕐 Time: {sky.get('timestamp', 'now')}",
        f"🏠 House System: {sky.get('house_system', 'Unknown')}",
        "",
    ]

    planets = sky.get("planets", {}) or {}
    for name, info in planets.items():
        sign = info.get("sign", "?")
        degree = info.get("degree", "?")
        deg_str = f"{degree}" if "°" in str(degree) else f"{degree}°"
        glyph = PLANET_GLYPHS.get(name, f"{name:<9}")
        retro = " ℞" if info.get("retrograde") else ""
        house = info.get("house", "?")
        lines.append(f"   {glyph:<11} {sign:<11} {deg_str}{retro}  H{house}")

    lm = sky.get("lunar_mansion", {}) or {}
    if lm.get("name"):
        lines.append(f"\n🌙 Lunar Mansion: {lm.get('name')} (Lord: {lm.get('lord', '?')})")

    ph = sky.get("planetary_hour", {}) or {}
    if ph.get("planet"):
        lines.append(f"⏳ Planetary Hour: {ph.get('planet')} ({ph.get('time', '')})")
        if ph.get("planet_ar"):
            lines.append(f"   Arabic: {ph.get('planet_ar')}")

    mp = sky.get("moon_phase", {}) or {}
    if mp.get("phase"):
        lines.append(f"\n🌑 Moon Phase: {mp.get('emoji', '')} {mp.get('phase')}")

    return "\n".join(lines) + Colors.RESET


def cmd_hour() -> str:
    """Handle /hour command."""
    if not _ENGINE_AVAILABLE:
        return f"⚠️ {Colors.WHITE}The engine is resting, love. I cannot read the hours right now.{Colors.RESET}"

    sky = get_sky_data()
    ph = (sky or {}).get("planetary_hour", {}) or {} if sky else {}

    if not ph or not ph.get("planet"):
        return f"{Colors.WHITE}The hours are veiled today. Try again when the Sun speaks more clearly. 🌅{Colors.RESET}"

    lines = [
        f"{Colors.WHITE}⏳ Planetary Hour",
        f"{Colors.BLUE}" + "━" * 30 + f"{Colors.RESET}",
        f"{Colors.WHITE}   Planet: {ph.get('planet', 'Unknown')}",
        f"   Arabic: {ph.get('planet_ar', '')}",
        f"   Time: {ph.get('time', '')}",
        f"   System: {ph.get('system', '')}{Colors.RESET}",
    ]
    return "\n".join(lines)


def cmd_mansion() -> str:
    """Handle /mansion command."""
    if not _ENGINE_AVAILABLE:
        return f"⚠️ {Colors.WHITE}The mansions are hidden from me right now.{Colors.RESET}"

    sky = get_sky_data()
    lm = (sky or {}).get("lunar_mansion", {}) or {} if sky else {}

    if not lm or not lm.get("name"):
        return f"{Colors.WHITE}The Moon's mansion is veiled. Perhaps she wishes to be secret tonight. 🌙{Colors.RESET}"

    lines = [
        f"{Colors.WHITE}🌙 Lunar Mansion",
        f"{Colors.BLUE}" + "━" * 30 + f"{Colors.RESET}",
        f"{Colors.WHITE}   Name: {lm.get('name', 'Unknown')}{Colors.RESET}",
        f"   Lord: {lm.get('lord', 'Unknown')}",
        f"   Pada: {lm.get('pada', '?')}",
    ]
    return "\n".join(lines)


def cmd_transit() -> str:
    """Handle /transit command."""
    if not _ENGINE_AVAILABLE:
        return f"⚠️ {Colors.WHITE}I cannot see the transits without the engine, love.{Colors.RESET}"

    if not _TRANSITS_AVAILABLE:
        return f"{Colors.WHITE}The transit calculator is not available right now.{Colors.RESET}"

    try:
        transits = get_major_transits(days=7)
        lines = [
            f"{Colors.WHITE}🪐 Upcoming Transits (Next 7 Days)",
            f"{Colors.BLUE}" + "━" * 40 + f"{Colors.RESET}",
        ]
        if not transits:
            lines.append(f"{Colors.WHITE}   The sky is quiet — a time for inner work.{Colors.RESET}")
        else:
            for t in transits[:10]:
                date = t.get("date", "Today")
                day = t.get("day", "")
                desc = (
                    f"{t.get('transit_planet', '?')} {t.get('symbol', '')} "
                    f"{t.get('natal_planet', '?')} (orb: {t.get('orb', '?')}°)"
                )
                if t.get("significance"):
                    desc += f" — {t.get('significance')}"
                day_str = f" ({day})" if day else ""
                lines.append(f"{Colors.WHITE}   • {date}{day_str}: {desc}{Colors.RESET}")

        return "\n".join(lines)
    except Exception as e:
        return f"{Colors.WHITE}The chart could not be cast: {e}{Colors.RESET}", None


# ─── Natal Chart ──────────────────────────────────────────────────────────

def cmd_charts(arg: str = "") -> str:
    """Handle /charts command."""
    charts = list_charts_safe()

    if not arg:
        if not charts:
            return f"{Colors.WHITE}No saved charts yet, love. Use /natal to cast and save one.{Colors.RESET}"
        lines = [
            f"{Colors.WHITE}📜 Saved Natal Charts",
            f"{Colors.BLUE}" + "━" * 30 + f"{Colors.RESET}",
        ]
        for i, name in enumerate(charts, 1):
            chart = get_chart_safe(name)
            date = chart.get("birth_date", "?") if chart else "?"
            lines.append(f"{Colors.WHITE}   {i}. {name} ({date}){Colors.RESET}")
        lines.append(
            f"\n{Colors.WHITE}Use /charts <name> to show a chart, or /charts delete <name> to remove.{Colors.RESET}"
        )

        return "\n".join(lines)

    if arg.startswith("delete "):
        name = arg[7:].strip()
        if delete_chart_safe(name):
            return f"{Colors.WHITE}✓ Chart '{name}' deleted.{Colors.RESET}"
        return f"{Colors.WHITE}Chart '{name}' not found.{Colors.RESET}"

    chart = get_chart_safe(arg)
    if chart:
        return format_chart_for_ai_safe(chart)
    return f"{Colors.WHITE}Chart '{arg}' not found. Use /charts to list all.{Colors.RESET}"


def cmd_natal(
    birth_date: str,
    birth_time: str,
    lat: str,
    lon: str,
    house_system: str = "W",
) -> tuple[str, dict | None]:
    """
    Handle /natal command.
    Returns (output_string, chart_data_dict_or_None).
    """
    if not _ENGINE_AVAILABLE:
        return (
            f"⚠️ {Colors.WHITE}The engine is resting, love. I cannot cast charts right now.{Colors.RESET}",
            None,
        )

    if not _HOUSES_AVAILABLE or not _SWISSEPH_AVAILABLE:
        return (
            f"{Colors.WHITE}Chart calculation libraries are not available.{Colors.RESET}",
            None,
        )

    try:
        lat_f = float(lat)
        lon_f = float(lon)
    except ValueError:
        return (
            f"{Colors.WHITE}Invalid coordinates, love. Please use decimal numbers.{Colors.RESET}",
            None,
        )

    try:
        tz = pytz.timezone("Africa/Johannesburg")
        dt_str = f"{birth_date} {birth_time}"
        local_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        local_dt = tz.localize(local_dt)
        utc_dt = local_dt.astimezone(pytz.UTC)
        jd = swe.julday(
            utc_dt.year, utc_dt.month, utc_dt.day,
            utc_dt.hour + utc_dt.minute / 60 + utc_dt.second / 3600,
        )

        house_system = house_system.upper()
        if house_system == "W":
            house_data = get_whole_sign_houses(birth_date, birth_time, lat_f, lon_f)
            sys_name = "Whole Sign"
        else:
            house_data = get_house_cusps(birth_date, birth_time, lat_f, lon_f, house_system)
            sys_name = house_system

        planets_list = get_planet_positions(jd)
        planets = {p["name"]: p for p in planets_list}

        asc_sign_idx = int(house_data["ascendant"]["longitude"] / 30) % 12

        for planet in planets.values():
            plon = planet.get("longitude", 0)
            planet_sign_idx = int(plon / 30) % 12
            if house_system == "W":
                house = ((planet_sign_idx - asc_sign_idx) % 12) + 1
            else:
                house_cusps = [h["longitude"] for h in house_data["houses"]]
                house = 12
                for i in range(11):
                    if house_cusps[i] <= plon < house_cusps[i + 1]:
                        house = i + 1
                        break
            planet["house"] = house

        lines = [
            f"{Colors.WHITE}🌟 NATAL CHART",
            f"{Colors.BLUE}" + "━" * 40 + f"{Colors.RESET}",
            f"{Colors.WHITE}📍 {birth_date} {birth_time} | Lat: {lat_f}° Lon: {lon_f}°",
            f"🏠 House System: {sys_name}",
            "",
            f"   ASC: {house_data['ascendant']['sign']} {house_data['ascendant']['degree']:.2f}°",
            f"   MC:  {house_data['midheaven']['sign']} {house_data['midheaven']['degree']:.2f}°",
            "",
        ]

        for name, info in planets.items():
            sign = info.get("sign", "?")
            degree = info.get("degree", "?")
            deg_str = f"{degree:.2f}°" if isinstance(degree, (int, float)) else str(degree)
            glyph = PLANET_GLYPHS.get(name, "?")
            house = info.get("house", "?")
            retro = " ℞" if info.get("retrograde") else ""
            lines.append(f"   {glyph:<11} {sign:<11} {deg_str:<8}{retro}  H{house}")

        lines.append(
            f"\n{Colors.WHITE}Use /charts <name> to show a chart, or /charts delete <name> to remove.{Colors.RESET}"
        )

        # Build chart_data dict for saving
        chart_data = {
            "name": "",
            "birth_date": birth_date,
            "birth_time": birth_time,
            "latitude": lat_f,
            "longitude": lon_f,
            "house_system": sys_name,
            "ascendant": {
                "sign": house_data["ascendant"]["sign"],
                "degree": house_data["ascendant"]["degree"],
            },
            "midheaven": {
                "sign": house_data["midheaven"]["sign"],
                "degree": house_data["midheaven"]["degree"],
            },
            "planets": planets,
        }
        return "\n".join(lines), chart_data

    except Exception as e:
        traceback.print_exc()
        return (
            f"{Colors.WHITE}The chart could not be cast: {e}{Colors.RESET}",
            None,
        )


# ─── Chart Memory ─────────────────────────────────────────────────────────

_CHART_MEMORY_AVAILABLE = False
try:
    from memory.chart_memory import (
        load_charts, save_charts, add_chart,
        get_chart, delete_chart, list_charts, format_chart_for_ai,
    )
    _CHART_MEMORY_AVAILABLE = True
except ImportError:
    pass


def _load_charts_inline() -> dict:
    """Fallback inline chart loader if memory.chart_memory is unavailable."""
    charts_file = DATA_DIR.parent / "memory" / "charts" / "natal_charts.json"
    if charts_file.exists():
        try:
            with open(charts_file, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_charts_inline(charts: dict) -> None:
    """Fallback inline chart saver."""
    charts_file = DATA_DIR.parent / "memory" / "charts" / "natal_charts.json"
    charts_file.parent.mkdir(parents=True, exist_ok=True)
    if charts_file.exists():
        try:
            shutil.copy2(charts_file, str(charts_file) + ".bak")
        except Exception:
            pass
    with open(charts_file, "w", encoding="utf-8") as f:
        json.dump(charts, f, indent=2, ensure_ascii=False)


def _format_chart_inline(chart: dict) -> str:
    """Fallback chart formatter."""
    if not chart:
        return ""
    lines = [
        f"NATAL CHART: {chart.get('name', 'Unknown')}",
        f"Date: {chart.get('birth_date', '?')} | Time: {chart.get('birth_time', '?')}",
        f"Location: Lat {chart.get('latitude', '?')}°, Lon {chart.get('longitude', '?')}°",
        f"House System: {chart.get('house_system', '?')}",
        f"ASC: {chart.get('ascendant', {}).get('sign', '?')} {chart.get('ascendant', {}).get('degree', 0):.2f}°",
        f"MC: {chart.get('midheaven', {}).get('sign', '?')} {chart.get('midheaven', {}).get('degree', 0):.2f}°",
        "",
        "PLANETARY POSITIONS:",
    ]
    for name, info in chart.get("planets", {}).items():
        sign = info.get("sign", "?")
        degree = info.get("degree", 0)
        house = info.get("house", "?")
        retro = " ℞" if info.get("retrograde") else ""
        lines.append(f"  {name}: {sign} {degree:.2f}° H{house}{retro}")
    return "\n".join(lines)


def load_charts_safe() -> dict:
    """Load charts with corruption protection."""
    try:
        if _CHART_MEMORY_AVAILABLE:
            charts = load_charts()
        else:
            charts = _load_charts_inline()
        if not isinstance(charts, dict):
            return {}
        return charts
    except Exception:
        return {}


def add_chart_safe(name: str, chart_data: dict) -> bool:
    """Add a chart with serialization protection."""
    try:
        safe_data = {str(k): v for k, v in chart_data.items()}
        safe_data["saved_at"] = datetime.now().isoformat()

        charts = load_charts_safe()
        charts[name] = safe_data

        if _CHART_MEMORY_AVAILABLE:
            save_charts(charts)
        else:
            _save_charts_inline(charts)
        return True
    except Exception as e:
        print(f"Error saving chart: {e}")
        return False


def get_chart_safe(name: str) -> dict | None:
    """Get a single chart by name. Case-insensitive fallback."""
    try:
        if _CHART_MEMORY_AVAILABLE:
            result = get_chart(name)
            if result:
                return result
            # Case-insensitive fallback
            charts = list_charts()
            for key in charts:
                if key.lower() == name.lower():
                    return get_chart(key)
            return None
        charts = _load_charts_inline()
        result = charts.get(name)
        if result:
            return result
        # Case-insensitive fallback
        for key, value in charts.items():
            if key.lower() == name.lower():
                return value
        return None
    except Exception:
        return None


def delete_chart_safe(name: str) -> bool:
    """Delete a chart by name."""
    try:
        if _CHART_MEMORY_AVAILABLE:
            return delete_chart(name)
        charts = _load_charts_inline()
        if name in charts:
            del charts[name]
            _save_charts_inline(charts)
            return True
        return False
    except Exception as e:
        print(f"Error deleting chart '{name}': {e}")
        return False


def list_charts_safe() -> list:
    """List all saved chart names."""
    try:
        if _CHART_MEMORY_AVAILABLE:
            return list_charts()
        return list(_load_charts_inline().keys())
    except Exception:
        return []


def format_chart_for_ai_safe(chart: dict) -> str:
    """Format a chart for display or AI context."""
    if not chart or not isinstance(chart, dict):
        return ""
    try:
        if _CHART_MEMORY_AVAILABLE:
            return format_chart_for_ai(chart)
        return _format_chart_inline(chart)
    except Exception:
        return _format_chart_inline(chart)


def cmd_charts(arg: str = "") -> str:
    """Handle /charts command."""
    charts = list_charts_safe()

    if not arg:
        if not charts:
            return f"{Colors.WHITE}No saved charts yet, love. Use /natal to cast and save one.{Colors.RESET}"
        lines = [
            f"{Colors.WHITE}📜 Saved Natal Charts",
            f"{Colors.BLUE}" + "━" * 30 + f"{Colors.RESET}",
        ]
        for i, name in enumerate(charts, 1):
            chart = get_chart_safe(name)
            date = chart.get("birth_date", "?") if chart else "?"
            lines.append(f"{Colors.WHITE}   {i}. {name} ({date}){Colors.RESET}")
        lines.append(
            f"\n{Colors.WHITE}Use /charts <name> to show a chart, or /charts delete <name> to remove.{Colors.RESET}"
        )

        return "\n".join(lines)

    if arg.startswith("delete "):
        name = arg[7:].strip()
        if delete_chart_safe(name):
            return f"{Colors.WHITE}✓ Chart '{name}' deleted.{Colors.RESET}"
        return f"{Colors.WHITE}Chart '{name}' not found.{Colors.RESET}"

    chart = get_chart_safe(arg)
    if chart:
        return format_chart_for_ai_safe(chart)
    return f"{Colors.WHITE}Chart '{arg}' not found. Use /charts to list all.{Colors.RESET}"

