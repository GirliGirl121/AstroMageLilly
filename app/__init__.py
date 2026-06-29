"""AstroMage — Flask application factory.

All blueprint route modules are registered here.
dashboard.py imports and runs this factory.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import swisseph as swe
from flask import Flask

swe.set_ephe_path(os.path.expanduser('~/.swisseph'))

ROOT = Path(__file__).resolve().parent.parent
# MagiJournal contains calendar_engine.py and other shared modules
sys.path.insert(0, str(ROOT / 'MagiJournal'))


def create_app(testing=False) -> Flask:
    """Create and configure the AstroMage Flask application."""
    app = Flask(__name__,
                template_folder=str(ROOT / 'templates'),
                static_folder=str(ROOT / 'static'))
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    if testing:
        app.config['TESTING'] = True

    # ─── Import and register blueprints ────────────────────────────────
    # Each blueprint lives in app/routes/ and handles a domain of endpoints.

    from app.routes.home import bp as home_bp
    from app.routes.simply import bp as simply_bp
    from app.routes.tarot import bp as tarot_bp
    from app.routes.library import bp as library_bp
    from app.routes.quran_hadith import bp as quran_hadith_bp
    from app.routes.diary import bp as diary_bp
    from app.routes.natal import bp as natal_bp
    from app.routes.chat import bp as chat_bp
    from app.routes.horoscope import bp as horoscope_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(simply_bp)
    app.register_blueprint(tarot_bp)
    app.register_blueprint(library_bp)
    app.register_blueprint(quran_hadith_bp)
    app.register_blueprint(diary_bp)
    app.register_blueprint(natal_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(horoscope_bp)

    # ─── Initialize library DB on startup ──────────────────────────────
    try:
        from library_engine import init_db
        init_db()
    except Exception:
        pass  # Graceful if DB unavailable

    return app
