"""Simply Astrology — knowledge sections API."""
from __future__ import annotations

from flask import Blueprint, jsonify

from simply_data import KNOWLEDGE_SECTIONS, SECTION_NAMES

bp = Blueprint('simply', __name__, url_prefix='/api/simply')


@bp.route('/sections')
def api_simply_sections():
    return jsonify(SECTION_NAMES)


@bp.route('/section/<int:index>')
def api_simply_section(index: int):
    if index < 0 or index >= len(SECTION_NAMES):
        return jsonify({'error': 'Section index out of range'}), 404
    name = SECTION_NAMES[index]
    cards = KNOWLEDGE_SECTIONS.get(name, [])
    result = [{'heading': h, 'body': b} for h, b in cards]
    return jsonify({'section': name, 'cards': result})


@bp.route('/all')
def api_simply_all():
    result = []
    for name in SECTION_NAMES:
        cards = KNOWLEDGE_SECTIONS.get(name, [])
        section = {'section': name, 'cards': []}
        for heading, body in cards:
            section['cards'].append({'heading': heading, 'body': body})
        result.append(section)
    return jsonify(result)
