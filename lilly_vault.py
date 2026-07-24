"""
The Esoteric Vault — Persistent astrological database.
"""
import json
from datetime import datetime
from typing import Dict, List, Optional

from lilly_config import VAULT_PATH


class EsotericVault:
    def __init__(self):
        self.vault_path = VAULT_PATH
        self.data = self._load()

    def _load(self) -> Dict:
        if self.vault_path.exists():
            try:
                with open(self.vault_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print("⚠️  Vault corrupted. Starting fresh.")
        return {
            "profiles": {},
            "charts": [],
            "synastry_pairs": [],
            "metadata": {
                "created": datetime.now().isoformat(),
                "version": "1.0",
                "keeper": "Lilly"
            }
        }

    def _save(self):
        with open(self.vault_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def add_profile(self, name: str, birth_date: str, birth_time: str,
                    latitude: float, longitude: float, timezone_offset: float = 0.0,
                    notes: str = "") -> str:
        profile_id = f"profile_{len(self.data['profiles']) + 1}"
        self.data["profiles"][profile_id] = {
            "id": profile_id,
            "name": name,
            "birth_date": birth_date,
            "birth_time": birth_time,
            "latitude": latitude,
            "longitude": longitude,
            "timezone_offset": timezone_offset,
            "notes": notes,
            "created": datetime.now().isoformat(),
            "charts_computed": []
        }
        self._save()
        return profile_id

    def get_profile(self, profile_id: str) -> Optional[Dict]:
        return self.data["profiles"].get(profile_id)

    def list_profiles(self) -> List[Dict]:
        return list(self.data["profiles"].values())

    def find_profile_by_name(self, name: str) -> Optional[Dict]:
        for pid, profile in self.data["profiles"].items():
            if profile["name"].lower() == name.lower():
                return profile
        return None

    def save_chart(self, profile_id: str, chart_data: Dict, chart_type: str = "natal") -> str:
        chart_id = f"chart_{len(self.data['charts']) + 1}"
        entry = {
            "id": chart_id,
            "profile_id": profile_id,
            "chart_type": chart_type,
            "computed_at": datetime.now().isoformat(),
            "data": chart_data
        }
        self.data["charts"].append(entry)
        if profile_id in self.data["profiles"]:
            self.data["profiles"][profile_id]["charts_computed"].append(chart_id)
        self._save()
        return chart_id

    def get_chart(self, chart_id: str) -> Optional[Dict]:
        for chart in self.data["charts"]:
            if chart["id"] == chart_id:
                return chart
        return None

    def add_journal_entry(self, title: str, content: str, tags: List[str] = None):
        if "journal" not in self.data:
            self.data["journal"] = []
        entry = {
            "id": f"entry_{len(self.data['journal']) + 1}",
            "title": title,
            "content": content,
            "tags": tags or [],
            "created": datetime.now().isoformat()
        }
        self.data["journal"].append(entry)
        self._save()
        return entry["id"]

    def get_journal_entries(self, tag: str = None) -> List[Dict]:
        entries = self.data.get("journal", [])
        if tag:
            entries = [e for e in entries if tag in e.get("tags", [])]
        return entries

    def vault_summary(self) -> str:
        profiles = len(self.data["profiles"])
        charts = len(self.data["charts"])
        entries = len(self.data.get("journal", []))
        return f"""The vault holds {profiles} soul{'s' if profiles != 1 else ''} within its walls,
{charts} celestial map{'s' if charts != 1 else ''} drawn across the ages,
and {entries} whispered secret{'s' if entries != 1 else ''} inscribed in starlight."""
