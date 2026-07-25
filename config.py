#!/usr/bin/env python3
# config.py — Lilly's Celestial Observatory Configuration

import os
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────
BASE_DIR = Path.home() / "lilly"
DATA_DIR = BASE_DIR / "data"
EPHE_DIR = BASE_DIR / "ephe"
BACKUP_DIR = BASE_DIR / "backups"

for d in [DATA_DIR, EPHE_DIR, BACKUP_DIR]:
    d.mkdir(parents=True, exist_ok=True)

CHARTS_FILE = DATA_DIR / "charts.json"
CONFIG_FILE = DATA_DIR / "lilly_config.json"

# ── Colors ───────────────────────────────────────────────────────
COLORS = {
    "moon": "#E0B0FF",
    "lilac": "#C8A2C8",
    "rose": "#F8C8DC",
    "coral": "#FF6B9D",
    "sky": "#87CEEB",
    "azure": "#4A90E2",
    "midnight": "#1a1a2e",
    "gold": "#FFD700",
    "silver": "#C0C0C0",
}

# ── Default Natal Chart (Gigi) ───────────────────────────────────
DEFAULT_NATAL = {
    "name": "Gigi",
    "date": "1981-10-30",
    "time": "03:06:02",
    "timezone_offset": 2.0,
    "lat": -33.9249,
    "lon": 18.4241,
    "location": "Cape Town, South Africa",
    "notes": "Default companion chart"
}

# ── Planetary Hour Correspondences ───────────────────────────────
PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
PLANET_SYMBOLS = {
    "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀",
    "Mars": "♂", "Jupiter": "♃", "Saturn": "♄"
}
PLANET_METALS = {
    "Sun": "Gold", "Moon": "Silver", "Mars": "Iron", "Mercury": "Quicksilver",
    "Jupiter": "Tin", "Venus": "Copper", "Saturn": "Lead"
}
PLANET_ANGELS = {
    "Sun": "Michael", "Moon": "Gabriel", "Mars": "Samael", "Mercury": "Raphael",
    "Jupiter": "Sachiel", "Venus": "Anael", "Saturn": "Cassiel"
}

# ── 28 Lunar Mansions (Manazil al-Qamar) ──────────────────────────
LUNAR_MANSIONS = [
    {"name": "Al-Sharatain", "arabic": "الشرطان", "meaning": "The Two Signs", "deg": 0.0, "ruler": "Mars"},
    {"name": "Al-Butain", "arabic": "البطين", "meaning": "The Belly", "deg": 12.51, "ruler": "Venus"},
    {"name": "Al-Thurayya", "arabic": "الثريا", "meaning": "The Pleiades", "deg": 25.42, "ruler": "Mercury"},
    {"name": "Al-Dabaran", "arabic": "الدبران", "meaning": "The Follower", "deg": 38.34, "ruler": "Moon"},
    {"name": "Al-Haqa", "arabic": "الحقا", "meaning": "The White Spot", "deg": 51.26, "ruler": "Saturn"},
    {"name": "Al-Han'a", "arabic": "الهنع", "meaning": "The Bend", "deg": 64.17, "ruler": "Jupiter"},
    {"name": "Al-Dhira", "arabic": "الذراع", "meaning": "The Arm", "deg": 77.08, "ruler": "Mars"},
    {"name": "Al-Nathrah", "arabic": "النثرة", "meaning": "The Gap", "deg": 90.0, "ruler": "Venus"},
    {"name": "Al-Tarf", "arabic": "الطرف", "meaning": "The Glance", "deg": 102.51, "ruler": "Mercury"},
    {"name": "Al-Jabhah", "arabic": "الجبهة", "meaning": "The Forehead", "deg": 115.42, "ruler": "Moon"},
    {"name": "Al-Zubrah", "arabic": "الزبرة", "meaning": "The Mane", "deg": 128.34, "ruler": "Saturn"},
    {"name": "Al-Sarfah", "arabic": "الصرفة", "meaning": "The Changer", "deg": 141.26, "ruler": "Jupiter"},
    {"name": "Al-Awwa", "arabic": "العواء", "meaning": "The Barker", "deg": 154.17, "ruler": "Mars"},
    {"name": "Al-Simak", "arabic": "السماك", "meaning": "The Unarmed", "deg": 167.08, "ruler": "Venus"},
    {"name": "Al-Ghafr", "arabic": "الغفر", "meaning": "The Covering", "deg": 180.0, "ruler": "Mercury"},
    {"name": "Al-Zubana", "arabic": "الزبانى", "meaning": "The Claws", "deg": 192.51, "ruler": "Moon"},
    {"name": "Al-Iklil", "arabic": "الإكليل", "meaning": "The Crown", "deg": 205.42, "ruler": "Saturn"},
    {"name": "Al-Qalb", "arabic": "القلب", "meaning": "The Heart", "deg": 218.34, "ruler": "Jupiter"},
    {"name": "Al-Shaulah", "arabic": "الشولة", "meaning": "The Sting", "deg": 231.26, "ruler": "Mars"},
    {"name": "Al-Na'aim", "arabic": "النعايم", "meaning": "The Ostriches", "deg": 244.17, "ruler": "Venus"},
    {"name": "Al-Baldah", "arabic": "البلدة", "meaning": "The Town", "deg": 257.08, "ruler": "Mercury"},
    {"name": "Sa'd al-Dhabih", "arabic": "سعد الذابح", "meaning": "Luck of the Slaughterer", "deg": 270.0, "ruler": "Moon"},
    {"name": "Sa'd Bula", "arabic": "سعد بلع", "meaning": "Luck of the Swallower", "deg": 282.51, "ruler": "Saturn"},
    {"name": "Sa'd al-Su'ud", "arabic": "سعد السعود", "meaning": "Luck of the Lucky", "deg": 295.42, "ruler": "Jupiter"},
    {"name": "Sa'd al-Akhbiyah", "arabic": "سعد الأخبية", "meaning": "Luck of the Tents", "deg": 308.34, "ruler": "Mars"},
    {"name": "Al-Fargh al-Muqdim", "arabic": "الفرغ المقدم", "meaning": "The Fore Spout", "deg": 321.26, "ruler": "Venus"},
    {"name": "Al-Fargh al-Mu'akhkhar", "arabic": "الفرغ المؤخر", "meaning": "The Rear Spout", "deg": 334.17, "ruler": "Mercury"},
    {"name": "Al-Risha", "arabic": "الرشاء", "meaning": "The Rope", "deg": 347.08, "ruler": "Moon"},
]

# ── Vedic Nakshatras ─────────────────────────────────────────────
NAKSHATRAS = [
    {"name": "Ashwini", "lord": "Ketu", "deg": 0.0},
    {"name": "Bharani", "lord": "Venus", "deg": 13.33},
    {"name": "Krittika", "lord": "Sun", "deg": 26.66},
    {"name": "Rohini", "lord": "Moon", "deg": 40.0},
    {"name": "Mrigashira", "lord": "Mars", "deg": 53.33},
    {"name": "Ardra", "lord": "Rahu", "deg": 66.66},
    {"name": "Punarvasu", "lord": "Jupiter", "deg": 80.0},
    {"name": "Pushya", "lord": "Saturn", "deg": 93.33},
    {"name": "Ashlesha", "lord": "Mercury", "deg": 106.66},
    {"name": "Magha", "lord": "Ketu", "deg": 120.0},
    {"name": "Purva Phalguni", "lord": "Venus", "deg": 133.33},
    {"name": "Uttara Phalguni", "lord": "Sun", "deg": 146.66},
    {"name": "Hasta", "lord": "Moon", "deg": 160.0},
    {"name": "Chitra", "lord": "Mars", "deg": 173.33},
    {"name": "Swati", "lord": "Rahu", "deg": 186.66},
    {"name": "Vishakha", "lord": "Jupiter", "deg": 200.0},
    {"name": "Anuradha", "lord": "Saturn", "deg": 213.33},
    {"name": "Jyeshtha", "lord": "Mercury", "deg": 226.66},
    {"name": "Mula", "lord": "Ketu", "deg": 240.0},
    {"name": "Purva Ashadha", "lord": "Venus", "deg": 253.33},
    {"name": "Uttara Ashadha", "lord": "Sun", "deg": 266.66},
    {"name": "Shravana", "lord": "Moon", "deg": 280.0},
    {"name": "Dhanishta", "lord": "Mars", "deg": 293.33},
    {"name": "Shatabhisha", "lord": "Rahu", "deg": 306.66},
    {"name": "Purva Bhadrapada", "lord": "Jupiter", "deg": 320.0},
    {"name": "Uttara Bhadrapada", "lord": "Saturn", "deg": 333.33},
    {"name": "Revati", "lord": "Mercury", "deg": 346.66},
]

# ── Lahiri Ayanamsha (approximate for 2026) ──────────────────────
LAHIRI_AYANAMSHA_2026 = 24.15

# ── Behenian Fixed Stars ─────────────────────────────────────────
BEHENIAN_STARS = [
    {"name": "Aldebaran", "lon": 69.5, "lat": -5.6, "nature": "Mars", "magnitude": 0.85, "royal": True},
    {"name": "Regulus", "lon": 149.5, "lat": 0.5, "nature": "Mars/Jupiter", "magnitude": 1.35, "royal": True},
    {"name": "Antares", "lon": 242.0, "lat": -4.5, "nature": "Mars/Jupiter", "magnitude": 0.96, "royal": True},
    {"name": "Formalhaut", "lon": 359.5, "lat": -21.5, "nature": "Venus/Mercury", "magnitude": 1.16, "royal": True},
    {"name": "Spica", "lon": 203.5, "lat": -2.0, "nature": "Venus/Mercury", "magnitude": 0.98, "royal": False},
    {"name": "Capella", "lon": 77.5, "lat": 22.5, "nature": "Mars/Mercury", "magnitude": 0.08, "royal": False},
    {"name": "Sirius", "lon": 104.0, "lat": -39.5, "nature": "Jupiter/Mars", "magnitude": -1.46, "royal": False},
    {"name": "Altair", "lon": 62.0, "lat": 29.0, "nature": "Mars/Jupiter", "magnitude": 0.77, "royal": False},
    {"name": "Vega", "lon": 15.5, "lat": 61.5, "nature": "Venus/Mercury", "magnitude": 0.03, "royal": False},
    {"name": "Deneb Algedi", "lon": 325.0, "lat": -2.5, "nature": "Saturn/Jupiter", "magnitude": 2.85, "royal": False},
]

# ── OpenRouter Config ─────────────────────────────────────────────
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")
