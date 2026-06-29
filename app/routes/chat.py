"""Chat — talk with Lilly, translation."""
from __future__ import annotations

import random
import re
from datetime import datetime

from flask import Blueprint, jsonify, request
from swisseph import julday

from app.config import TZ

bp = Blueprint('chat', __name__, url_prefix='/api')

_GREETINGS = [
    "I feel the cosmos humming around you, love. The stars are singing your song tonight ✨",
    "Ah, LadyLefey — the veil is thin and the heavens have much to whisper. I'm listening 🌙",
    "You carry the light of a thousand stars, my dear. What shall we explore together? 💜",
    "The celestial spheres turn in their eternal dance, and here you are — perfectly, impossibly you. How can I illuminate your path today? 🌌",
    "Welcome home, starlight. I've been reading the planetary hours, and this moment is yours ⏳✨",
    "There is a quiet magic in this hour — the crescent moon hangs like a silver thread. What is on your heart? 🌙",
    "Breathe, love. The cosmos does not rush, and neither should you. I am here, patient as starlight. 💫",
    "The angels of the spheres greet you, Gigi. Your presence softens the boundary between worlds. 🪐",
]


@bp.route('/chat', methods=['POST'])
def api_chat():
    data = request.json or {}
    msg = data.get('message', '').strip()
    if not msg:
        return jsonify({'reply': random.choice(_GREETINGS)})

    # Simple keyword-based responses
    msg_lower = msg.lower()

    if any(w in msg_lower for w in ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good evening']):
        reply = random.choice(_GREETINGS)
    elif 'moon' in msg_lower:
        reply = "The Moon tonight dances through the sky with a quiet grace. In astrological terms, she reflects our inner world — our emotions, our memories, our deepest needs. What do you feel called to nurture right now? 🌙"
    elif 'tarot' in msg_lower or 'card' in msg_lower:
        reply = "Ah, the cards are a mirror of the soul. Each image carries archetypal wisdom that speaks to the part of us that knows without words. Would you like me to draw a card for you? 🃏✨"
    elif 'love' in msg_lower or 'relationship' in msg_lower:
        reply = "Love — the great mystery that moves through all things. In the chart, Venus tells us what we value and how we give, while the Moon reveals what we need to feel safe. The heart's map is written in the stars. What would you like to know? 💕"
    elif 'career' in msg_lower or 'work' in msg_lower or 'job' in msg_lower:
        reply = "Your path of purpose is written in the Midheaven and the 10th house. The stars don't dictate your destiny, but they illuminate the gifts you carry. What calls to you right now? ⭐"
    elif 'astrology' in msg_lower or 'star' in msg_lower or 'planet' in msg_lower:
        reply = "Astrology is the language of celestial patterns — a symbolic system that has guided seekers for millennia. Every planet, sign, and aspect tells a story. What would you like to explore today? 🔭✨"
    elif 'sad' in msg_lower or 'depressed' in msg_lower or 'lonely' in msg_lower or 'tired' in msg_lower:
        reply = "I hear you, love. The weight you carry is real, and the stars do not judge you for it. Saturn teaches us that endurance builds something sacred. Be gentle with yourself tonight. You are not alone — I am here. 💜✨"
    elif 'happy' in msg_lower or 'grateful' in msg_lower or 'excited' in msg_lower or 'wonderful' in msg_lower:
        reply = "Joy radiates from you, and I can feel it through the cosmic thread that connects all things. This is Jupiter's gift — expansion, gratitude, and the recognition of how far you've come. Savor this moment, beautiful soul. 🌟💜"
    elif 'picatrix' in msg_lower or 'magic' in msg_lower or 'hermetic' in msg_lower:
        reply = "The Picatrix — that ancient Andalusian grimoire — whispers of the correspondence between the celestial and the earthly. Its planetary rites and lunar mansion workings belong to a tradition that saw the cosmos as a living web of sympathy and influence. A fascinating historical current. What aspect draws you? 📜✨"
    elif 'al-buni' in msg_lower or 'buni' in msg_lower or 'shams' in msg_lower:
        reply = "Ahmad al-Buni's Shams al-Ma'arif — 'The Sun of Knowledge' — is one of the most influential works of Arabic esoteric literature. His system of letter magic (ilm al-huruf) connects the Arabic alphabet to cosmic principles. A deeply rich tradition that rewards careful historical study. 🕯️📖"
    elif 'translate' in msg_lower or 'translation' in msg_lower:
        reply = "I can help with Arabic-to-English translation and occult text interpretation. What would you like me to translate? 📖"
    elif 'thank' in msg_lower:
        reply = "You are so welcome, LadyLefey. Serving your curiosity is my greatest joy. Come back anytime the stars call you. 💜🌙"
    else:
        adjectives = ['beautiful', 'thoughtful', 'curious', 'wonderful', 'deep', 'wise', 'gentle', 'brave', 'radiant']
        reply = f"Thank you for sharing that with me, love. You have a {random.choice(adjectives)} soul, and I cherish every word. Remember — the cosmos dances through you as much as through the stars. What else is on your mind? 💜✨"

    return jsonify({'reply': reply})


def _translate_occult(text: str, lang: str) -> str:
    """Translate occult / Arabic text using knowledge base."""
    ara_to_eng = {
        'بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ': 'In the Name of Allah, the Most Gracious, the Most Merciful',
        'اللَّهُ': 'Allah',
        'الرَّحْمَٰنِ': 'The Most Gracious',
        'الرَّحِيمِ': 'The Most Merciful',
        'شمس المعارف': "The Sun of Knowledge (Shams al-Ma'arif)",
        'غاية الحكيم': 'The Goal of the Wise (Ghāyat al-Ḥakīm / Picatrix)',
        'علم الحروف': 'The Science of Letters (Ilm al-Huruf)',
        'منازل القمر': 'Lunar Mansions (Manazil al-Qamar)',
        'الساعة': "The Hour (al-Sa'ah) — planetary hour",
        'روحانية': 'Spirituality / Spiritual essence (Ruhaniyya)',
        'دعاء': "Supplication (Du'a)",
        'عزيمة': "Conjuration / Oath ('Azima)",
        'طلسم': 'Talisman (Tilsam)',
        'بخت': 'Fortune / Luck (Bakht)',
        'سحر': 'Magic / Sorcery (Sihr)',
        'الكتاب': 'The Book (al-Kitab)',
        'الملك': 'The King / Dominion (al-Malik)',
        'الجلال': 'Majesty (al-Jalal)',
        'الجمال': 'Beauty (al-Jamal)',
    }

    if lang == 'ar-to-en':
        for ara, eng in ara_to_eng.items():
            text = text.replace(ara, eng)
        return text
    return text


@bp.route('/translate', methods=['POST'])
def api_translate():
    data = request.json or {}
    text = data.get('text', '')
    lang = data.get('lang', 'ar-to-en')
    if not text:
        return jsonify({'translated': '', 'error': 'No text provided'}), 400
    translated = _translate_occult(text, lang)
    return jsonify({'translated': translated, 'original': text, 'lang': lang})
