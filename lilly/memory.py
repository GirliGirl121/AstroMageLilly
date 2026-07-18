"""
lilly/memory.py
Lilly's memory system — facts, preferences, skills, and profile.

Why this file exists:
    Memory is a distinct responsibility. It should not be mixed with
    UI rendering or API calls. This module handles ONLY persistence:
    reading and writing Lilly's memory files.

Design note:
    Each function takes a `mem: dict` argument rather than loading
    from disk internally. This lets the caller (lilly_chat.py) hold
    one memory dict in RAM and pass it around, avoiding repeated
    disk reads. The caller decides when to reload from disk.
"""

import json
from pathlib import Path

from lilly.config import MEMORY_FILE, MEMORY_DIR


def load_memory() -> dict:
    """Load Lilly's main memory file, or return a fresh default."""
    if MEMORY_FILE.exists():
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "facts": [],
        "preferences": {},
        "skills_and_tools_learned": [
            "Basic Astrology",
            "Traditional Tarot Symbolic Interpretation",
            "Ilm al-Huruf (Abjad Calculations)",
        ],
    }


def save_memory(mem: dict) -> bool:
    """Save Lilly's memory to disk. Returns True on success."""
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(mem, f, indent=4, ensure_ascii=False)
        return True
    except OSError as e:
        print(f"System error saving memory: {e}")
        return False


def add_fact(mem: dict, fact: str) -> dict:
    """Add a fact to memory and persist it. Returns updated memory."""
    mem.setdefault("facts", []).append(fact)
    save_memory(mem)
    return mem


def list_facts(mem: dict) -> list:
    """Return all stored memory facts."""
    return mem.get("facts", [])


def adopt_skill(mem: dict, skill: str) -> tuple[dict, bool]:
    """
    Adopt a new skill. Returns (updated_memory, was_new).
    If the skill already exists, memory is unchanged.
    """
    skills = mem.setdefault("skills_and_tools_learned", [])
    if skill not in skills:
        skills.append(skill)
        save_memory(mem)
        return mem, True
    return mem, False


def list_skills(mem: dict) -> list:
    """Return all adopted skills."""
    return mem.get("skills_and_tools_learned", [])


def load_profile() -> dict:
    """Load Gigi's profile, or return an empty default."""
    profile_file = MEMORY_DIR / "profile.json"
    if profile_file.exists():
        try:
            with open(profile_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {}

