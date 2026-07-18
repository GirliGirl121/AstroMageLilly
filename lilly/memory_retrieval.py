"""
lilly/memory_retrieval.py

Smart memory retrieval for Lilly.

Why this exists:
    The old system dumped ALL facts into EVERY prompt. As memory grows,
    this bloats tokens, drowns signal in noise, and wastes API calls.
    This module scores each fact for relevance to the current prompt
    and returns only the most useful ones.

Design philosophy:
    No external libraries. No neural networks. Just clean word overlap
    scoring that works on Termux/Android without bloat.
"""

import re


def _tokenize(text: str) -> set[str]:
    """Extract meaningful words from text, lowercase, no punctuation."""
    return set(re.findall(r"[a-zA-Z]{2,}", text.lower()))


def recall_relevant_facts(prompt: str, facts: list[str], top_n: int = 5) -> list[str]:
    """
    Score each fact for relevance to the prompt and return the top N.

    Scoring:
        Simple word overlap. For each fact, count how many words from
        the prompt appear in that fact. Higher count = more relevant.

    Fallback:
        If no fact scores above 0 (no overlap), return the most recent
        N facts. This ensures Lilly never has "zero memory" in a chat.

    Args:
        prompt: The user's current message.
        facts:  All stored memory facts (ordered newest-first).
        top_n:  How many facts to return (default 5).

    Returns:
        A list of the most relevant fact strings.
    """
    if not facts:
        return []

    prompt_words = _tokenize(prompt)

    scored = []
    for fact in facts:
        fact_words = _tokenize(fact)
        score = len(prompt_words & fact_words)  # intersection count
        scored.append((score, fact))

    # Sort by score descending
    scored.sort(key=lambda x: x[0], reverse=True)

    # If top scorer is 0, fall back to most recent facts
    if scored[0][0] == 0:
        return facts[:top_n]

    # Return top N, preserving original order among ties
    return [fact for _, fact in scored[:top_n]]


def format_memory_context(facts: list[str]) -> str:
    """Format a list of facts into Lilly's memory block."""
    if not facts:
        return "No relevant memories for this conversation."
    return "Lilly's Relevant Memories of Gigi:\n- " + "\n- ".join(facts)
