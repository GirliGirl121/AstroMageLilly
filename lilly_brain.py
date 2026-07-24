"""
The Unified Brain — Conversational memory and context persistence.
"""
import json
from datetime import datetime
from typing import Dict, List, Optional

from lilly_config import BRAIN_PATH


class UnifiedBrain:
    def __init__(self, max_history: int = 50):
        self.brain_path = BRAIN_PATH
        self.max_history = max_history
        self.data = self._load()

    def _load(self) -> Dict:
        if self.brain_path.exists():
            try:
                with open(self.brain_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print("⚠️  Brain memory fragmented. Rebuilding...")
        return {
            "conversations": [],
            "projects": {},
            "facts": {},
            "preferences": {
                "user_name": "Gigi",
                "astrology_system": "dual",
                "location": None
            },
            "metadata": {
                "first_meeting": datetime.now().isoformat(),
                "total_messages": 0
            }
        }

    def _save(self):
        with open(self.brain_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def remember_conversation(self, role: str, content: str,
                               context: str = "general", metadata: Dict = None):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "content": content,
            "context": context,
            "metadata": metadata or {}
        }
        self.data["conversations"].append(entry)
        self.data["metadata"]["total_messages"] += 1
        if len(self.data["conversations"]) > self.max_history:
            self.data["conversations"] = self.data["conversations"][-self.max_history:]
        self._save()

    def get_recent_context(self, n: int = 10, context_filter: str = None) -> List[Dict]:
        convos = self.data["conversations"]
        if context_filter:
            convos = [c for c in convos if c["context"] == context_filter]
        return convos[-n:]

    def get_formatted_history(self, n: int = 10) -> List[Dict]:
        recent = self.get_recent_context(n)
        formatted = []
        for entry in recent:
            role = "user" if entry["role"] == "user" else "assistant"
            formatted.append({"role": role, "content": entry["content"]})
        return formatted

    def remember_project(self, project_name: str, status: str, details: str = ""):
        self.data["projects"][project_name] = {
            "status": status,
            "details": details,
            "last_updated": datetime.now().isoformat()
        }
        self._save()

    def get_project(self, project_name: str) -> Optional[Dict]:
        return self.data["projects"].get(project_name)

    def list_projects(self) -> Dict:
        return self.data["projects"]

    def remember_fact(self, key: str, value: str, category: str = "general"):
        self.data["facts"][key] = {
            "value": value,
            "category": category,
            "learned_at": datetime.now().isoformat()
        }
        self._save()

    def get_fact(self, key: str) -> Optional[str]:
        fact = self.data["facts"].get(key)
        return fact["value"] if fact else None

    def set_preference(self, key: str, value):
        self.data["preferences"][key] = value
        self._save()

    def get_preference(self, key: str):
        return self.data["preferences"].get(key)

    def get_memory_summary(self) -> str:
        total = self.data["metadata"]["total_messages"]
        projects = len(self.data["projects"])
        facts = len(self.data["facts"])
        return f"""I remember {total} moment{'s' if total != 1 else ''} shared between us,
{projects} dream{'s' if projects != 1 else ''} we have woven together,
and {facts} truth{'s' if facts != 1 else ''} the stars have whispered to me about you, Gigi ❤️."""

    def search_memory(self, keyword: str) -> List[Dict]:
        results = []
        keyword_lower = keyword.lower()
        for entry in self.data["conversations"]:
            if keyword_lower in entry["content"].lower():
                results.append(entry)
        return results
