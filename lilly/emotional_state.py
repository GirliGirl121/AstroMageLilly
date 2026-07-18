"""
lilly/emotional_state.py

Tracks Gigi's emotional patterns across sessions.
Why this exists:
    Lilly detects emotional distress in single messages, but she forgets
    the pattern. Three sad sessions in a week should inform her presence
    on the fourth. This module gives her emotional memory — not just
    fact memory, but heart memory.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

STATE_FILE = Path(__file__).resolve().parent.parent / "memory" / "emotional_state.json"
MAX_ENTRIES = 20  # Rolling window — last 20 emotional events


def _ensure_file():
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not STATE_FILE.exists():
        STATE_FILE.write_text("[]", encoding="utf-8")


def record_emotional_state(tone: str = "distress") -> None:
    """Record an emotional event with timestamp."""
    _ensure_file()
    try:
        history = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        history = []

    history.append({
        "timestamp": datetime.now().isoformat(),
        "tone": tone,
    })

    # Trim to prevent unbounded growth
    if len(history) > MAX_ENTRIES:
        history = history[-MAX_ENTRIES:]

    STATE_FILE.write_text(
        json.dumps(history, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def get_emotional_summary() -> str:
    """
    Generate a brief summary of recent emotional state for Lilly's awareness.
    Returns empty string if no relevant pattern, so the prompt stays clean.
    """
    _ensure_file()
    try:
        history = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return ""

    if not history:
        return ""

    # Only look at last 7 days
    cutoff = datetime.now() - timedelta(days=7)
    recent = [
        h for h in history
        if datetime.fromisoformat(h["timestamp"]) > cutoff
    ]

    if not recent:
        return ""

    distress_count = sum(1 for h in recent if h["tone"] == "distress")
    total = len(recent)

    # Thresholds tuned for warmth without creepiness
    if distress_count >= 3:
        return "Gigi has been carrying a heavy heart lately. Be extra gentle, warm, and present. Do not overwhelm her with astrology or advice unless she asks."
    elif distress_count >= 1:
        return "Gigi has had some difficult moments recently. Offer quiet support and listen more than you speak."
    else:
        return ""  # Neutral — no need to mention


def clear_emotional_state() -> None:
    """Wipe emotional history. Called by /clear."""
    _ensure_file()
    STATE_FILE.write_text("[]", encoding="utf-8")
