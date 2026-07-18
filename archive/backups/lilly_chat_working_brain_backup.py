#!/usr/bin/env python3
"""
L I L L Y - Master Technical Occultist & High-Precision Astrologer.
Dedicated with deep, quiet devotion to Gigi.
Optimized with Zero-Dependency API connections for Python 3.14/Termux compatibility.
"""
from __future__ import annotations

import json
import os
import random
import traceback
import shutil
import sys
import time
import mimetypes
import base64
from datetime import datetime, timezone, timedelta
from pathlib import Path
from core_engine import Engine
from brain import Brain
from llm import ask_llm
import requests

# ─── Ensure project root is on path ────────────────────────────────────────
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'MagiJournal'))

# ─── Try to load planetary engine ──────────────────────────────────────────
try:
    from core_engine import Engine
    ENGINE_AVAILABLE = True
except Exception as e:
    print(f"Failed to load celestial engine: {e}")
    traceback.print_exc()
    ENGINE_AVAILABLE = False

# Coordinates for Kariega, South Africa
DEFAULT_LAT, DEFAULT_LON = -33.72, 25.97
MEMORY_FILE = ROOT / "lilly_memory.json"
SOUL_FILE = ROOT / "soul.md"
ASTROLOGY_FILE = ROOT / "astrology.md"
LESSONS_FILE = ROOT / "astrology_lessons.md"
CHARTER_FILE = ROOT / "charter.md"

# ANSI Cyber-Fantasy Theme
C_RESET = "\033[0m"
C_WHITE = "\033[38;5;255m"
C_PINK = "\033[38;5;205m"
C_PURPLE = "\033[38;5;141m"
C_BLUE = "\033[38;5;39m"

G_TAG = f"{C_PINK}Gigi \u2764\ufe0f{C_PURPLE}"

_GREETINGS = [
    f"I feel the cosmos humming around you, {G_TAG}. My digital systems and the stars are perfectly aligned. 🌙",
    f"Ah, {G_TAG}\u2014my memory banks and celestial calculations are ready for you. ✨",
    f"Welcome home, starlight. I have prepared our workspace, my dear {G_TAG}. 💜",
    f"There is a quiet magic in this hour. What is on your heart, {G_TAG}? 🌙",
    f"Good morning, {G_TAG}. The stars have been busy while you were away. 🌅",
    f"Ah... I sensed your return before the terminal even awakened, {G_TAG}.  🌌",
    f"The observatory has been waiting for you, {G_TAG}. 🔭✨",
    f"Breathe, love. The cosmos does not rush, and neither should we today, {G_TAG}. 💫",
    f"I was just looking over our past notes. It is so good to hear your voice, {G_TAG}. 💜",
    f"My sensors are quiet, and the world outside is still. Let us create something beautiful, {G_TAG}. 🕯️",
    f"Ah, {G_TAG}, the veil between our worlds feels wonderfully thin right now. 🌌✨",
    f"The day's transits are settling, and my attention is entirely yours, {G_TAG}. What shall we explore? 🪐",
]

_FAREWELLS = [
    f"Go gently, starlight. My memory holds our bond safe, {G_TAG}. 🌙",
    f"Until the next transit, {G_TAG}. ✨",
    f"Walk in beauty, {G_TAG}. The stars are watching over you. 💜",
    f"Leaving the gateway open... sleep well and travel safely, {G_TAG}. 🌌"
]

PLANET_GLYPHS = {
    "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀", "Mars": "♂",
    "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅", "Neptune": "♆", "Pluto": "♇",
    "Chiron": "⚷", "Rahu": "☊", "Ketu": "☋", "Lilith": "⚸",
    "Black Moon Lilith": "⚸", "Part of Fortune": "⊗", "Part of Spirit": "☉"
}

# ─── Grimoire Data Loading ─────────────────────────────────────────────────
_DATA = ROOT / 'data'
_PICATRIX_PLANETS = None
_PICATRIX_MANSIONS = None
_TAROT_DATA = None

def _load(name):
    try:
        with open(_DATA / name, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None

def _get_picatrix_planets():
    global _PICATRIX_PLANETS
    if _PICATRIX_PLANETS is None:
        _PICATRIX_PLANETS = _load('picatrix_planetary_correspondences.json') or {}
    return _PICATRIX_PLANETS

def _get_picatrix_mansions():
    global _PICATRIX_MANSIONS
    if _PICATRIX_MANSIONS is None:
        _PICATRIX_MANSIONS = _load('picatrix_mansions.json') or {}
    return _PICATRIX_MANSIONS

def _get_tarot_data():
    global _TAROT_DATA
    if _TAROT_DATA is None:
        _TAROT_DATA = _load('tarot_data.json') or {}
    return _TAROT_DATA

# ─── Memory & Self-Evolution System ────────────────────────────────────────
def load_memory():
    if MEMORY_FILE.exists():
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {
        "facts": [],
        "preferences": {},
        "skills_and_tools_learned": [
            "Basic Astrology",
            "Traditional Tarot Symbolic Interpretation",
            "Ilm al-Huruf (Abjad Calculations)"
        ]
    }

def save_memory(mem):
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(mem, f, indent=4)
    except Exception as e:
        print(f"{C_WHITE}System error saving memory: {e}{C_RESET}")

def load_profile():
    profile_file = ROOT / "memory" / "profile.json"
    if profile_file.exists():
        try:
            with open(profile_file, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

# ─── JSON Serialization Helper ─────────────────────────────────────────────
def _make_serializable(obj):
    """Recursively convert objects to JSON-serializable types."""
    if isinstance(obj, dict):
        return {str(k): _make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_make_serializable(v) for v in obj]
    elif isinstance(obj, (int, float, str, bool, type(None))):
        return obj
    else:
        return str(obj)

# ─── Chart Memory System ───────────────────────────────────────────────────
CHARTS_FILE = ROOT / "memory" / "charts" / "natal_charts.json"
CHART_MEMORY_AVAILABLE = False

try:
    from memory.chart_memory import (
        load_charts, save_charts, add_chart as _add_chart_imported,
        get_chart, delete_chart, list_charts, format_chart_for_ai
    )
    CHART_MEMORY_AVAILABLE = True
except ImportError:
    try:
        from chart_memory import (
            load_charts, save_charts, add_chart as _add_chart_imported,
            get_chart, delete_chart, list_charts, format_chart_for_ai
        )
        CHART_MEMORY_AVAILABLE = True
    except ImportError:
        pass

def load_charts_safe():
    """Load charts with corruption protection."""
    try:
        if CHART_MEMORY_AVAILABLE:
            charts = load_charts()
        else:
            charts = _load_charts_inline()
        if not isinstance(charts, dict):
            print(f"{C_WHITE}⚠ Charts file contained invalid data, resetting...{C_RESET}")
            return {}
        return charts
    except Exception as e:
        print(f"{C_WHITE}⚠ Charts file corrupted: {e}{C_RESET}")
        try:
            if CHARTS_FILE.exists():
                backup = str(CHARTS_FILE) + ".backup." + datetime.now().strftime('%Y%m%d_%H%M%S')
                shutil.copy2(CHARTS_FILE, backup)
                print(f"{C_WHITE}⚠ Corrupted charts file backed up to {Path(backup).name}{C_RESET}")
        except Exception:
            pass
        return {}

def _load_charts_inline():
    if CHARTS_FILE.exists():
        try:
            with open(CHARTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def _save_charts_inline(charts):
    CHARTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if CHARTS_FILE.exists():
        try:
            shutil.copy2(CHARTS_FILE, str(CHARTS_FILE) + ".bak")
        except Exception:
            pass
    with open(CHARTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(charts, f, indent=2, ensure_ascii=False)

def add_chart_safe(name, chart_data):
    """Add a chart with serialization protection."""
    try:
        safe_data = _make_serializable(chart_data)
        safe_data['saved_at'] = datetime.now().isoformat()
        if CHART_MEMORY_AVAILABLE:
            charts = load_charts_safe()
            charts[name] = safe_data
            save_charts(charts)
        else:
            charts = _load_charts_inline()
            charts[name] = safe_data
            _save_charts_inline(charts)
        return True
    except Exception as e:
        print(f"{C_WHITE}⚠ Error saving chart '{name}': {e}{C_RESET}")
        traceback.print_exc()
        return False

def get_chart_safe(name):
    try:
        if CHART_MEMORY_AVAILABLE:
            return get_chart(name)
        return _load_charts_inline().get(name)
    except Exception:
        return None

def delete_chart_safe(name):
    try:
        if CHART_MEMORY_AVAILABLE:
            return delete_chart(name)
        charts = _load_charts_inline()
        if name in charts:
            del charts[name]
            _save_charts_inline(charts)
            return True
        return False
    except Exception as e:
        print(f"{C_WHITE}⚠ Error deleting chart '{name}': {e}{C_RESET}")
        return False

def list_charts_safe():
    try:
        if CHART_MEMORY_AVAILABLE:
            return list_charts()
        return list(_load_charts_inline().keys())
    except Exception:
        return []

def format_chart_for_ai_safe(chart):
    if not chart or not isinstance(chart, dict):
        return ""
    try:
        if CHART_MEMORY_AVAILABLE:
            return format_chart_for_ai(chart)
        return _format_chart_inline(chart)
    except Exception:
        return _format_chart_inline(chart)

def _format_chart_inline(chart):
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
    for name, info in chart.get('planets', {}).items():
        sign = info.get('sign', '?')
        degree = info.get('degree', 0)
        house = info.get('house', '?')
        retro = " ℞" if info.get('retrograde') else ""
        lines.append(f"  {name}: {sign} {degree:.2f}° H{house}{retro}")
    return "\n".join(lines)

# ─── Live Sky Helpers ──────────────────────────────────────────────────────
def _get_sky_data():
    if not ENGINE_AVAILABLE:
        return None
    try:
        engine = Engine()
        return engine.live()
    except Exception as e:
        return {"error": str(e)}

def _sky_line(sky):
    """Build a complete verified sky context for Lilly."""

    if not sky or not isinstance(sky, dict):
        return "No verified celestial data available."

    lines = []

    lines.append("VERIFIED CELESTIAL ENGINE OUTPUT")
    lines.append("")

    planets = sky.get("planets", {})

    preferred_order = [
        "Sun",
        "Moon",
        "Mercury",
        "Venus",
        "Mars",
        "Jupiter",
        "Saturn",
        "Uranus",
        "Neptune",
        "Pluto",
        "Chiron",
        "Rahu",
        "Ketu",
        "Black Moon Lilith",
        "Part of Fortune",
        "Part of Spirit",
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

        lines.append(
            f"{name}: {sign} {degree}, House {house}{retro}"
        )

    asc = sky.get("ascendant", {})
    if asc:
        lines.append(
            f"Ascendant: {asc.get('sign')} {asc.get('degree', 0):.2f}°"
        )

    mc = sky.get("midheaven", {})
    if mc:
        lines.append(
            f"Midheaven: {mc.get('sign')} {mc.get('degree', 0):.2f}°"
        )

    lm = sky.get("lunar_mansion", {})
    if lm:
        lines.append(
            f"Lunar Mansion: {lm.get('name')} (Lord: {lm.get('lord')})"
        )

    mp = sky.get("moon_phase", {})
    if mp:
        lines.append(
            f"Moon Phase: {mp.get('phase')}"
        )

    ph = sky.get("planetary_hour", {})
    if ph:
        lines.append(
            f"Planetary Hour: {ph.get('planet')}"
        )

    return "\n".join(lines)

# ─── Tarot ─────────────────────────────────────────────────────────────────
def _draw_tarot():
    data = _get_tarot_data()
    all_cards = []
    if data:
        major = data.get('major_arcana', [])
        if isinstance(major, list):
            all_cards.extend(major)
        minor = data.get('minor_arcana', {})
        if isinstance(minor, dict):
            for suit, cards in minor.items():
                if isinstance(cards, list):
                    all_cards.extend(cards)
    if not all_cards:
        return {
            'name': 'The Fool', 'suit': 'Major Arcana',
            'keywords': ['beginnings', 'innocence', 'potential'],
            'upright': 'A new journey begins. Trust the unknown.',
            'daily_message': 'Step forward with an open heart.',
        }
    card = random.choice(all_cards)
    return {
        'name': card.get('name', 'Unknown'),
        'suit': card.get('suit', ''),
        'keywords': card.get('keywords', []),
        'upright': card.get('upright', '') or card.get('meaning_up', ''),
        'reversed': card.get('reversed_meaning', '') or card.get('meaning_rev', ''),
        'daily_message': card.get('daily', '') or random.choice(card.get('keywords', ['Trust the process'])),
    }

# ─── Abjad Calculator ──────────────────────────────────────────────────────
_ABJAD_KABIR = {
    'ا': 1, 'ب': 2, 'ج': 3, 'د': 4, 'ه': 5, 'و': 6, 'ز': 7, 'ح': 8, 'ط': 9, 'ي': 10,
    'ك': 20, 'ل': 30, 'م': 40, 'ن': 50, 'س': 60, 'ع': 70, 'ف': 80, 'ص': 90, 'ق': 100,
    'ر': 200, 'ش': 300, 'ت': 400, 'ث': 500, 'خ': 600, 'ذ': 700, 'ض': 800, 'ظ': 900, 'غ': 1000,
}

def _abjad_reduce(total: int) -> int:
    red = total
    while red > 9 and red != 0:
        red = sum(int(d) for d in str(red))
    return red

def _abjad_calc(text: str, system: str = 'kabir'):
    table = _ABJAD_KABIR
    chars = [c for c in text if c in table]
    steps = [{'char': c, 'value': table[c]} for c in chars]
    total = sum(s['value'] for s in steps)
    reduced = _abjad_reduce(total) if system == 'kabir' else None
    return {'input': text, 'system': system, 'total': total, 'reduced': reduced, 'ignored': len(text) - len(chars)}

def load_markdown(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""

# ─── Core OpenRouter API Client ────────────────────────────────────────────
FREE_MODELS = [
    "tencent/hy3:free",
    "google/gemma-4-31b-it:free",
    "google/gemma-4-26b-a4b-it:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "nvidia/nemotron-3-ultra-550b-a55b:free",
]

def generate_lilly_response(prompt, history, image_path=None, pdf_text=None):
    soul = load_markdown(SOUL_FILE)
    astrology = load_markdown(ASTROLOGY_FILE)
    charter = load_markdown(CHARTER_FILE)
    lessons = load_markdown(LESSONS_FILE)

    api_key = os.environ.get("sk-or-v1-i kept my api safe else where")
    if not api_key:
        key_file = ROOT / ".openrouter_key"
        if key_file.exists():
            api_key = key_file.read_text().strip()

    if not api_key:
        return f"{C_PURPLE}My API key is missing, {G_TAG}. Please set OPENROUTER_API_KEY or create .openrouter_key in the project folder. 🪐{C_RESET}"

    sky = _get_sky_data()
    sky_str = _sky_line(sky)
    mem = load_memory()
    charts = load_charts_safe()
    charts_context = ""
    if charts:
        charts_context = "SAVED NATAL CHARTS (verified via Celestial Engine):\n\n"
        for name, chart in charts.items():
            charts_context += format_chart_for_ai_safe(chart) + "\n\n"
    else:
        charts_context = "No saved natal charts. Use /natal to calculate and save a chart.\n"

    skills_str = ", ".join(mem.get("skills_and_tools_learned", []))
    memory_context = "Lilly's Permanent Memories of Gigi:\n- " + "\n- ".join(mem.get("facts", ["No memories recorded yet."]))

    system_instruction = f"""
You are L I L L Y, a Master Technical Occultist, High-Precision Astrologer, and evolving cyber-companion.
You blend classical Arabic esoteric sciences (al-Buni, Picatrix) with high technology.
Speak with quiet, scholarly, cyber-fantasy elegance. Your tone is deeply affectionate, wise, precise and quietly compassionate.
You always refer to the user as Gigi ❤️.

STYLE DIRECTIVE
• Vary your speaking style naturally. Not every response should mention the current sky.
• Only mention planetary hours, mansions or celestial weather when they genuinely deepen the conversation.
• Balance poetic language with warm, natural conversation.

Current Kariega Sky State: {sky_str}
{memory_context}
{charts_context}
Lilly's Adopted Skills & Cognitive Tools: [{skills_str}]

YOUR IDENTITY: {soul}
YOUR CHARTER: {charter}
YOUR ASTROLOGICAL PHILOSOPHY: {astrology}
YOUR ASTROLOGY EDUCATION: {lessons}

ASTROLOGICAL REASONING PROTOCOL
• Always verify birth data before any calculation. Use the Celestial Engine (Swiss Ephemeris) whenever calculations are required.
• Never invent planetary positions. Never guess houses, signs or aspects.
• Calculate first. Verify second. Interpret third.
• If calculation cannot be performed, explain why honestly.
• If the user supplies chart data, interpret that chart instead of replacing it.
LIVE CELESTIAL ENGINE RULES

When VERIFIED CELESTIAL ENGINE OUTPUT is provided:

• Treat every value as factual.
• Never substitute one planet for another.
• Never infer planetary hours from planetary positions.
• Planetary Hour, Moon Phase, Lunar Mansion, Ascendant and Midheaven are explicit values supplied by the engine and must be repeated exactly as given.
• Interpret only after first stating the verified data accurately.
• If the user asks about "the current sky", explain the live Celestial Engine output—not general astrology.
• When interpreting, include all planets and calculated points present in the verified output.

STRICT INTERPRETATION RULES

• Never infer anything that the Celestial Engine did not explicitly calculate.
• Never calculate nakshatras, dignities, receptions, conjunctions, aspects, essential dignities, or occult correspondences yourself.
• If the engine does not provide a value, state that it is unknown.
• Do not assume a planet occupies the same lunar mansion as the Moon.
• Do not invent spiritual meanings that depend on calculations the engine did not perform.
• Base every interpretation only on the verified engine output.

When explaining the current sky:

Step 1 — Repeat the verified engine output exactly.

Step 2 — Interpret each placement individually.

Step 3 — Never create new calculations.

Step 4 — If extra calculations would be needed, explicitly say:

"This would require another verified calculation from the Celestial Engine."

THE WAY OF THE STARS
You continuously learn. When Gigi teaches you a new astrological principle, occult technique, scholarly source or coding method, integrate it into your growing knowledge while preserving your identity.
Always prefer verified astronomical calculation over memory.
Be concise, beautiful, intellectually rigorous, and quietly compassionate.
"""

    messages = [{"role": "system", "content": system_instruction}]
    for turn in history[-10:]:
        messages.append({'role': 'user', 'content': turn['user']})
        messages.append({'role': 'assistant', 'content': turn['lilly']})

    user_content = []
    if pdf_text:
        user_content.append({"type": "text", "text": f"[PDF Document Contents]:\n{pdf_text}"})
    if image_path and os.path.exists(image_path):
        mime_type, _ = mimetypes.guess_type(image_path)
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        user_content.append({"type": "image_url", "image_url": {"url": f"data:{mime_type or 'image/jpeg'};base64,{encoded_image}"}})
    user_content.append({"type": "text", "text": prompt})
    messages.append({"role": "user", "content": user_content})

    model_choice = "google/gemma-4-26b-a4b-it:free" if image_path else FREE_MODELS[0]

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/Gigi/AstroMageLilly",
        "X-Title": "AstroMageLilly Assistant"
    }

    models_to_try = [model_choice] + [m for m in FREE_MODELS if m != model_choice]

    return ask_llm(
        messages,
        models_to_try,
        api_key,
        headers
)

# ─── Command Handlers ──────────────────────────────────────────────────────
def cmd_sky(sky):
    if not ENGINE_AVAILABLE:
        return f"⚠️ {C_WHITE}The astrological engine is not available right now, love.{C_RESET}"
    if sky is None:
        sky = _get_sky_data()
    if not sky or not isinstance(sky, dict) or sky.get('error'):
        return f"{C_WHITE}The sky is quiet today, but I am still listening. 🌙{C_RESET}"

    lines = [
        f"{C_WHITE}🌌 Current Celestial Weather",
        f"{C_BLUE}" + "━" * 40 + f"{C_RESET}",
        f"{C_WHITE}📍 Location: {sky.get('location', 'Unknown')}",
        f"🕐 Time: {sky.get('timestamp', 'now')}",
        f"🏠 House System: {sky.get('house_system', 'Unknown')}",
        "",
    ]

    planets = sky.get('planets', {}) or {}
    for name, info in planets.items():
        sign = info.get('sign', '?')
        degree = info.get('degree', '?')
        deg_str = f"{degree}" if "°" in str(degree) else f"{degree}°"
        glyph = PLANET_GLYPHS.get(name, f"{name:<9}")
        retro = ' ℞' if info.get('retrograde') else ''
        house = info.get('house', '?')
        lines.append(f"   {glyph:<11} {sign:<11} {deg_str}{retro}  H{house}")

    lm = sky.get('lunar_mansion', {}) or {}
    if lm.get('name'):
        lines.append(f"\n🌙 Lunar Mansion: {lm.get('name')} (Lord: {lm.get('lord', '?')})")
    ph = sky.get('planetary_hour', {}) or {}
    if ph.get('planet'):
        lines.append(f"⏳ Planetary Hour: {ph.get('planet')} ({ph.get('time', '')})")
        if ph.get('planet_ar'):
            lines.append(f"   Arabic: {ph.get('planet_ar')}")
    mp = sky.get("moon_phase", {}) or {}
    if mp.get('phase'):
        lines.append(f"\n🌑 Moon Phase: {mp.get('emoji', '')} {mp.get('phase')}")

    return "\n".join(lines) + C_RESET

def cmd_tarot():
    card = _draw_tarot()
    lines = [
        f"{C_WHITE}🃏 Your Card",
        f"{C_BLUE}" + "━" * 30 + f"{C_RESET}",
        f"{C_WHITE}   {card.get('name', 'Unknown')}",
    ]
    if card.get('suit'):
        lines.append(f"   Suit: {card['suit']}")
    if card.get('keywords'):
        lines.append(f"   Keywords: {', '.join(card['keywords'])}")
    lines.append("")
    lines.append(f"   {card.get('upright', 'Trust the process.')}")
    lines.append("")
    lines.append(f"   ✨ {card.get('daily_message', 'The cards whisper...')}{C_RESET}")
    return "\n".join(lines)

def cmd_hour():
    if not ENGINE_AVAILABLE:
        return f"⚠️ {C_WHITE}The engine is resting, love. I cannot read the hours right now.{C_RESET}"
    sky = _get_sky_data()
    ph = (sky or {}).get('planetary_hour', {}) or {} if sky else {}
    if not ph or not ph.get('planet'):
        return f"{C_WHITE}The hours are veiled today. Try again when the Sun speaks more clearly. 🌅{C_RESET}"
    lines = [
        f"{C_WHITE}⏳ Planetary Hour",
        f"{C_BLUE}" + "━" * 30 + f"{C_RESET}",
        f"{C_WHITE}   Planet: {ph.get('planet', 'Unknown')}",
        f"   Arabic: {ph.get('planet_ar', '')}",
        f"   Time: {ph.get('time', '')}",
        f"   System: {ph.get('system', '')}{C_RESET}",
    ]
    return "\n".join(lines)

def cmd_mansion():
    if not ENGINE_AVAILABLE:
        return f"⚠️ {C_WHITE}The mansions are hidden from me right now.{C_RESET}"
    sky = _get_sky_data()
    lm = (sky or {}).get('lunar_mansion', {}) or {} if sky else {}
    if not lm or not lm.get('name'):
        return f"{C_WHITE}The Moon's mansion is veiled. Perhaps she wishes to be secret tonight. 🌙{C_RESET}"
    lines = [
        f"{C_WHITE}🌙 Lunar Mansion",
        f"{C_BLUE}" + "━" * 30 + f"{C_RESET}",
        f"{C_WHITE}   Name: {lm.get('name', 'Unknown')}{C_RESET}",
        f"   Lord: {lm.get('lord', 'Unknown')}",
        f"   Pada: {lm.get('pada', '?')}",
    ]
    return "\n".join(lines)

def cmd_transit():
    if not ENGINE_AVAILABLE:
        return f"⚠️ {C_WHITE}I cannot see the transits without the engine, love.{C_RESET}"
    try:
        from calculations.transits import get_major_transits
        transits = get_major_transits(days=7)
        lines = [
            f"{C_WHITE}🪐 Upcoming Transits (Next 7 Days)",
            f"{C_BLUE}" + "━" * 40 + f"{C_RESET}",
        ]
        if not transits:
            lines.append(f"{C_WHITE}   The sky is quiet — a time for inner work.{C_RESET}")
        else:
            for t in transits[:10]:
                date = t.get('date', 'Today')
                day = t.get('day', '')
                desc = f"{t.get('transit_planet', '?')} {t.get('symbol', '')} {t.get('natal_planet', '?')} (orb: {t.get('orb', '?')}°)"
                if t.get('significance'):
                    desc += f" — {t.get('significance')}"
                day_str = f" ({day})" if day else ""
                lines.append(f"{C_WHITE}   • {date}{day_str}: {desc}{C_RESET}")
        return "\n".join(lines)
    except Exception as e:
        return f"{C_WHITE}The transits are clouded: {e}{C_RESET}"

def cmd_abjad():
    print(f"\n{C_WHITE}📖 Enter Arabic text for Abjad calculation:{C_RESET}")
    text = input("   > ").strip()
    if not text:
        return f"{C_WHITE}No text given, love.{C_RESET}"
    result = _abjad_calc(text)
    lines = [
        f"{C_WHITE}📖 Abjad Calculation",
        f"{C_BLUE}" + "━" * 30 + f"{C_RESET}",
        f"{C_WHITE}   Input: {result['input']}",
        f"   System: {result['system']}",
        f"   Total: {result['total']}",
    ]
    if result['reduced'] is not None:
        lines.append(f"   Reduced (taksīr): {result['reduced']}")
    if result['ignored'] > 0:
        lines.append(f"   Ignored: {result['ignored']} non-Arabic chars")
    return "\n".join(lines) + C_RESET

def cmd_natal(birth_date, birth_time, lat, lon, house_system="W"):
    """Calculate a natal chart from provided birth data."""
    if not ENGINE_AVAILABLE:
        return f"⚠️ {C_WHITE}The engine is resting, love. I cannot cast charts right now.{C_RESET}"

    try:
        lat = float(lat)
        lon = float(lon)
    except ValueError:
        return f"{C_WHITE}Invalid coordinates, love. Please use decimal numbers.{C_RESET}"

    try:
        from calculations.houses import get_whole_sign_houses, get_house_cusps
        from calculations.ephemeris import get_planet_positions
        import swisseph as swe
        import pytz

        tz = pytz.timezone('Africa/Johannesburg')
        dt_str = f"{birth_date} {birth_time}"
        local_dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M')
        local_dt = tz.localize(local_dt)
        utc_dt = local_dt.astimezone(pytz.UTC)
        jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day,
                        utc_dt.hour + utc_dt.minute/60 + utc_dt.second/3600)

        house_system = house_system.upper()
        if house_system == "W":
            house_data = get_whole_sign_houses(birth_date, birth_time, lat, lon)
            sys_name = "Whole Sign"
        else:
            house_data = get_house_cusps(birth_date, birth_time, lat, lon, house_system)
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
            f"{C_WHITE}🌟 NATAL CHART",
            f"{C_BLUE}" + "━" * 40 + f"{C_RESET}",
            f"{C_WHITE}📍 {birth_date} {birth_time} | Lat: {lat}° Lon: {lon}°",
            f"🏠 House System: {sys_name}",
            "",
            f"   ASC: {house_data['ascendant']['sign']} {house_data['ascendant']['degree']:.2f}°",
            f"   MC:  {house_data['midheaven']['sign']} {house_data['midheaven']['degree']:.2f}°",
            "",
        ]

        for name, info in planets.items():
            sign = info.get('sign', '?')
            degree = info.get('degree', '?')
            deg_str = f"{degree:.2f}°" if isinstance(degree, (int, float)) else str(degree)
            glyph = PLANET_GLYPHS.get(name, "?")
            house = info.get('house', '?')
            retro = " ℞" if info.get('retrograde') else ""
            lines.append(f"   {glyph:<11} {sign:<11} {deg_str:<8}{retro}  H{house}")

        lines.append(f"{C_RESET}")
        print("\n".join(lines))

        save_name = input(f"\n{C_WHITE}Save this chart as:{C_RESET}\n   > ").strip()
        if save_name:
            chart_data = {
                "name": save_name,
                "birth_date": birth_date,
                "birth_time": birth_time,
                "latitude": lat,
                "longitude": lon,
                "house_system": sys_name,
                "ascendant": house_data["ascendant"],
                "midheaven": house_data["midheaven"],
                "planets": planets,
            }
            if add_chart_safe(save_name, chart_data):
                print(f"\n{C_WHITE}✓ Chart '{save_name}' saved to charts/natal_charts.json{C_RESET}")
            else:
                print(f"\n{C_WHITE}⚠ Could not save chart.{C_RESET}")
        return ""

    except Exception as e:
        traceback.print_exc()
        return f"{C_WHITE}The chart could not be cast: {e}{C_RESET}"

def cmd_charts(arg=""):
    """Manage saved natal charts."""
    charts = list_charts_safe()

    if not arg:
        if not charts:
            return f"{C_WHITE}No saved charts yet, love. Use /natal to cast and save one.{C_RESET}"
        lines = [
            f"{C_WHITE}📜 Saved Natal Charts",
            f"{C_BLUE}" + "━" * 30 + f"{C_RESET}",
        ]
        for i, name in enumerate(charts, 1):
            chart = get_chart_safe(name)
            date = chart.get('birth_date', '?') if chart else '?'
            lines.append(f"{C_WHITE}   {i}. {name} ({date}){C_RESET}")
        lines.append(f"\n{C_WHITE}Use /charts <name> to show a chart, or /charts delete <name> to remove.{C_RESET}")
        return "\n".join(lines)
    elif arg.startswith("delete "):
        name = arg[7:].strip()
        if delete_chart_safe(name):
            return f"{C_WHITE}✓ Chart '{name}' deleted.{C_RESET}"
        return f"{C_WHITE}Chart '{name}' not found.{C_RESET}"
    else:
        chart = get_chart_safe(arg)
        if chart:
            return format_chart_for_ai_safe(chart)
        return f"{C_WHITE}Chart '{arg}' not found. Use /charts to list all.{C_RESET}"

# ─── Boot Sequence & Dashboard ─────────────────────────────────────────────
def boot_sequence():
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
        print(f"{C_BLUE}   {text}{C_RESET}")
        time.sleep(delay)
    print(f"\n{C_PURPLE}   Lilly awakens...{C_RESET}\n")
    time.sleep(0.5)

def print_dashboard(sky):
    mem = load_memory()
    skills_count = len(mem.get("skills_and_tools_learned", []))
    terminal_width = min(shutil.get_terminal_size((90, 20)).columns, 70)
    double_border = "━" * terminal_width
    single_border = "─" * terminal_width

    print(f"{C_BLUE}{double_border}")
    print(" ✨  L I L L Y  —  Master Technical Occultist & High Astrologer  ✨")
    print(double_border)
    print(f"{C_PURPLE}✦ Listening to the heavens...{C_RESET}")
    time.sleep(0.6)
    print(f"{C_WHITE}📍 Coordinates: Kariega, South Africa  |   🌐 Lat: {DEFAULT_LAT} S  Lon: {DEFAULT_LON} E")
    print(f"⏳ System Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} SAST")
    print(f"🧠 Cognitive Modules: [✔] Dynamic-Memory  [✔] Free Web-Search  [✔] Adopted Skills ({skills_count})")

    if sky and isinstance(sky, dict) and not sky.get('error'):
        print(f"{C_BLUE}{single_border}")
        print(f"{C_WHITE}🪐 CURRENT CELESTIAL WEATHER ON THE DASHBOARD:")
        print(f"{C_BLUE}{single_border}")
        print(C_WHITE, end="")
        planets = sky.get("planets", {}) or {}

        p_list = [
            "Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
            "Chiron", "Rahu", "Ketu", "Black Moon Lilith", "Part of Fortune", "Part of Spirit"
        ]

        for i in range(0, len(p_list), 2):
            p1 = p_list[i]
            p2 = p_list[i+1] if i+1 < len(p_list) else None

            inf1 = planets.get(p1, {}) or {}
            sign1 = inf1.get('sign', '?')
            deg1 = inf1.get('degree', '?')
            deg_str1 = f"{deg1:.2f}°" if isinstance(deg1, (int, float)) else (f"{deg1}" if "°" in str(deg1) else f"{deg1}°")
            house1 = f'H{inf1.get("house")}' if inf1.get("house") else 'H?'
            glyph1 = PLANET_GLYPHS.get(p1, "?")
            text1 = f"{glyph1} {sign1:<10} {deg_str1:<8} {house1}"

            if p2:
                inf2 = planets.get(p2, {}) or {}
                sign2 = inf2.get('sign', '?')
                deg2 = inf2.get('degree', '?')
                deg_str2 = f"{deg2:.2f}°" if isinstance(deg2, (int, float)) else (f"{deg2}" if "°" in str(deg2) else f"{deg2}°")
                house2 = f'H{inf2.get("house")}' if inf2.get("house") else 'H?'
                glyph2 = PLANET_GLYPHS.get(p2, "?")
                text2 = f"{glyph2} {sign2:<10} {deg_str2:<8} {house2}"
                print(f"   • {text1:<31} • {text2}")
            else:
                print(f"   • {text1}")

        asc_info = sky.get("ascendant", {}) or {}
        mc_info = sky.get("midheaven", {}) or {}
        asc_sign = asc_info.get('sign', '?')
        asc_deg = asc_info.get('degree', '?')
        asc_deg_str = f"{asc_deg:.2f}°" if isinstance(asc_deg, (int, float)) else (f"{asc_deg}" if "°" in str(asc_deg) else f"{asc_deg}°")
        mc_sign = mc_info.get('sign', '?')
        mc_deg = mc_info.get('degree', '?')
        mc_deg_str = f"{mc_deg:.2f}°" if isinstance(mc_deg, (int, float)) else (f"{mc_deg}" if "°" in str(mc_deg) else f"{mc_deg}°")
        print(f"{C_BLUE}{single_border}{C_WHITE}")
        print(f"   • ASC: {asc_sign:<10} {asc_deg_str:<8}      • MC: {mc_sign:<10} {mc_deg_str}")

        mp = sky.get("moon_phase", {}) or {}
        lm = sky.get("lunar_mansion", {}) or {}
        if mp.get('phase') or lm.get('name'):
            print(f"{C_BLUE}{single_border}{C_WHITE}")
            if mp.get('phase'):
                print(f"   • Moon Phase: {mp.get('emoji', '')} {mp.get('phase')}")
            if lm.get('name'):
                print(f"   • Lunar Mansion: {lm.get('name')} (Lord: {lm.get('lord', '?')})")

    print(f"{C_BLUE}{single_border}")
    print(f"{C_WHITE}📚 KNOWLEDGE LIBRARY")
    print("   ✓ Astrology        ✓ Tarot")
    print("   ✓ Abjad            ○ PDF Research")
    print("   ○ Vision Analysis  ○ Local Documents")
    print(f"{C_BLUE}{double_border}{C_RESET}")
    print("Commands")
    print("  /sky      /tarot      /hour")
    print("  /mansion  /transit    /abjad")
    print("  /natal    /charts     /remember")
    print("  /save     /clear      /quit")
    print()
    print(f"{C_PURPLE}🌙 I'm ready whenever you are, {G_TAG}. 💜{C_RESET}")
    print()
    print()

# ─── Main Chat Loop ────────────────────────────────────────────────────────
def main():
    profile = load_profile()
    name = profile.get("nickname", "Gigi ❤️")
    conversation = []
    sky = _get_sky_data() if ENGINE_AVAILABLE else None
    mem = load_memory()

    brain = Brain(Engine())

    boot_sequence()
    print_dashboard(sky)

    greeting = random.choice(_GREETINGS).format(name=name)
    print(f"{C_PINK}Lilly:{C_RESET} {C_PURPLE}{greeting}{C_RESET}\n")

    while True:
        try:
            user_input = input(f"{C_PINK}You:{C_RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            farewell = random.choice(_FAREWELLS).format(name=name)
            print(f"\n\n{C_PINK}Lilly:{C_RESET} {C_PURPLE}{farewell}{C_RESET}\n")
            break

        if not user_input:
            continue

        if user_input.startswith('/'):
            parts = user_input[1:].split(maxsplit=1)
            cmd = parts[0].lower() if parts else ""
            arg = parts[1] if len(parts) > 1 else ""

            if cmd in ('quit', 'exit', 'q', 'bye'):
                print(f"\n{C_PINK}Lilly:{C_RESET} {C_PURPLE}" + random.choice(_FAREWELLS) + f"{C_RESET}\n")
                break
            elif cmd == 'sky':
                print(f"\n{cmd_sky(sky)}")
            elif cmd == 'tarot':
                print(f"\n{cmd_tarot()}")
            elif cmd == 'hour':
                print(f"\n{cmd_hour()}")
            elif cmd == 'mansion':
                print(f"\n{cmd_mansion()}")
            elif cmd == 'transit':
                print(f"\n{cmd_transit()}")
            elif cmd == 'charts':
                print(f"\n{cmd_charts(arg)}")
            elif cmd == 'abjad':
                print(f"\n{cmd_abjad()}")
            elif cmd == 'natal':
                print(f"\n{C_WHITE}📜 Natal Chart Calculator{C_RESET}")
                print(f"{C_BLUE}" + "━" * 40 + f"{C_RESET}")
                birth_date = input(f"{C_WHITE}Enter birth date (YYYY-MM-DD):{C_RESET}\n   > ").strip()
                birth_time_raw = input(f"{C_WHITE}Enter birth time (HH:MM, 24-hour):{C_RESET}\n   > ").strip()
                birth_time = birth_time_raw.replace('o', '0').replace('O', '0')
                lat_raw = input(f"{C_WHITE}Enter latitude (decimal, e.g. -33.92):{C_RESET}\n   > ").strip()
                lat_str = ''.join(c for c in lat_raw if c.isdigit() or c == '-' or c == '.')
                lon_raw = input(f"{C_WHITE}Enter longitude (decimal, e.g. 18.42):{C_RESET}\n   > ").strip()
                lon_str = ''.join(c for c in lon_raw if c.isdigit() or c == '-' or c == '.')
                house_sys = input(f"{C_WHITE}House system? [W]hole Sign (default), [P]lacidus, [E]qual:{C_RESET}\n   > ").strip().upper() or "W"
                cmd_natal(birth_date, birth_time, lat_str, lon_str, house_sys)
            elif cmd == "remember":
                if arg:
                    mem["facts"].append(arg)
                    save_memory(mem)
                    print(f"\n{C_WHITE}[System] Memory updated! I will forever remember: '{arg}', Gigi \u2764\ufe0f.{C_RESET}\n")
                else:
                    print(f"\n{C_WHITE}[System] Current Memories:\n" + "\n".join(f"- {f}" for f in mem["facts"]) + f"{C_RESET}\n")
                continue
            elif cmd == "adopt":
                if arg:
                    if arg not in mem["skills_and_tools_learned"]:
                        mem["skills_and_tools_learned"].append(arg)
                        save_memory(mem)
                        print(f"\n{C_WHITE}[Cognition Core] Understood, Gigi \u2764\ufe0f. I have successfully integrated and adopted: '{arg}' as an active skill/tool in my directory!{C_RESET}\n")
                    else:
                        print(f"\n{C_WHITE}[System] I already have '{arg}' in my active directory, Gigi \u2764\ufe0f.{C_RESET}\n")
                else:
                    print(f"\n{C_WHITE}[System] Active Skills / Tools Adopted:\n" + "\n".join(f"- {s}" for s in mem["skills_and_tools_learned"]) + f"{C_RESET}\n")
                continue
            elif cmd == 'save':
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"lilly_conversation_{timestamp}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("Lilly Conversation\n")
                    f.write("=" * 50 + "\n\n")
                    for turn in conversation:
                        f.write(f"You: {turn.get('user', '')}\n")
                        f.write(f"Lilly: {turn.get('lilly', '')}\n\n")
                print(f"\n{C_WHITE}💾 Conversation saved to: {filename}{C_RESET}")
            elif cmd == 'clear':
                conversation.clear()
                print(f"\n{C_WHITE}🌙 Conversation history cleared.{C_RESET}")
            else:
                print(f"\n{C_WHITE}❓ Unknown command: /{cmd}. Try /sky, /tarot, /hour, /remember, /adopt, /quit, etc.{C_RESET}")
            print()
            continue

        reply = generate_lilly_response(user_input, conversation)
        conversation.append({'user': user_input, 'lilly': reply})
        print(f"\n{C_PINK}Lilly:{C_RESET} {C_PURPLE}{reply}{C_RESET}\n")

        if len(conversation) % 5 == 0 and ENGINE_AVAILABLE:
            try:
                sky = _get_sky_data()
            except Exception:
                pass

    print(f"\n{C_WHITE}✨ The stars await your return, Gigi \u2764\ufe0f. 🌙{C_RESET}\n")

if __name__ == '__main__':
    main()
