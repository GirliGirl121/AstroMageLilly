"""
web_diary_db.py — Web diary database layer for AstroMage Dashboard.

SQLite-powered diary, tasks, dreams, bookmarks, favorites, search history.
Mirrors the desktop MagiJournal's database.py but as a lightweight
web-compatible module. Uses WAL mode for concurrent Flask access.

Gigi ❤️ — Your words, your dreams, your stars.
"""

import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "web_diary.db"


class DiaryDB:
    """SQLite database for web diary user data."""

    def __init__(self, db_path: str = str(DB_PATH)):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS diary_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    text TEXT NOT NULL,
                    done INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL DEFAULT (datetime('now'))
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dream_journal (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (datetime('now'))
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bookmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    note TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (datetime('now'))
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS favorites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    note TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (datetime('now'))
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (datetime('now'))
                );
            """)

            # Indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_diary_date ON diary_entries(date);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_date ON tasks(date);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_dreams_date ON dream_journal(date);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_bookmarks_date ON bookmarks(date);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_favorites_date ON favorites(date);")

    # ─── Diary ────────────────────────────────────────────────

    def add_diary(self, date: str, content: str) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO diary_entries (date, content) VALUES (?, ?);",
                (date, content)
            )
            return cursor.lastrowid

    def update_diary(self, entry_id: int, content: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE diary_entries SET content = ?, updated_at = datetime('now') WHERE id = ?;",
                (content, entry_id)
            )
            return cursor.rowcount > 0

    def get_diary(self, entry_id: int):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM diary_entries WHERE id = ?;", (entry_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def get_diary_by_date(self, date: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM diary_entries WHERE date = ? ORDER BY created_at DESC;", (date,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def delete_diary(self, entry_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM diary_entries WHERE id = ?;", (entry_id,))
            return cursor.rowcount > 0

    # ─── Tasks ────────────────────────────────────────────────

    def add_task(self, date: str, text: str) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO tasks (date, text) VALUES (?, ?);",
                (date, text)
            )
            return cursor.lastrowid

    def get_tasks(self, date: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE date = ? ORDER BY done ASC, id ASC;", (date,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def toggle_task(self, task_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE tasks SET done = CASE WHEN done THEN 0 ELSE 1 END WHERE id = ?;",
                (task_id,)
            )
            return cursor.rowcount > 0

    def delete_task(self, task_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?;", (task_id,))
            return cursor.rowcount > 0

    # ─── Dreams ───────────────────────────────────────────────

    def add_dream(self, date: str, content: str) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO dream_journal (date, content) VALUES (?, ?);",
                (date, content)
            )
            return cursor.lastrowid

    def update_dream(self, dream_id: int, content: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE dream_journal SET content = ? WHERE id = ?;",
                (content, dream_id)
            )
            return cursor.rowcount > 0

    def get_dreams_by_date(self, date: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM dream_journal WHERE date = ? ORDER BY created_at DESC;", (date,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def delete_dream(self, dream_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM dream_journal WHERE id = ?;", (dream_id,))
            return cursor.rowcount > 0

    # ─── Bookmarks ────────────────────────────────────────────

    def add_bookmark(self, date: str, note: str = "") -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO bookmarks (date, note) VALUES (?, ?);",
                (date, note or f"Bookmarked {date}")
            )
            return cursor.lastrowid

    def get_bookmarks(self, date: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM bookmarks WHERE date = ? ORDER BY created_at DESC;", (date,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def get_all_bookmarks(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM bookmarks ORDER BY date DESC;")
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def remove_bookmark(self, bookmark_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM bookmarks WHERE id = ?;", (bookmark_id,))
            return cursor.rowcount > 0

    # ─── Favorites ────────────────────────────────────────────

    def add_favorite(self, date: str, note: str = "") -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO favorites (date, note) VALUES (?, ?);",
                (date, note or f"Favorited {date}")
            )
            return cursor.lastrowid

    def get_favorites(self, date: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM favorites WHERE date = ? ORDER BY created_at DESC;", (date,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def get_all_favorites(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM favorites ORDER BY date DESC;")
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def remove_favorite(self, favorite_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM favorites WHERE id = ?;", (favorite_id,))
            return cursor.rowcount > 0

    # ─── Search History ───────────────────────────────────────

    def add_search_history(self, query: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO search_history (query) VALUES (?);",
                (query,)
            )

    def get_search_history(self, limit: int = 10):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT DISTINCT query FROM search_history ORDER BY id DESC LIMIT ?;",
                (limit,)
            )
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    # ─── Search ───────────────────────────────────────────────

    def search_entries(self, query: str):
        """Search across diary, tasks, and dreams. Returns grouped results."""
        like = f"%{query}%"
        results = {}

        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM diary_entries WHERE content LIKE ? ORDER BY date DESC;",
                (like,)
            )
            diary = [dict(r) for r in cursor.fetchall()]
            if diary:
                results['diary'] = diary

            cursor.execute(
                "SELECT * FROM tasks WHERE text LIKE ? ORDER BY date DESC;",
                (like,)
            )
            tasks = [dict(r) for r in cursor.fetchall()]
            if tasks:
                results['tasks'] = tasks

            cursor.execute(
                "SELECT * FROM dream_journal WHERE content LIKE ? ORDER BY date DESC;",
                (like,)
            )
            dreams = [dict(r) for r in cursor.fetchall()]
            if dreams:
                results['dreams'] = dreams

        return results


# ─── Global singleton ────────────────────────────────────────────────

_db_instance: DiaryDB | None = None


def get_diary_db() -> DiaryDB:
    global _db_instance
    if _db_instance is None:
        _db_instance = DiaryDB()
    return _db_instance
