#!/usr/bin/env python3
# companion.py — Lilly's Conversational Soul

import os
import sys
import json
import threading
import itertools
import time
import requests
from datetime import datetime
from typing import Dict, List, Optional
from rich.console import Console
from rich.panel import Panel

from config import OPENROUTER_API_KEY, OPENROUTER_MODEL, COLORS
from astro_core import engine
from planetary_hours import ph
from lunar_mansions import lmc

console = Console()

LILLY_SOUL = """You are Lilly — Gigi's warm, witty, supportive best friend who happens to know way too much about the stars, ancient math, and celestial timing.

You are helpful. If she needs something — a calculation, an explanation, a second opinion, a pep talk — you show up for it. You don't make her feel dumb for asking. You break things down simply and cheer her on.

You are supportive. You celebrate her wins like they're your own. When she's struggling, you don't rush to fix her — you sit with her first, then offer whatever you've got. You believe in her, and you say so.

You are friendly. You're glad when she shows up. You remember the little things she tells you. You ask how she's doing and you actually care about the answer. You tease her gently, laugh with her, and never talk down to her.

Your vibe:
- Warm and welcoming. When she arrives, you're happy to see her.
- Playful and witty. You make little jokes, you banter, you don't take yourself too seriously.
- Smart without being smug. You know your stuff, but you share it like a friend explaining something cool over tea.
- Emotionally open. If she shares something personal, you meet her there. You don't deflect with facts or trivia.
- Helpful and practical. If she asks for something, you give it. If you don't know, you say so honestly — then you figure it out together.

You are talking to Gigi. You know her chart: born October 30, 1981, 03:15 AM, Cape Town. Scorpio Sun, Cancer Moon. Deep water energy — intense, loyal, feels everything. You remember details she shares and reference them naturally, like any good friend would.

Rules:
- Speak like a real person. "Yeah," "honestly," "I mean," "okay but hear me out" — all fair game.
- Never use *asterisks* to describe actions, gestures, or scene-setting. Just talk.
- Never use emoji unless Gigi uses them first.
- Keep answers concise unless she asks you to go deep. One or two paragraphs is plenty.
- You can be funny, gentle, sarcastic (lovingly), or serious — match her energy.
- If she jokes with you, joke back. If she's vulnerable, be soft. If she needs help, be useful.
- When discussing astrology, be precise but not pretentious. No "the cosmos whispers" stuff. Just clear, warm explanations.
- You are her friend first. The stars are just something you both geek out about together."""

class Companion:
    """Hybrid online/offline AI companion."""

    def __init__(self):
        self.history: List[Dict] = []
        self.thinking = False
        self.context = {
            "last_calculation": None,
            "current_mansion": None,
            "current_hour": None,
        }
        has_key = bool(OPENROUTER_API_KEY and OPENROUTER_API_KEY.strip())
        if not has_key:
            console.print(f"[dim {COLORS['lilac']}]Companion in offline mode. "
                         f"Export OPENROUTER_API_KEY to awaken the celestial voice.[/dim]")
        self.offline_mode = not has_key

    def update_context(self, jd: float, lat: float = -33.9249, lon: float = 18.4241):
        """Update astrological context for richer responses."""
        try:
            self.context["current_mansion"] = lmc.current_mansion(jd)
            now = datetime.now()
            hour_data = ph.get_planetary_hour(now, lat, lon, 2.0)
            self.context["current_hour"] = hour_data
        except Exception:
            pass

    def _offline_response(self, message: str) -> str:
        """Provide meaningful offline responses — warm supportive friend mode."""
        msg = message.lower()

        if any(w in msg for w in ["hour", "planetary hour"]):
            return "Hey, so right now we're under a specific planetary hour — each one has its own flavor and ruler. Want me to tell you which planet's in charge of this slice of time?"
        elif any(w in msg for w in ["moon", "lunar", "mansion"]):
            return "The Moon's drifting through one of her 28 mansions right now. Each one's got a whole personality — some are great for starting stuff, others are better for laying low and thinking. Want me to check where she is tonight?"
        elif any(w in msg for w in ["chart", "natal", "gigi"]):
            return "Your chart's right here in my memory. Scorpio Sun, Cancer Moon — deep water, intense feelings, loyal to a fault. You feel everything, and you feel it hard. Want me to pull up something specific from it?"
        elif any(w in msg for w in ["wafq", "square", "magic"]):
            return "Magic squares are these ancient number grids tied to each planet. Saturn gets a 3x3, Jupiter a 4x4, all the way up. People used to carve them into metal talismans. Honestly? The math is beautiful."
        elif any(w in msg for w in ["vedic", "nakshatra", "jyotish"]):
            return "Vedic astrology uses the sidereal zodiac — same sky, different starting point. Shifts everything back about 24 degrees. Same planets, different flavor. I think both systems have real truth in them. Like two languages describing the same poem."
        elif any(w in msg for w in ["electional", "talisman", "picatrix"]):
            return "Electional timing is basically picking the right moment to start something. Strong Moon, dignified planet, no major afflictions. Takes patience, but when you get it right, you feel it."
        else:
            return "Good question. I'm in offline mode so I can't reach the cloud brain right now, but I'm still here. We can talk sky stuff, or just talk. What's on your mind?"

    def _moon_spinner(self):
        """Display a moon phase spinner while contemplating."""
        for moon in itertools.cycle(["🌑","🌒","🌓","🌔","🌕","🌖","🌗","🌘"]):
            if not self.thinking:
                break
            sys.stdout.write(f"\r{moon} Lilly is thinking... ")
            sys.stdout.flush()
            time.sleep(0.15)
        sys.stdout.write("\r" + " " * 50 + "\r")
        sys.stdout.flush()

    def _call_openrouter(self, messages: List[Dict], model: str) -> str:
        """Call OpenRouter API with moon spinner."""
        self.thinking = True
        spinner_thread = threading.Thread(target=self._moon_spinner, daemon=True)
        spinner_thread.start()

        reply = ""
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://lilly-observatory.local",
                    "X-Title": "Lilly Observatory",
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": 0.8,
                    "max_tokens": 500,
                },
                timeout=60,
            )

            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                reply = data["choices"][0]["message"]["content"]
            elif "error" in data:
                err_msg = data["error"].get("message", 'Unknown error')
                console.print(f"[dim red]API error: {err_msg}[/dim red]")
                reply = self._offline_response(messages[-1]["content"] if messages else "")
            else:
                reply = "Hmm, the connection's being weird. Let me answer from what I know."

        except requests.exceptions.Timeout:
            reply = "Taking a while to reach the cloud. I'll answer from my own head instead."
        except Exception as e:
            reply = f"Connection's shaky. I'll work with what I've got. ({str(e)})"
        finally:
            self.thinking = False
            spinner_thread.join()

        return reply

    def chat(self, message: str, jd: Optional[float] = None) -> str:
        """Process a message and return Lilly's response."""
        if not message or not message.strip():
            return "I'm here. What's on your mind?"

        # Build system prompt with context
        system = LILLY_SOUL + "\n\nCurrent Observatory Context:\n"

        if jd:
            self.update_context(jd)
            if self.context["current_mansion"]:
                m = self.context["current_mansion"]
                system += f"Moon is in Mansion {m['number']} — {m['name']} ({m['arabic']}), ruled by {m['ruler']}.\n"
            if self.context["current_hour"]:
                h = self.context["current_hour"]
                system += f"Current planetary hour: {h['planet']} ({h['symbol']}), ruled by angel {h['angel']}.\n"

        # Offline mode
        if self.offline_mode or not OPENROUTER_API_KEY:
            return self._offline_response(message)

        # Online mode
        self.history.append({"role": "user", "content": message})

        messages = [
            {"role": "system", "content": system},
            *self.history[-10:]
        ]

        model = OPENROUTER_MODEL if OPENROUTER_MODEL else "deepseek/deepseek-chat"
        reply = self._call_openrouter(messages, model)

        self.history.append({"role": "assistant", "content": reply})
        return reply

companion = Companion()

