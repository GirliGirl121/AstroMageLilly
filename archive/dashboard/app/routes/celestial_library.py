"""Phase 15 — Celestial Library index API (read-only over celestial_library.db)."""
from __future__ import annotations

import sqlite3
from pathlib import Path

from flask import Blueprint, jsonify

bp = Blueprint('celestial_library', __name__, url_prefix='/api/celestial')

ROOT = Path(__file__).resolve().parent.parent.parent
DB = ROOT / 'celestial_library.db'


def _conn():
    return sqlite3.connect(str(DB))


@bp.route('/library')
def api_celestial_library():
    if not DB.exists():
        return jsonify({'error': 'celestial_library.db not built', 'authors': [], 'index': []}), 404
    conn = _conn()
    authors = [dict(zip(['author_key', 'name', 'tradition', 'core_work', 'domain', 'era', 'present'], r))
               for r in conn.execute(
        "SELECT author_key, name, tradition, core_work, domain, era, present FROM authors ORDER BY name")]
    index = [dict(zip(['author_key', 'item_type', 'item_ref', 'title', 'tradition', 'domain'], r))
              for r in conn.execute(
        "SELECT author_key, item_type, item_ref, title, tradition, domain FROM celestial_index ORDER BY author_key, item_type")]
    conn.close()
    return jsonify({'authors': authors, 'index': index})


@bp.route('/preview')
def celestial_preview():
    """Serve the standalone preview page (Option B) at a clean, unambiguous path."""
    from flask import send_from_directory
    return send_from_directory(ROOT, 'celestial_library_preview.html')
