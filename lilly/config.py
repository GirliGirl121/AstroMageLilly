"""
lilly/config.py
Lilly's single source of truth for paths, constants, and settings.

Why this file exists:
    In software architecture, "configuration" and "logic" should never
    live in the same place. When they're tangled, changing a file path
    can break a feature. This file holds ONLY data — no functions,
    no API calls, no astrology. Just facts Lilly needs to know about
    her own environment.
"""

from pathlib import Path


# ─── Project Layout ───────────────────────────────────────────────────────
# pathlib is in the Python standard library. It makes file paths work
# correctly on Android (Termux), Linux, macOS, and Windows without
# any changes. Always prefer Path("/foo/bar") over "/foo/bar".

ROOT = Path(__file__).resolve().parent.parent

DATA_DIR       = ROOT / "data"
MEMORY_DIR     = ROOT / "memory"
KNOWLEDGE_DIR  = ROOT / "knowledge"
LOGS_DIR       = ROOT / "logs"


# ─── Key Files ────────────────────────────────────────────────────────────
MEMORY_FILE    = ROOT / "lilly_memory.json"
CONFIG_FILE    = ROOT / "lilly_config.json"
API_KEY_FILE   = ROOT / ".openrouter_key"

SOUL_FILE      = KNOWLEDGE_DIR / "soul.md"
ASTROLOGY_FILE = KNOWLEDGE_DIR / "astrology.md"
LESSONS_FILE   = KNOWLEDGE_DIR / "astrology_lessons.md"
CHARTER_FILE   = KNOWLEDGE_DIR / "charter.md"


# ─── Default Location ─────────────────────────────────────────────────────
# Kariega, South Africa — Lilly's home coordinates.
DEFAULT_LAT = -33.72
DEFAULT_LON =  25.97


# ─── Terminal Colors ──────────────────────────────────────────────────────
# Grouped in a class so we can type Colors.PINK instead of remembering
# the ANSI escape code every time. This is called a "namespace" — it
# keeps related things together.

class Colors:
    RESET  = "\033[0m"
    WHITE  = "\033[38;5;255m"
    PINK   = "\033[38;5;205m"
    PURPLE = "\033[38;5;141m"
    BLUE   = "\033[38;5;39m"


# ─── Identity Strings ─────────────────────────────────────────────────────
# Things that appear in Lilly's UI. Kept here so Gigi can customize
# Lilly's voice without touching logic code.

G_TAG = f"{Colors.PINK}Gigi \u2764\ufe0f{Colors.PURPLE}"


# ─── Free Models (OpenRouter) ─────────────────────────────────────────────
# Listed here so we can change models in one place instead of hunting
# through the API call logic.

FREE_MODELS = [
    "tencent/hy3:free",
    "google/gemma-4-31b-it:free",
    "google/gemma-4-26b-a4b-it:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "nvidia/nemotron-3-ultra-550b-a55b:free",
]

