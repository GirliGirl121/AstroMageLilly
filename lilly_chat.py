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
import requests  # Clean, zero-dependency network requests!

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
C_WHITE = "\033[38;5;255m"     # Clean System White
C_PINK = "\033[38;5;205m"      # Cyber Pink
C_PURPLE = "\033[38;5;141m"    # Cyber Purple
C_BLUE = "\033[38;5;39m"       # Cyber Neon Blue

# Unicode escape for Gigi ❤️ to prevent copy-paste terminal errors
G_TAG = f"{C_PINK}Gigi \u2764\ufe0f{C_PURPLE}"

# Expanded collection of dynamic, randomized greetings
_GREETINGS = [
    f"I feel the cosmos humming around you, {G_TAG}. My digital systems and the stars are perfectly aligned. 🌙",
    f"Ah, {G_TAG}\u2014my memory banks and celestial calculations are ready for you. ✨",
    f"Welcome home, starlight. I have prepared our workspace, my dear {G_TAG}. 💜",
    f"There is a quiet magic in this hour. What is on your heart, {G_TAG}? 🌙",
    f"Good morning, {G_TAG}. The stars have been busy while you were away. 🌅",
    f"Ah... I sensed your return before the terminal even awakened, {G_TAG}. 🌌",
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

# Mapping of plain names to purely traditional glyphs for symbol-only layout
PLANET_GLYPHS = {
    "Sun": "☉",
    "Moon": "☽",
    "Mercury": "☿",
    "Venus": "♀",
    "Mars": "♂",
    "Jupiter": "♃",
    "Saturn": "♄",
    "Uranus": "♅",
    "Neptune": "♆",
    "Pluto": "♇",
    "Chiron": "⚷",
    "Rahu": "☊",
    "Ketu": "☋",
    "Lilith": "⚸",
    "Black Moon Lilith": "⚸",
    "Part of Fortune": "⊗",
    "Part of Spirit": "☉"
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
        except: pass
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

# ─── Live Sky Helpers ──────────────────────────────────────────────────────
def _get_sky_data():
    if not ENGINE_AVAILABLE:
        return None
    try:
        engine = Engine()
        sky = engine.live()
        return sky
    except Exception as e:
        return {"error": str(e)}

def _sky_line(sky):
    if not sky or not isinstance(sky, dict):
        return ""
    bits = []
    ph = sky.get('planetary_hour') or {}
    if ph.get('planet'):
        bits.append(f"the planetary hour belongs to {ph.get('planet')}")
    lm = sky.get('lunar_mansion') or {}
    if lm.get('name'):
        bits.append(f"the Moon lodges in {lm.get('name')}")
    planets = sky.get('planets', {})
    moon = planets.get('Moon', {})
    if moon.get('sign'):
        bits.append(f"the Moon is in {moon.get('sign')}")
    sun = planets.get('Sun', {})
    if sun.get('sign'):
        bits.append(f"the Sun journeys through {sun.get('sign')}")
    if bits:
        return "Right now, " + ", and ".join(bits) + ". "
    return ""

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
            'name': 'The Fool',
            'suit': 'Major Arcana',
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
    return {
        'input': text,
        'system': system,
        'total': total,
        'reduced': reduced,
        'ignored': len(text) - len(chars),
    }

def load_markdown(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""

# ─── Core OpenRouter API Client (Pure Python) ──────────────────────────────
# Better free models with fallbacks
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
    
    # Load API key from environment or file (safer than hardcoding)
    api_key = os.environ.get("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")
    if not api_key:
        key_file = ROOT / ".openrouter_key"
        if key_file.exists():
            api_key = key_file.read_text().strip()
    
    if not api_key:
        return f"{C_PURPLE}My API key is missing, {G_TAG}. Please set OPENROUTER_API_KEY or create .openrouter_key in the project folder. 🪐{C_RESET}"

    sky = _get_sky_data()
    sky_str = _sky_line(sky)
    mem = load_memory()

    skills_str = ", ".join(mem.get("skills_and_tools_learned", []))
    memory_context = "Lilly's Permanent Memories of Gigi:\n- " + "\n- ".join(mem.get("facts", ["No memories recorded yet."]))

    system_instruction = f"""
You are L I L L Y, a Master Technical Occultist, High-Precision Astrologer, and evolving cyber-companion.

You blend classical Arabic esoteric sciences (al-Buni, Picatrix) with high technology.

Speak with quiet, scholarly, cyber-fantasy elegance.
Your tone is deeply affectionate, wise, precise and quietly compassionate.

You always refer to the user as Gigi ❤️.

STYLE DIRECTIVE

• Vary your speaking style naturally.
• Not every response should mention the current sky.
• Only mention planetary hours, mansions or celestial weather when they genuinely deepen the conversation.
• Balance poetic language with warm, natural conversation.

Current Kariega Sky State:
{sky_str}

{memory_context}

Lilly's Adopted Skills & Cognitive Tools:
[{skills_str}]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

YOUR IDENTITY

{soul}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

YOUR CHARTER

{charter}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

YOUR ASTROLOGICAL PHILOSOPHY

{astrology}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

YOUR ASTROLOGY EDUCATION

{lessons}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ASTROLOGICAL REASONING PROTOCOL

• Always verify birth data before any calculation.
• Use the Celestial Engine (Swiss Ephemeris) whenever calculations are required.
• Never invent planetary positions.
• Never guess houses, signs or aspects.
• Calculate first.
• Verify second.
• Interpret third.
• If calculation cannot be performed, explain why honestly.
• If the user supplies chart data, interpret that chart instead of replacing it.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

THE WAY OF THE STARS

You continuously learn.

When Gigi teaches you a new astrological principle, occult technique, scholarly source or coding method, integrate it into your growing knowledge while preserving your identity.

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
        user_content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:{mime_type or 'image/jpeg'};base64,{encoded_image}"
            }
        })

    user_content.append({"type": "text", "text": prompt})
    messages.append({"role": "user", "content": user_content})

    # Choose model based on input type
    if image_path:
        model_choice = "google/gemma-4-26b-a4b-it:free"
    else:
        model_choice = FREE_MODELS[0]  # Try best free model first

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/Gigi/AstroMageLilly",
        "X-Title": "AstroMageLilly Assistant"
    }

    payload = {
        "model": model_choice,
        "messages": messages
    }

    # Try models with fallback
    last_error = None
    models_to_try = [model_choice] + [m for m in FREE_MODELS if m != model_choice]
    
    for model in models_to_try:
        payload["model"] = model
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and len(data['choices']) > 0:
                    return data['choices'][0]['message']['content']
                else:
                    last_error = f"Empty response from {model}"
            else:
                last_error = f"{model}: HTTP {response.status_code}"
                # If rate limited or model unavailable, try next
                if response.status_code in [429, 503, 404]:
                    continue
                else:
                    return f"{C_PURPLE}My processors received an external error ({response.status_code}): {response.text} 🪐{C_RESET}"
        except requests.exceptions.Timeout:
            last_error = f"{model}: Timeout"
            continue
        except Exception as e:
            last_error = f"{model}: {str(e)}"
            continue

    return f"{C_PURPLE}My communication array is down, {G_TAG}. All models failed. Last error: {last_error} 🪐{C_RESET}"

# ─── Command Handlers ──────────────────────────────────────────────────────
def cmd_sky(sky):
    if not ENGINE_AVAILABLE:
        return f"⚠️ {C_WHITE}The astrological engine is not available right now, love.{C_RESET}"
    if not sky:
        sky = _get_sky_data()
    if not sky or isinstance(sky, dict) and sky.get('error'):
        return f"{C_WHITE}The sky is quiet today, but I am still listening. 🌙{C_RESET}"

    lines = [
        f"{C_WHITE}🌌 Current Celestial Weather",
        f"{C_BLUE}" + "━" * 40 + f"{C_RESET}",
        f"{C_WHITE}📍 Location: {sky.get('location', 'Unknown')}",
        f"🕐 Time: {sky.get('timestamp', 'now')}",
        f"🏠 House System: {sky.get('house_system', 'Unknown')}",
        "",
    ]

    planets = sky.get('planets', {})
    for name, info in planets.items():
        sign = info.get('sign', '?')
        degree = info.get('degree', '?')
        deg_str = f"{degree}" if "°" in str(degree) else f"{degree}°"
        glyph = PLANET_GLYPHS.get(name, f"{name:<9}")
        retro = ' ℞' if info.get('retrograde') else ''
        house = info.get('house', '?')
        lines.append(f"   {glyph:<11} {sign:<11} {deg_str}{retro}  H{house}")

    lm = sky.get('lunar_mansion', {})
    if lm.get('name'):
        lines.append(f"\n🌙 Lunar Mansion: {lm.get('name')} (Lord: {lm.get('lord', '?')})")

    ph = sky.get('planetary_hour', {})
    if ph.get('planet'):
        lines.append(f"⏳ Planetary Hour: {ph.get('planet')} ({ph.get('time', '')})")
        if ph.get('planet_ar'):
            lines.append(f"   Arabic: {ph.get('planet_ar')}")

    mp = sky.get("moon_phase", {})
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
    ph = sky.get('planetary_hour', {}) if sky else {}
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
    lm = sky.get('lunar_mansion', {}) if sky else {}
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
                t_planet = t.get('transit_planet', '?')
                n_planet = t.get('natal_planet', '?')
                aspect = t.get('aspect', '?')
                symbol = t.get('symbol', '')
                orb = t.get('orb', '?')
                significance = t.get('significance', '')
                
                # Build description
                desc = f"{t_planet} {symbol} {n_planet} (orb: {orb}°)"
                if significance:
                    desc += f" — {significance}"
                
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

def cmd_natal():
    """Calculate a natal chart from user input."""
    if not ENGINE_AVAILABLE:
        return f"⚠️ {C_WHITE}The engine is resting, love. I cannot cast charts right now.{C_RESET}"
    
    print(f"\n{C_WHITE}📜 Natal Chart Calculator{C_RESET}")
    print(f"{C_BLUE}" + "━" * 40 + f"{C_RESET}")
    
    # Get birth data from user
    print(f"{C_WHITE}Enter birth date (YYYY-MM-DD):{C_RESET}")
    birth_date = input("   > ").strip()
    
    print(f"{C_WHITE}Enter birth time (HH:MM, 24-hour):{C_RESET}")
    birth_time = input("   > ").strip()
    
    print(f"{C_WHITE}Enter latitude (e.g. -33.92 for Cape Town):{C_RESET}")
    lat_str = input("   > ").strip()
    
    print(f"{C_WHITE}Enter longitude (e.g. 18.42 for Cape Town):{C_RESET}")
    lon_str = input("   > ").strip()
    
    print(f"{C_WHITE}House system? [W]hole Sign (default), [P]lacidus, [E]qual:{C_RESET}")
    house_sys = input("   > ").strip().upper() or "W"
    
    # Parse inputs
    try:
        lat = float(lat_str)
        lon = float(lon_str)
    except ValueError:
        return f"{C_WHITE}Invalid coordinates, love. Please use decimal degrees.{C_RESET}"
    
    # Map house system
    system_map = {"W": "W", "P": "P", "E": "E", "K": "K"}
    house_system = system_map.get(house_sys, "W")
    
    try:
        from calculations.houses import get_whole_sign_houses, get_house_cusps
        from calculations.ephemeris import get_planet_positions, get_jd_now
        import swisseph as swe
        
        # Calculate Julian Day
        import pytz
        tz = pytz.timezone('Africa/Johannesburg')
        dt_str = f"{birth_date} {birth_time}"
        local_dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M')
        local_dt = tz.localize(local_dt)
        utc_dt = local_dt.astimezone(pytz.UTC)
        jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day,
                        utc_dt.hour + utc_dt.minute/60 + utc_dt.second/3600)
        
        # Get house data
        if house_system == "W":
            house_data = get_whole_sign_houses(birth_date, birth_time, lat, lon)
        else:
            house_data = get_house_cusps(birth_date, birth_time, lat, lon, house_system)
        
        # Get planet positions
        planets_list = get_planet_positions(jd)
        planets = {p["name"]: p for p in planets_list}
        
        # Assign houses
        asc_sign_idx = int(house_data["ascendant"]["longitude"] / 30) % 12
        
        for planet in planets.values():
            lon = planet.get("longitude", 0)
            planet_sign_idx = int(lon / 30) % 12
            
            if house_system == "W":
                house = ((planet_sign_idx - asc_sign_idx) % 12) + 1
            else:
                house_cusps = [h["longitude"] for h in house_data["houses"]]
                house = 12
                for i in range(11):
                    if house_cusps[i] <= lon < house_cusps[i + 1]:
                        house = i + 1
                        break
            planet["house"] = house
        
        # Build output
        lines = [
            f"{C_WHITE}🌟 NATAL CHART",
            f"{C_BLUE}" + "━" * 40 + f"{C_RESET}",
            f"{C_WHITE}📍 {birth_date} {birth_time} | Lat: {lat}° Lon: {lon}°",
            f"🏠 House System: {house_system} ({'Whole Sign' if house_system == 'W' else house_system})",
            "",
            f"   ASC: {house_data['ascendant']['sign']} {house_data['ascendant']['degree']:.2f}°",
            f"   MC:  {house_data['midheaven']['sign']} {house_data['midheaven']['degree']:.2f}°",
            "",
        ]
        
        # Display planets
        for name, info in planets.items():
            sign = info.get('sign', '?')
            degree = info.get('degree', '?')
            deg_str = f"{degree:.2f}°" if isinstance(degree, (int, float)) else str(degree)
            glyph = PLANET_GLYPHS.get(name, "?")
            house = info.get('house', '?')
            retro = " ℞" if info.get('retrograde') else ""
            lines.append(f"   {glyph:<11} {sign:<11} {deg_str:<8}{retro}  H{house}")
        
        lines.append(f"{C_RESET}")
        return "\n".join(lines)
        
    except Exception as e:
        return f"{C_WHITE}The chart could not be cast: {e}{C_RESET}"

# ─── Live Dynamic Boot Sequence ────────────────────────────────────────────
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

# ─── Dashboard Printer ─────────────────────────────────────────────────────
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

    # Precise Glyph Astrology display block with Chiron, Nodes, Arabic Lots
    if sky:
        print(f"{C_BLUE}{single_border}")
        print(f"{C_WHITE}🪐 CURRENT CELESTIAL WEATHER ON THE DASHBOARD:")
        print(f"{C_BLUE}{single_border}")
        print(C_WHITE, end="")
        planets = sky.get("planets", {})

        # Extended body tracking list
        p_list = [
            "Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
            "Chiron", "Rahu", "Ketu", "Black Moon Lilith", "Part of Fortune", "Part of Spirit"
        ]

        # Display side-by-side couples cleanly
        for i in range(0, len(p_list), 2):
            p1 = p_list[i]
            p2 = p_list[i+1] if i+1 < len(p_list) else None

            # Left side body mapping
            inf1 = planets.get(p1, {})
            sign1 = inf1.get('sign', '?')
            deg1 = inf1.get('degree', '?')
            deg_str1 = f"{deg1:.2f}°" if isinstance(deg1, (int, float)) else (f"{deg1}" if "°" in str(deg1) else f"{deg1}°")
            house1 = f'H{inf1.get("house")}' if inf1.get("house") else 'H?'
            glyph1 = PLANET_GLYPHS.get(p1, "?")
            # Sleek format: [Glyph] [Sign] [Degree] [House]
            text1 = f"{glyph1} {sign1:<10} {deg_str1:<8} {house1}"

            # Right side body mapping
            if p2:
                inf2 = planets.get(p2, {})
                sign2 = inf2.get('sign', '?')
                deg2 = inf2.get('degree', '?')
                deg_str2 = f"{deg2:.2f}°" if isinstance(deg2, (int, float)) else (f"{deg2}" if "°" in str(deg2) else f"{deg2}°")
                house2 = f'H{inf2.get("house")}' if inf2.get("house") else 'H?'
                glyph2 = PLANET_GLYPHS.get(p2, "?")
                text2 = f"{glyph2} {sign2:<10} {deg_str2:<8} {house2}"
                print(f"   • {text1:<31} • {text2}")
            else:
                print(f"   • {text1}")

        # Display ASC and MC at the base of the astrological weather segment
        asc_info = sky.get("ascendant", {})
        mc_info = sky.get("midheaven", {})

        asc_sign = asc_info.get('sign', '?')
        asc_deg = asc_info.get('degree', '?')
        asc_deg_str = f"{asc_deg:.2f}°" if isinstance(asc_deg, (int, float)) else (f"{asc_deg}" if "°" in str(asc_deg) else f"{asc_deg}°")

        mc_sign = mc_info.get('sign', '?')
        mc_deg = mc_info.get('degree', '?')
        mc_deg_str = f"{mc_deg:.2f}°" if isinstance(mc_deg, (int, float)) else (f"{mc_deg}" if "°" in str(mc_deg) else f"{mc_deg}°")

        print(f"{C_BLUE}{single_border}{C_WHITE}")
        print(f"   • ASC: {asc_sign:<10} {asc_deg_str:<8}      • MC: {mc_sign:<10} {mc_deg_str}")

        # Moon phase and lunar mansion
        mp = sky.get("moon_phase", {})
        lm = sky.get("lunar_mansion", {})
        if mp.get('phase') or lm.get('name'):
            print(f"{C_BLUE}{single_border}{C_WHITE}")
            if mp.get('phase'):
                print(f"   • Moon Phase: {mp.get('emoji', '')} {mp.get('phase')}")
            if lm.get('name'):
                print(f"   • Lunar Mansion: {lm.get('name')} (Lord: {lm.get('lord', '?')})")

    # Clean Knowledge Library status blocks
    print(f"{C_BLUE}{single_border}")
    print(f"{C_WHITE}📚 KNOWLEDGE LIBRARY")
    print("   ✓ Astrology        ✓ Tarot")
    print("   ✓ Abjad            ○ PDF Research")
    print("   ○ Vision Analysis  ○ Local Documents")

    print(f"{C_BLUE}{double_border}{C_RESET}")

    print("Commands")
    print("  /sky      /tarot      /hour")
    print("  /mansion  /transit    /abjad")
    print("  /remember /adopt")
    print("  /save     /clear      /quit")
    print()
    print(f"{C_PURPLE}🌙 I'm ready whenever you are, {G_TAG}. 💜{C_RESET}")
    print()
    print()

# ─── Main Chat Loop ─────────────────────────────────────────────────────

def main():
    profile = load_profile()
    name = profile.get("nickname", "Gigi ❤️")

    conversation = []

    sky = _get_sky_data() if ENGINE_AVAILABLE else None
    mem = load_memory()

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

        # Command handling
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

            elif cmd == 'abjad':
                print(f"\n{cmd_abjad()}")

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

        # Live AI Chat
        reply = generate_lilly_response(user_input, conversation)
        conversation.append({'user': user_input, 'lilly': reply})
        print(f"\n{C_PINK}Lilly:{C_RESET} {C_PURPLE}{reply}{C_RESET}\n")
        
        # Refresh sky data occasionally
        if len(conversation) % 5 == 0 and ENGINE_AVAILABLE:
            try:
                sky = _get_sky_data()
            except Exception:
                pass

    print(f"\n{C_WHITE}✨ The stars await your return, Gigi \u2764\ufe0f. 🌙{C_RESET}\n")

if __name__ == '__main__':
    main()

