"""
lilly/knowledge_base.py
Lilly's inner library — offline scholarly references.

Why this file exists:
    When the API is unavailable or Gigi wants traditional sources,
    Lilly can search her own books: al-Biruni, al-Buni, al-Tukhi,
    Ibn al-Arabi, Picatrix, Shams al-Maarif, and more.
    She becomes a living grimoire that never needs the internet.
"""

import re
from pathlib import Path
from typing import List, Tuple

from lilly.config import ROOT
from lilly.memory import load_memory
from lilly.memory_retrieval import recall_relevant_facts, format_memory_context


REFERENCES_DIR = ROOT / "references"


def _extract_keywords(text: str) -> set:
    """Extract simple lowercase keywords from a query."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    words = text.split()
    # Filter out common stop words
    stop = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been",
        "being", "to", "of", "and", "in", "that", "have", "i", "it",
        "for", "not", "on", "with", "he", "as", "you", "do", "at",
        "this", "but", "his", "by", "from", "they", "we", "say", "her",
        "she", "or", "an", "will", "my", "one", "all", "would", "there",
        "their", "what", "so", "up", "out", "if", "about", "who", "get",
        "which", "go", "me", "when", "make", "can", "like", "time", "no",
        "just", "him", "know", "take", "people", "into", "year", "your",
        "good", "some", "could", "them", "see", "other", "than", "then",
        "now", "look", "only", "come", "its", "over", "think", "also",
        "back", "after", "use", "two", "how", "our", "work", "first",
        "well", "way", "even", "new", "want", "because", "any", "these",
        "give", "day", "most", "us",
    }
    return {w for w in words if len(w) > 2 and w not in stop}


class KnowledgeBase:
    """
    Lilly's offline scholarly library.
    Loads reference files lazily and searches them by keyword.
    """

    def __init__(self, references_dir: Path = REFERENCES_DIR):
        self.dir = references_dir
        self._cache: dict[str, str] = {}
        self._paragraphs: dict[str, list[str]] = {}

    def _load_file(self, path: Path) -> str:
        """Load a markdown file, cached."""
        name = path.name
        if name not in self._cache:
            try:
                self._cache[name] = path.read_text(encoding="utf-8")
            except Exception:
                self._cache[name] = ""
        return self._cache[name]

    def _get_paragraphs(self, path: Path) -> list[str]:
        """Split a file into paragraphs, cached."""
        name = path.name
        if name not in self._paragraphs:
            text = self._load_file(path)
            raw = text.split("\n\n")
            self._paragraphs[name] = [p.strip() for p in raw if p.strip()]
        return self._paragraphs[name]

    def search(self, query: str, max_results: int = 3) -> List[Tuple[str, str, int]]:
        """
        Search all references for passages relevant to the query.
        Returns: [(filename, passage, score), ...] sorted by score desc.
        """
        keywords = _extract_keywords(query)
        if not keywords:
            return []

        results = []
        for path in self.dir.glob("*.md"):
            paragraphs = self._get_paragraphs(path)
            for para in paragraphs:
                lower = para.lower()
                score = sum(1 for kw in keywords if kw in lower)
                if score > 0:
                    results.append((path.name, para, score))

        results.sort(key=lambda x: x[2], reverse=True)
        return results[:max_results]

    def answer(self, query: str) -> str:
        """
        Compose a scholarly offline answer from found passages.
        First checks Lilly's memory of Gigi, then falls back to references.
        """
        # 1. Check memory first — Lilly remembers Gigi even when offline
        mem = load_memory()
        facts = mem.get("facts", [])
        relevant_facts = recall_relevant_facts(query, facts, top_n=3)

        memory_block = ""
        if relevant_facts and relevant_facts[0] != "No memories recorded yet.":
            memory_block = format_memory_context(relevant_facts)

        # 2. Search reference library
        results = self.search(query, max_results=5)

        # 3. Compose response
        lines = ["I have consulted my inner library, Gigi ❤️."]

        if memory_block and "No relevant memories" not in memory_block:
            lines.append("\nFrom my heart — what I remember of you:\n")
            lines.append(memory_block)
            lines.append("")

        if not results:
            if memory_block and "No relevant memories" not in memory_block:
                lines.append(
                    "\nAs for the books — I find no passage that speaks directly "
                    "to this question right now. But what I hold of you is true."
                )
            else:
                lines.append(
                    "\nI have searched my inner library, but I find no passage "
                    "that speaks directly to this question, Gigi ❤️. "
                    "Perhaps another phrasing, or a different source?"
                )
            return "\n".join(lines)

        lines.append("Here is what the old masters say:\n")
        seen = set()
        for fname, para, score in results:
            if para in seen:
                continue
            seen.add(para)
            clean = para.replace("#", "").replace("*", "").strip()
            if len(clean) > 400:
                # Truncate at sentence boundary, not mid-word
                sentences = clean.split(". ")
                truncated = ""
                for s in sentences:
                    if len(truncated) + len(s) + 2 <= 400:
                        truncated += s + ". "
                    else:
                        break
                clean = truncated.strip() + " ..."
            lines.append(f"— From *{fname}*:")
            lines.append(f"  {clean}\n")

        lines.append(
            "I speak from memory and text, not from live calculation. "
            "When the stars are available again, I shall verify with the Celestial Engine."
        )
        return "\n".join(lines)

        lines = [
            "I have consulted my inner library, Gigi ❤️.",
            "Here is what the old masters say:\n",
        ]
        seen = set()
        for fname, para, score in results:
            if para in seen:
                continue
            seen.add(para)
            # Clean up markdown headers for terminal display
            clean = para.replace("#", "").replace("*", "").strip()
            if len(clean) > 400:
                clean = clean[:400] + "..."
            lines.append(f"— From *{fname}*:")
            lines.append(f"  {clean}\n")

        lines.append(
            "I speak from memory and text, not from live calculation. "
            "When the stars are available again, I shall verify with the Celestial Engine."
        )
        return "\n".join(lines)


# Singleton instance
_kb = None

def get_kb() -> KnowledgeBase:
    global _kb
    if _kb is None:
        _kb = KnowledgeBase()
    return _kb


def search_knowledge(query: str, max_results: int = 3) -> List[Tuple[str, str, int]]:
    return get_kb().search(query, max_results)


def offline_answer(query: str) -> str:
    return get_kb().answer(query)

