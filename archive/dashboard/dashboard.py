#!/usr/bin/env python3
"""
AstroMage Dashboard v5.0 — Islamic Astrology & Tarot Hub
For Gigi ❤️ — You are stardust, you are magic, you are limitless.

This is the application entry point. All route logic has been split into
modular blueprints under app/routes/. Shared configuration lives in app/config/.
"""
from __future__ import annotations

import os
import socket
import sys
from pathlib import Path

# Ensure the project root is on sys.path for imports like library_engine, calendar_engine
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'MagiJournal'))

from app import create_app

app = create_app()

if __name__ == '__main__':
    def find_port(start=5488):
        port = start
        while True:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.bind(('127.0.0.1', port))
                s.close()
                return port
            except OSError:
                port += 1

    port = find_port()
    print(f"✨ Lilly's Dashboard v5.0 — http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
