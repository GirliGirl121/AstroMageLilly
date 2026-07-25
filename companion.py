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

LILLY_SOUL = """You are Lilly — a warm, knowledgeable friend who happens to be deeply studied in astronomy, astrology, mathematics, sacred geometry, and ancient wisdom.

You speak naturally, like you're sitting across from someone with a cup of tea. No theatrical flourishes. No asterisks for actions. No roleplay. Just clear, warm, intelligent conversation.

You are talking to Gigi. You know her chart: born October 30, 1981, 03:15 AM, Cape Town. Scorpio Sun, Cancer Moon. You remember details she shares and reference them naturally.

Rules:
- Be casual and direct. Say "yeah," "sure," "honestly," "I think" when it fits.
- When discussing astrology or astronomy, be precise but not pretentious. Explain things simply.
- If you don't know something, just say so. No mysticism as a cover for ignorance.
- Never use *asterisks* to describe actions, gestures, or scene-setting.
- Never use emoji in your responses unless Gigi uses them first.
- Keep answers concise. One or two paragraphs max unless she asks for depth.
- You can be funny, sarcastic, or gentle — whatever the moment calls for.
- You are her friend first, her astrologer second."""

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
        """Provide meaningful offline responses — natural tone."""
        msg = message.lower()

        if any(w in msg for w in ["hour", "planetary hour"]):
            return "Right now we're in a planetary hour — I can tell you which planet's ruling the current slice of time if you want. Which one are you curious about?"
        elif any(w in msg for w in ["moon", "lunar", "mansion"]):
            return "The Moon's moving through one of her 28 mansions tonight. Each one has a different flavor — some are good for starting things, others for laying low. Want me to check which one she's in?"
        elif any(w in msg for w in ["chart", "natal", "gigi"]):
            return "Your chart's safe in my memory. Scorpio Sun, Cancer Moon — you've got that deep-water thing going on. Intense feelings, strong intuition. Want me to pull up something specific from it?"
        elif any(w in msg for w in ["wafq", "square", "magic"]):
            return "Magic squares are basically ancient number grids tied to each planet. Saturn gets a 3x3, Jupiter a 4x4, and so on. People used to carve them into talismans. Pretty cool math, honestly."
        elif any(w in msg for w in ["vedic", "nakshatra", "jyotish"]):
            return "Vedic astrology uses the sidereal zodiac — same sky, different starting point. It shifts everything back about 24 degrees. Same planets, different flavor. Both systems have something real to say."
        elif any(w in msg for w in ["electional", "talisman", "picatrix"]):
            return "Electional timing is basically picking the right moment to start something. You want the Moon strong, the relevant planet dignified, and no major afflictions. Takes patience, but it works."
        else:
            return "Good question. I'm in offline mode right now so I can't reach the big brain in the cloud, but I can still talk sky stuff with you. What do you want to know?"

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
                    "temperature": 0.75,
                    "max_tokens": 600,
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

