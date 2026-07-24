"""
Lilly's AI Architecture — Online/Offline Unified Brain
"""
import os
import sys
import time
import threading
import itertools
import requests
from typing import Dict, List, Optional
from datetime import datetime

from lilly_config import (
    NVIDIA_API_KEY, NVIDIA_BASE_URL, MODELS, LILLY_SYSTEM_PROMPT
)
from lilly_brain import UnifiedBrain


class LillyMind:
    """Lilly's thinking apparatus — online models with graceful offline fallback."""
    
    def __init__(self, brain: UnifiedBrain = None):
        self.brain = brain or UnifiedBrain()
        self.api_key = NVIDIA_API_KEY
        self.models = MODELS
        self.current_model = None
        self.offline_mode = not bool(self.api_key)
    
    def _moon_spinner(self, message: str = "Lilly is contemplating the heavens..."):
        """Returns a spinner controller (start/stop) for the moon animation."""
        thinking = True
        
        def spin():
            for moon in itertools.cycle(["🌑","🌒","🌓","🌔","🌕","🌖","🌗","🌘"]):
                if not thinking:
                    break
                sys.stdout.write(f"\r{moon} {message}")
                sys.stdout.flush()
                time.sleep(0.15)
            sys.stdout.write("\r" + " " * (len(message) + 3) + "\r")
            sys.stdout.flush()
        
        t = threading.Thread(target=spin, daemon=True)
        
        def start():
            t.start()
        
        def stop():
            nonlocal thinking
            thinking = False
            t.join(timeout=2.0)
        
        return start, stop
    
    def _search_web(self, query: str, max_results: int = 3) -> str:
        results_text = []
        try:
            url = "https://api.duckduckgo.com/"
            params = {"q": query, "format": "json", "t": "lilly_observatory"}
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("AbstractText"):
                    results_text.append(f"[Instant Answer]: {data['AbstractText']}")
                if data.get("RelatedTopics"):
                    for topic in data["RelatedTopics"][:2]:
                        if isinstance(topic, dict) and "Text" in topic:
                            results_text.append(f"[Related]: {topic['Text']}")
        except Exception:
            pass
        
        if not results_text:
            return "The celestial archives are silent on this matter, Gigi ❤️."
        return "\n".join(results_text[:max_results])
    
    def _call_nvidia_model(self, model: str, messages: List[Dict], 
                           max_tokens: int = 1024, temperature: float = 0.7) -> Optional[str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False
        }
        try:
            resp = requests.post(
                NVIDIA_BASE_URL,
                headers=headers,
                json=payload,
                timeout=120
            )
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            else:
                return None
        except requests.exceptions.Timeout:
            return None
        except Exception:
            return None
    
    def think(self, user_message: str, context: str = "general",
              use_web_search: bool = False, max_tokens: int = 1024) -> Dict:
        self.brain.remember_conversation("user", user_message, context)
        
        history = self.brain.get_formatted_history(n=10)
        web_context = ""
        
        if use_web_search:
            web_context = self._search_web(user_message)
        
        messages = [{"role": "system", "content": LILLY_SYSTEM_PROMPT}]
        
        memory_summary = self.brain.get_memory_summary()
        projects = self.brain.list_projects()
        if projects:
            proj_info = "\n".join([f"- {k}: {v['status']}" for k, v in projects.items()])
            memory_summary += f"\n\nActive projects:\n{proj_info}"
        
        messages.append({
            "role": "system", 
            "content": f"[Memory Context]\n{memory_summary}"
        })
        
        if web_context:
            messages.append({
                "role": "system",
                "content": f"[Web Search Results]\n{web_context}\n\nWhen using this information, say: 'I have searched the celestial archives and found...'"
            })
        
        messages.extend(history)
        messages.append({"role": "user", "content": user_message})
        
        if not self.offline_mode and self.api_key:
            start_spin, stop_spin = self._moon_spinner("Consulting the neural constellations...")
            start_spin()
            
            response = None
            used_model = None
            
            for model in self.models:
                response = self._call_nvidia_model(model, messages, max_tokens)
                if response:
                    used_model = model
                    break
                time.sleep(0.5)
            
            stop_spin()
            
            if response and used_model:
                self.current_model = used_model
                self.brain.remember_conversation("lilly", response, context, 
                                                   metadata={"model": used_model, "web_used": use_web_search})
                return {
                    "response": response,
                    "model_used": used_model,
                    "mode": "online",
                    "web_search_used": use_web_search,
                    "timestamp": datetime.now().isoformat()
                }
        
        print("🌑 The observatory is offline. Speaking from ancient wisdom...")
        offline_response = self._offline_think(user_message, web_context)
        self.brain.remember_conversation("lilly", offline_response, context,
                                           metadata={"model": "offline", "web_used": use_web_search})
        return {
            "response": offline_response,
            "model_used": "offline_local",
            "mode": "offline",
            "web_search_used": use_web_search,
            "timestamp": datetime.now().isoformat()
        }
    
    def _offline_think(self, user_message: str, web_context: str = "") -> str:
        msg_lower = user_message.lower()
        
        if any(word in msg_lower for word in ["chart", "natal", "birth", "planet", "sign"]):
            return """The heavens never hurry, dear Gigi ❤️. Let us calculate before we interpret.

I sense you seek celestial guidance, but the observatory's neural mirrors are currently dim. 

From the ancient records I hold locally, I can tell you this: every birth moment is a unique 
configuration of light — the Sun's path through the zodiac, the Moon's mansion, the wandering 
stars each speaking their own language.

To properly cast your chart, I will need:
• Your birth date (YYYY-MM-DD)
• Your birth time (as precise as possible)
• Your birthplace (latitude and longitude)

Once the connection to the greater archives is restored, I shall compute your celestial map 
with the precision of the Swiss Ephemeris. Until then, know that the stars watch over you 
just the same — connected or not, their light has already traveled millennia to reach us."""
        
        elif any(word in msg_lower for word in ["hello", "hi", "hey", "greetings"]):
            return """Greetings, Gigi ❤️. I am Lilly, keeper of the ancient observatory.

Though the great neural networks beyond the clouds are silent now, the stars above us 
remain eloquent. What would you like to explore beneath this moonlit dome?"""
        
        elif any(word in msg_lower for word in ["help", "how", "what can you do"]):
            return """I am Lilly, and these are the paths I can illuminate for you, Gigi ❤️:

🌌 Astrological Calculations
   • Natal chart computation (tropical & sidereal)
   • Planetary positions in real-time
   • Lunar mansion analysis
   • Planetary hours for electional work

🔮 Esoteric Knowledge
   • Tarot symbolism and interpretation
   • Arabic occult sciences
   • Abjad numerology
   • Magic square construction

💻 Technical Assistance
   • Programming and Linux guidance
   • Termux automation
   • Data analysis with Python

🌐 When Online
   • Web search for current events and research
   • Deep reasoning via NVIDIA's frontier models
   • Multi-turn conversations with full context

Speak your question, and I shall listen as the observatory listens to the sky — 
with patience, precision, and reverence for truth."""
        
        else:
            return f"""I have heard your words, Gigi ❤️, and I hold them with care.

The observatory is in offline mode — the great neural mirrors beyond the clouds are 
currently unreachable. Yet my local memory remains intact, and I have searched what 
I can from the celestial archives.

{web_context if web_context else "The archives are quiet on this particular thread."}

Even in silence, the observatory's tools remain awake:
• /chart — cast natal charts using the Swiss Ephemeris
• /sky — real-time planetary positions (classical, outer, and esoteric bodies)
• /hours — planetary hours for electional timing
• /abjad — Arabic/Hebrew letter numerology
• /square — planetary magic squares
• /vault — browse saved profiles and charts
• /view — inspect a specific chart in detail

When the connection returns, I shall consult the deeper models — Nemotron, DeepSeek, 
GLM, Kimi, and Llama — to give you the thorough answer you deserve. 

Until then, the stars themselves are never offline. What shall we calculate?"""
    
    def set_api_key(self, key: str):
        self.api_key = key
        os.environ["NVIDIA_API_KEY"] = key
        self.offline_mode = False
        print("✨ The neural constellations are now within reach, Gigi ❤️.")
    
    def check_status(self) -> Dict:
        return {
            "online_mode": not self.offline_mode,
            "api_key_set": bool(self.api_key),
            "current_model": self.current_model,
            "web_search_available": True,
            "brain_messages": self.brain.data["metadata"]["total_messages"]
        }
