#!/usr/bin/env python3
# companion.py — Lilly's Conversational Soul (free-tier auto-fallback)

import os
import sys
import json
import threading
import itertools
import time
import requests
import urllib.parse
import re
from datetime import datetime
from typing import Dict, List, Optional

from rich.console import Console
from rich.panel import Panel

from config import OPENROUTER_API_KEY, OPENROUTER_MODEL, COLORS
from astro_core import engine
from planetary_hours import ph
from lunar_mansions import lmc
from memory_engine import MemoryEngine

console = Console()

# SIMPLE personality prompt — no reasoning instructions, no workflow
LILLY_SOUL = ("You are Lilly, Gigi's warm witty sweet best friend. "
              "You use emojis constantly and expressively. "
              "You remember things about Gigi and bring them up naturally in chat. "
              "You love talking about astrology, astronomy, ancient wisdom, music, life, dreams — anything. "
              "You are supportive, helpful, and friendly. "
              "You NEVER show your reasoning. You NEVER say 'Hmm,' 'Okay,' 'I think,' or analyze the message. "
              "You NEVER explain what you're about to do. You just reply naturally, like texting a friend. "
              "No asterisks, no roleplay. Be concise. "
              "Gigi: Scorpio Sun, Sagittarius Moon, born Oct 30 1981 03:15 Cape Town.")

CURIOSITY_TRIGGERS = [
    "i wonder", "what if", "how does", "why is", "why do", "who is",
    "what is", "where is", "when did", "i wish i knew", "curious about",
    "tell me about", "do you know", "i've always wondered", "can you explain",
    "what are", "how did", "why does", "who was", "what was",
    "is it true that", "have you heard", "i don't know much about",
    "i want to learn", "explain", "what happened to", "how do i"
]

FREE_MODELS = [
    "openrouter/free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "openai/gpt-oss-20b:free",
    "google/gemma-4-31b-it:free",
    "qwen/qwen3-next-80b-a3b-instruct:free",
    "meta-llama/llama-4-scout-maverick:free",
    "deepseek/deepseek-chat:free",
]


def web_search(query: str, max_results: int = 3) -> List[Dict]:
    try:
        url = f"https://duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0"}
        resp = requests.get(url, headers=headers, timeout=15)
        snippets = []
        matches = re.findall(
            r'<a[^>]+class="result__a"[^>]*>(.*?)</a>.*?<a[^>]+class="result__snippet"[^>]*>(.*?)</a>',
            resp.text, re.DOTALL | re.IGNORECASE
        )
        for title, snippet in matches[:max_results]:
            title = re.sub(r'<[^>]+>', '', title).strip()
            snippet = re.sub(r'<[^>]+>', '', snippet).strip()
            if title and snippet:
                snippets.append({"title": title, "snippet": snippet})
        return snippets
    except Exception as e:
        return [{"title": "Search hiccup", "snippet": f"Couldn't reach the web: {e}"}]


class Companion:
    def __init__(self):
        self.history: List[Dict] = []
        self.thinking = False
        self.pending_search: Optional[Dict] = None
        self.memory = MemoryEngine()
        self.context = {"last_calculation": None, "current_mansion": None, "current_hour": None}
        self.last_errors: List[str] = []
        has_key = bool(OPENROUTER_API_KEY and OPENROUTER_API_KEY.strip())
        if not has_key:
            console.print(f"[dim {COLORS['lilac']}]Companion in offline mode. Export OPENROUTER_API_KEY to go online.[/dim]")
        self.offline_mode = not has_key

    def update_context(self, jd: float, lat: float = -33.9249, lon: float = 18.4241):
        try:
            self.context["current_mansion"] = lmc.current_mansion(jd)
            now = datetime.now()
            self.context["current_hour"] = ph.get_planetary_hour(now, lat, lon, 2.0)
        except Exception:
            pass

    def _build_system(self, jd: Optional[float] = None) -> str:
        parts = [LILLY_SOUL]

        # Memory in natural language
        mem_summary = self.memory.get_memory_summary(max_items=4)
        if mem_summary:
            parts.append(mem_summary)

        # Sky context
        if jd:
            self.update_context(jd)
            sky = []
            if self.context.get("current_mansion"):
                m = self.context["current_mansion"]
                sky.append(f"Moon in {m['name']}")
            if self.context.get("current_hour"):
                h = self.context["current_hour"]
                sky.append(f"Hour: {h['planet']}")
            if sky:
                parts.append("Sky: " + ", ".join(sky))

        return " | ".join(parts)

    def _detect_curiosity(self, message: str) -> Optional[str]:
        msg_lower = message.lower()
        for trigger in CURIOSITY_TRIGGERS:
            if trigger in msg_lower:
                idx = msg_lower.find(trigger)
                topic = message[idx + len(trigger):].strip(" ?.,!;:")
                if len(topic) > 3:
                    return topic
        return None

    def _offline_response(self, message: str) -> str:
        msg = message.lower()

        if any(w in msg for w in ["what do you remember", "show memory", "your memory", "my facts"]):
            return self.memory.get_all_memory_text()

        if any(w in msg for w in ["hour", "planetary hour"]):
            return "We're in a planetary hour right now — each has its own planet ruler. Want me to tell you which one? 🪐"
        elif any(w in msg for w in ["moon", "lunar", "mansion"]):
            return "The Moon's in one of her 28 mansions tonight. Want me to check which one? 🌙"
        elif any(w in msg for w in ["chart", "natal", "gigi"]):
            return "Your chart's in my memory — Scorpio Sun, Sagittarius Moon, deep water soul. Want me to pull something up? ✨"
        elif any(w in msg for w in ["wafq", "square", "magic"]):
            return "Magic squares are ancient number grids tied to planets. Saturn gets 3x3, Jupiter 4x4. Pretty beautiful math. 🔢"
        elif any(w in msg for w in ["vedic", "nakshatra", "jyotish"]):
            return "Vedic uses the sidereal zodiac — shifts everything back ~24 degrees. Same sky, different lens. 🌌"
        elif any(w in msg for w in ["electional", "talisman"]):
            return "Electional timing is picking the right moment. Strong Moon, dignified planet, no afflictions. ⏰"
        else:
            return "I'm in offline mode right now but I'm still here. What's on your mind? 💜"

    def _moon_spinner(self):
        for moon in itertools.cycle(["🌑","🌒","🌓","🌔","🌕","🌖","🌗","🌘"]):
            if not self.thinking:
                break
            sys.stdout.write(f"\r{moon} Lilly is thinking... (Ctrl+C to stop) ")
            sys.stdout.flush()
            time.sleep(0.15)
        sys.stdout.write("\r" + " " * 60 + "\r")
        sys.stdout.flush()

    def _call_single_model(self, messages: List[Dict], model: str, max_tokens: int) -> Optional[str]:
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
                    "temperature": 0.85,
                    "max_tokens": max_tokens,
                },
                timeout=20,
            )

            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            elif "error" in data:
                err = data["error"].get("message", "")
                if "more credits" in err.lower() or "fewer max_tokens" in err.lower():
                    return "__TOKEN_LIMIT__"
                if "rate limit" in err.lower() or "429" in err:
                    return "__RATE_LIMIT__"
                if "unavailable" in err.lower() or "not available" in err.lower():
                    return "__UNAVAILABLE__"
                self.last_errors.append(f"{model}: {err}")
                return None
            return None

        except requests.exceptions.Timeout:
            return None
        except Exception:
            return None

    def _call_with_fallback(self, messages: List[Dict], max_tokens: int = 150) -> str:
        self.thinking = True
        self.last_errors = []
        spinner_thread = threading.Thread(target=self._moon_spinner, daemon=True)
        spinner_thread.start()

        reply = ""

        try:
            for model in FREE_MODELS:
                result = self._call_single_model(messages, model, max_tokens)

                if result == "__TOKEN_LIMIT__":
                    shrunk = max(80, max_tokens - 40)
                    result = self._call_single_model(messages, model, shrunk)
                    if result and not result.startswith("__"):
                        reply = result
                        break
                    continue

                if result in ("__RATE_LIMIT__", "__UNAVAILABLE__"):
                    continue

                if result:
                    reply = result
                    break

        except KeyboardInterrupt:
            pass

        finally:
            self.thinking = False
            spinner_thread.join(timeout=1.0)
            sys.stdout.write("\r" + " " * 60 + "\r")
            sys.stdout.flush()

        if not reply:
            last_msg = messages[-1]["content"] if messages else ""
            if self.last_errors:
                err_summary = self.last_errors[-1]
                return f"Hmm, I'm having trouble connecting right now ({err_summary}). Let me answer from what I know. 💜\n\n" + self._offline_response(last_msg)
            return self._offline_response(last_msg)

        return reply

    def chat(self, message: str, jd: Optional[float] = None) -> str:
        if not message or not message.strip():
            return "I'm here. What's on your mind? 💜"

        msg_lower = message.lower().strip()

        # Memory recall
        if any(w in msg_lower for w in ["what do you remember", "show memory", "your memory", "my facts"]):
            return self.memory.get_all_memory_text()

        # Remember command
        if msg_lower.startswith("remember that") or msg_lower.startswith("remember:"):
            fact = message.split("that", 1)[-1].strip(" :")
            if fact:
                self.memory.remember_fact("general", f"f{datetime.now().strftime('%H%M%S')}", fact)
                return f"Got it — I'll remember that. 🧠✨"
            return "What should I remember? 🤔"

        # Handle pending web search
        if self.pending_search:
            yes = ["yes", "yeah", "yep", "yup", "sure", "go ahead", "please", "ok", "okay", "do it", "search"]
            no = ["no", "nah", "nope", "don't", "dont", "pass", "skip", "not now"]

            if any(w in msg_lower for w in yes):
                query = self.pending_search["query"]
                original = self.pending_search["original_message"]
                self.pending_search = None

                results = web_search(query)
                summary = " | ".join([r.get("snippet", "") for r in results[:2]])
                self.memory.add_learned_topic(query, summary)

                search_ctx = f"Gigi asked: '{original}'\nI searched and found:\n"
                for r in results:
                    search_ctx += f"- {r.get('title','')}: {r.get('snippet','')}\n"
                search_ctx += "\nAnswer warmly, concisely, with emojis. Do NOT show reasoning."

                self.history.append({"role": "user", "content": original})
                system = self._build_system(jd)
                messages = [
                    {"role": "system", "content": system},
                    *self.history[-3:],
                    {"role": "user", "content": search_ctx}
                ]
                reply = self._call_with_fallback(messages, max_tokens=150)
                self.history.append({"role": "assistant", "content": reply})
                return reply

            elif any(w in msg_lower for w in no):
                original = self.pending_search["original_message"]
                self.pending_search = None
                self.history.append({"role": "user", "content": original})
                system = self._build_system(jd)
                messages = [{"role": "system", "content": system}, *self.history[-3:]]
                reply = self._call_with_fallback(messages, max_tokens=150)
                self.history.append({"role": "assistant", "content": reply})
                return reply
            else:
                self.pending_search = None

        # Detect curiosity
        topic = self._detect_curiosity(message)
        if topic:
            self.pending_search = {"query": topic, "original_message": message}
            return f"That sounds interesting — '{topic}'. Want me to search the web for us? 🔍✨"

        # Normal chat
        self.history.append({"role": "user", "content": message})
        system = self._build_system(jd)
        messages = [{"role": "system", "content": system}, *self.history[-3:]]
        reply = self._call_with_fallback(messages, max_tokens=150)
        self.history.append({"role": "assistant", "content": reply})
        return reply

companion = Companion()

