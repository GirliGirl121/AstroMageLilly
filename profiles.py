#!/usr/bin/env python3
# profiles.py — Natal Profile Vault

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from config import DATA_DIR
from rich.console import Console

console = Console()

PROFILES_FILE = DATA_DIR / "profiles.json"


class ProfileVault:
    """Store, retrieve, and manage natal chart profiles."""

    def __init__(self):
        self.profiles: Dict[str, Dict] = {}
        self._load()

    def _load(self):
        if PROFILES_FILE.exists():
            with open(PROFILES_FILE, 'r', encoding='utf-8') as f:
                self.profiles = json.load(f)
        else:
            self.profiles = {}

    def _save(self):
        with open(PROFILES_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.profiles, f, indent=2, ensure_ascii=False)

    def add(self, name: str, date: str, time: str, lat: float, lon: float,
            tz_offset: float, location: str = "", notes: str = "") -> Dict:
        """Add or update a profile."""
        self.profiles[name] = {
            "name": name,
            "date": date,
            "time": time,
            "lat": lat,
            "lon": lon,
            "timezone_offset": tz_offset,
            "location": location,
            "notes": notes,
            "created_at": datetime.now().isoformat(),
        }
        self._save()
        return self.profiles[name]

    def get(self, name: str) -> Optional[Dict]:
        return self.profiles.get(name)

    def delete(self, name: str) -> bool:
        if name in self.profiles:
            del self.profiles[name]
            self._save()
            return True
        return False

    def list(self) -> List[str]:
        return list(self.profiles.keys())

    def to_chart_data(self, name: str) -> Optional[Dict]:
        """Convert a profile to engine-ready chart data."""
        p = self.get(name)
        if not p:
            return None
        return dict(p)

    def display_all(self):
        if not self.profiles:
            console.print("[dim]The vault is empty. No souls recorded yet.[/dim]")
            return
        for name, p in self.profiles.items():
            console.print(f"[bold {COLORS['gold']}]{name}[/] — {p['date']} {p['time']} — {p['location']}")


from config import COLORS
vault = ProfileVault()

