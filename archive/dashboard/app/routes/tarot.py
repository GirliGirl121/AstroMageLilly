"""Tarot — daily card and readings."""
from __future__ import annotations

import random

from flask import Blueprint, jsonify

from app.config import TAROT_DATA

bp = Blueprint('tarot', __name__, url_prefix='/api/tarot')

SUIT_EMOJI = {'wands': '🪄', 'cups': '🏆', 'swords': '🗡️', 'pentacles': '🪙', 'major': '⭐'}


@bp.route('/daily')
def api_tarot_daily():
    if not TAROT_DATA:
        return jsonify({'name': 'The Fool', 'keywords': ['beginnings', 'innocence']})
    cards = TAROT_DATA.get('cards', [])
    if not cards:
        return jsonify({'name': 'The Fool', 'keywords': ['beginnings', 'innocence']})
    card = random.choice(cards)
    return jsonify({
        'name': card.get('name', 'Unknown'),
        'suit': card.get('suit', ''),
        'keywords': card.get('keywords', []),
        'upright': card.get('upright_meaning', '') or card.get('meaning_up', ''),
        'reversed': card.get('reversed_meaning', '') or card.get('meaning_rev', ''),
    })


@bp.route('/draw')
def api_tarot_draw():
    """Draw a specified number of cards for a reading."""
    from flask import request
    count = min(int(request.args.get('count', 1)), 78)
    if not TAROT_DATA:
        return jsonify({'cards': [{'name': 'The Fool'}], 'count': count})
    cards = TAROT_DATA.get('cards', [])
    drawn = random.sample(cards, min(count, len(cards)))
    result = []
    for card in drawn:
        result.append({
            'name': card.get('name', 'Unknown'),
            'suit': card.get('suit', ''),
            'keywords': card.get('keywords', []),
            'upright': card.get('upright_meaning', '') or card.get('meaning_up', ''),
            'reversed': card.get('reversed_meaning', '') or card.get('meaning_rev', ''),
            'emoji': SUIT_EMOJI.get(card.get('suit', '').lower(), '🃏'),
        })
    return jsonify({'cards': result, 'count': len(result)})
