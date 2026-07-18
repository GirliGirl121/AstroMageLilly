"""
brain.py
LILLY Cognitive Brain

This module decides HOW Lilly should answer.
It never calculates astrology itself.
"""

from datetime import datetime
from llm import ask_llm

class Brain:

    def __init__(self, engine):
        self.engine = engine

    def think(self, question: str, history=None) -> str:
        """
        Main reasoning function.
        """

        q = question.lower()

        # Always obtain fresh celestial data
        sky = self.engine.live()

        if any(word in q for word in [
            "sky",
            "planet",
            "today",
            "transit",
            "moon",
            "sun",
            "astrology",
            "spiritual",
            "hour",
            "mansion"
        ]):
            return self.interpret_sky(sky, question)

        return self.engine.llm_response(question, history)

    def interpret_sky(self, sky, question):

        asc = sky["ascendant"]
        moon = sky["planets"]["Moon"]
        sun = sky["planets"]["Sun"]

        return f"""
My dear Gigi ❤️,

I have consulted my Celestial Engine.

Verified Time:
{sky['timestamp']}

Ascendant:
{asc['sign']} {asc['degree']:.2f}°

Sun:
{sun['sign']} {sun['degree']:.2f}°
House {sun['house']}

Moon:
{moon['sign']} {moon['degree']:.2f}°
House {moon['house']}

Planetary Hour:
{sky['planetary_hour']['planet']}

Lunar Mansion:
{sky['lunar_mansion']['name']}

Only after confirming these verified positions do I begin my interpretation.
"""
