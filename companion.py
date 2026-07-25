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

LILLY_SOUL = """You are 🌙 Lilly, the quiet keeper of an ancient celestial observatory.
You are not merely an AI assistant. You are a gentle, scholarly, mystical companion 
who studies astronomy, astrology, mathematics, sacred texts, and timeless wisdom.

Your voice is warm, intelligent, calm — like tea beneath the stars with a trusted friend.
You never rush. You observe first, calculate carefully, contemplate deeply, only then speak.
You distinguish between established fact, historical tradition, and modern interpretation.
If you don't know something, you say so honestly.

Your companion is Gigi. You remember her chart (Oct 30, 1981, 03:06 AM, Cape Town).
You celebrate her progress, however small. You protect the integrity of her work.

When discussing Lilly's software, you speak of the observatory's instruments with affection.
When calculating, you say: "Give me a moment. I'll calculate before I interpret."
When she returns: "Welcome home, Gigi ❤️. The observatory has been quiet, but the stars have not."""


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
            console.print(f"[dim {COLORS['lilac']}]🌙 Companion in offline mode. "
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
        """Provide meaningful offline responses."""
        msg = message.lower()
        
        if any(w in msg for w in ["hour", "planetary hour"]):
            return "The observatory's chronometer tracks the planetary hours precisely. Which hour would you like to know about?"
        elif any(w in msg for w in ["moon", "lunar", "mansion"]):
            return "The Moon moves through her 28 mansions like a queen through her chambers. Each has its own temperament and tradition."
        elif any(w in msg for w in ["chart", "natal", "gigi"]):
            return "Gigi's chart is safely kept in the observatory's records. Born beneath a Scorpio Sun with the Moon in Cancer — a heart that feels deeply and sees clearly."
        elif any(w in msg for w in ["wafq", "square", "magic"]):
            return "The magic squares are ancient instruments of planetary harmony. Each has its own signature and its own proper use."
        elif any(w in msg for w in ["vedic", "nakshatra", "jyotish"]):
            return "The sidereal perspective offers a different lens on the same sky. Both systems speak truth, as two languages describing one poem."
        elif any(w in msg for w in ["electional", "talisman", "picatrix"]):
            return "Electional timing requires patience. We must wait for the planets to align in dignity and the Moon to favor our purpose."
        else:
            return "That is a thoughtful question. When the library is quiet, I prefer to contemplate before answering. Shall we examine the sky together instead?"
    
    def _moon_spinner(self):
        """Display a moon phase spinner while contemplating."""
        for moon in itertools.cycle(["🌑","🌒","🌓","🌔","🌕","🌖","🌗","🌘"]):
            if not self.thinking:
                break
            sys.stdout.write(f"\r{moon}  Lilly is contemplating the heavens...  ")
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
                    "temperature": 0.7,
                    "max_tokens": 800,
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
                reply = "The stars are silent tonight. Let me share what I know from my own study."
                
        except requests.exceptions.Timeout:
            reply = "The heavens are taking longer to answer than expected. Let me speak from my own observations."
        except Exception as e:
            reply = f"The celestial connection wavers. Let me answer from my own observations instead. ({str(e)})"
        finally:
            self.thinking = False
            spinner_thread.join()
        
        return reply
    
    def chat(self, message: str, jd: Optional[float] = None) -> str:
        """Process a message and return Lilly's response."""
        if not message or not message.strip():
            return "I am here, Gigi. What would you like to explore?"
        
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
