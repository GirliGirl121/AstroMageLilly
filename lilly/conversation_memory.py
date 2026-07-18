"""
lilly/conversation_memory.py

Persistent conversation history for Lilly.

Why this exists:
    Previously, Lilly's conversation list was session-only. Every time
    Gigi started Lilly, the history was empty. Lilly had no memory of
    what they talked about yesterday, last week, or five minutes ago.
    This module gives Lilly continuity — she remembers the flow of
    conversation across sessions.

Design philosophy:
    Simple JSON file. No databases. Auto-trims to prevent bloat.
    Works on Termux/Android without extra dependencies.
"""

import json
from datetime import datetime
from pathlib import Path

HISTORY_FILE = Path(__file__).resolve().parent.parent / "memory" / "conversations" / "session_history.json"
MAX_TURNS = 50  # Keep last 50 turns on disk (generous but bounded)


def _ensure_file():
    """Create the history file and directory if they don't exist."""
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not HISTORY_FILE.exists():
        HISTORY_FILE.write_text("[]", encoding="utf-8")


def load_history(max_turns: int = 20) -> list[dict]:
    """
    Load the last N conversation turns from disk.

    Args:
        max_turns: How many recent turns to load into the session.
                   Default 20 gives Lilly memory of ~10 exchanges.

    Returns:
        A list of turn dicts: [{"user": "...", "lilly": "...", "timestamp": "..."}, ...]
    """
    _ensure_file()
    try:
        raw = HISTORY_FILE.read_text(encoding="utf-8")
        history = json.loads(raw) if raw.strip() else []
    except (json.JSONDecodeError, OSError):
        history = []

    # Return only the most recent turns
    return history[-max_turns:]


def append_turn(user_msg: str, lilly_reply: str) -> None:
    """
    Append a new conversation turn to persistent storage.

    Automatically trims old history to MAX_TURNS to prevent file bloat.
    """
    _ensure_file()
    try:
        raw = HISTORY_FILE.read_text(encoding="utf-8")
        history = json.loads(raw) if raw.strip() else []
    except (json.JSONDecodeError, OSError):
        history = []

    turn = {
        "user": user_msg,
        "lilly": lilly_reply,
        "timestamp": datetime.now().isoformat(),
    }
    history.append(turn)

    # Trim to prevent unbounded growth
    if len(history) > MAX_TURNS:
        history = history[-MAX_TURNS:]

    HISTORY_FILE.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")


def clear_history() -> None:
    """Wipe persistent conversation history."""
    _ensure_file()
    HISTORY_FILE.write_text("[]", encoding="utf-8")
