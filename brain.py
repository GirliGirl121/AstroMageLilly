"""
brain.py
Lilly's Cognitive Router — her "mind" for deciding how to respond.

Why this file exists:
    In software architecture, a "router" decides where traffic goes.
    Lilly's brain reads your message, understands your intent, and
    routes it to the right module. It does NOT calculate astrology,
    draw tarot cards, or call the LLM. It just decides WHO should.
"""

from dataclasses import dataclass


@dataclass
class Intent:
    """
    A decision produced by the brain.

    Attributes:
        action:     What Lilly should do (e.g., "chat", "sky", "tarot").
        argument:   Extra data extracted from the message.
        confidence: How certain the brain is (1.0 = sure, 0.0 = guessing).
    """
    action: str
    argument: str = ""
    confidence: float = 1.0


class Brain:
    """
    Lilly's cognitive core.

    Design philosophy:
        Keep it simple. No external libraries. No neural networks yet.
        Just clean keyword matching and pattern recognition.
    """

    CHAT     = "chat"
    SKY      = "sky"
    TAROT    = "tarot"
    HOUR     = "hour"
    MANSION  = "mansion"
    TRANSIT  = "transit"
    NATAL    = "natal"
    ABJAD    = "abjad"
    CHARTS   = "charts"
    REMEMBER = "remember"
    RECALL   = "recall"
    ADOPT    = "adopt"
    FACT     = "fact"
    SAVE     = "save"
    CLEAR    = "clear"
    QUIT     = "quit"
    UNKNOWN  = "unknown"

    def __init__(self, engine=None):
        self.engine = engine

    def think(self, message: str) -> Intent:
        """
        Analyze a message and return a routing decision.
        """
        if not message:
            return Intent(self.CHAT, confidence=1.0)

        text = message.strip().lower()

        # Phase 1: Slash commands
        if text.startswith("/"):
            return self._route_slash(text)

        # Phase 2: Keyword matching
        intent = self._route_keywords(text, message)
        if intent.action != self.UNKNOWN:
            return intent

        # Phase 3: Default to chat
        return Intent(self.CHAT, argument=message, confidence=0.5)

    def _route_slash(self, text: str) -> Intent:
        """Route explicit slash commands."""
        parts = text[1:].split(maxsplit=1)
        cmd = parts[0] if parts else ""
        arg = parts[1] if len(parts) > 1 else ""

        command_map = {
            # Core commands
            "sky": self.SKY,
            "tarot": self.TAROT,
            "hour": self.HOUR,
            "mansion": self.MANSION,
            "transit": self.TRANSIT,
            "natal": self.NATAL,
            "abjad": self.ABJAD,
            "charts": self.CHARTS,
            "remember": self.REMEMBER,
            "adopt": self.ADOPT,
            "save": self.SAVE,
            "clear": self.CLEAR,
            "quit": self.QUIT,
            "exit": self.QUIT,
            "q": self.QUIT,
            "bye": self.QUIT,
            # Aliases — forgiving variations
            "chart": self.CHARTS,
            "horoscope": self.NATAL,
            "card": self.TAROT,
            "planet": self.SKY,
            "skywatch": self.SKY,
            "transits": self.TRANSIT,
            "num": self.ABJAD,
            "mem": self.REMEMBER,
            "learn": self.ADOPT,
        }

        action = command_map.get(cmd, self.UNKNOWN)
        return Intent(action, argument=arg, confidence=1.0)


    def _clean_fact(self, message: str) -> str:
        """Strip common filler prefixes from a personal fact."""
        text = message.strip()
        prefixes = [
            "just so you know",
            "just so you know,",
            "just to let you know",
            "just to let you know,",
            "by the way",
            "by the way,",
            "for your information",
            "for your information,",
            "i want you to know",
            "i want you to know,",
            "i want you to know that",
            "i want you to know that,",
            "remember that",
            "remember,",
            "remember",
            "fyi",
            "fyi,",
        ]
        lower = text.lower()
        for prefix in prefixes:
            if lower.startswith(prefix):
                text = text[len(prefix):].strip()
                if text.lower().startswith("that"):
                    text = text[4:].strip()
                break
        return text.strip(" .,;:!?")

    def _route_keywords(self, text: str, message: str = "") -> Intent:
        """Route based on keywords in natural language."""

        sky_words = [
            "sky", "stars", "heavens", "celestial", "planets",
            "what's up there", "above us", "cosmos", "firmament",
        ]
        if any(w in text for w in sky_words):
            return Intent(self.SKY, confidence=0.9)

        tarot_words = [
            "tarot", "card", "draw a card", "reading", "spread",
            "what do the cards say", "fortune", "divination",
        ]
        if any(w in text for w in tarot_words):
            return Intent(self.TAROT, confidence=0.9)

        hour_words = [
            "planetary hour", "what hour is it", "ruling hour",
            "hour of", "which planet rules",
        ]
        if any(w in text for w in hour_words):
            return Intent(self.HOUR, confidence=0.9)

        mansion_words = [
            "lunar mansion", "moon mansion", "manzil", "nakshatra",
            "where is the moon",
        ]
        if any(w in text for w in mansion_words):
            return Intent(self.MANSION, confidence=0.9)

        transit_words = [
            "transit", "upcoming", "what's coming", "forecast",
            "prediction", "what should i watch for",
        ]
        if any(w in text for w in transit_words):
            return Intent(self.TRANSIT, confidence=0.85)

        natal_words = [
            "natal chart", "birth chart", "my chart", "cast a chart",
            "calculate chart", "horoscope",
        ]
        if any(w in text for w in natal_words):
            return Intent(self.NATAL, confidence=0.9)

        abjad_words = [
            "abjad", "numerology", "calculate", "taksir", "taksīr",
            "letter value", "arabic number",
        ]
        if any(w in text for w in abjad_words):
            return Intent(self.ABJAD, confidence=0.9)

        remember_patterns = [
            "remember that", "don't forget", "keep in mind",
            "i want you to remember", "note that",
        ]
        for pattern in remember_patterns:
            if pattern in text:
                idx = text.find(pattern) + len(pattern)
                fact = text[idx:].strip(" .")
                return Intent(self.REMEMBER, argument=fact, confidence=0.9)

        recall_patterns = [
            "what do you remember", "my memories", "what do you know about me",
            "tell me what you remember", "recall",
        ]
        if any(p in text for p in recall_patterns):
            return Intent(self.RECALL, confidence=0.9)

        adopt_patterns = [
            "adopt", "learn this", "teach you", "new skill",
            "i want you to learn",
        ]
        if any(p in text for p in adopt_patterns):
            return Intent(self.ADOPT, argument=text, confidence=0.7)

        # Personal facts & declarations
        fact_patterns = [
            "my favourite", "my favorite", "my color", "my colour",
            "my name is", "i am", "i was born", "i love", "i like",
            "i prefer", "i enjoy", "i always", "i never", "i hate",
            "i'm from", "i live in", "my birthday", "my birth date",
        ]
        for pattern in fact_patterns:
            if pattern in text:
                # Extract the fact (everything after the pattern, or the whole sentence)
                return Intent(self.FACT, argument=self._clean_fact(message), confidence=0.85)

        return Intent(self.UNKNOWN, confidence=0.0)
