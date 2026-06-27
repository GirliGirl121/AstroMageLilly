"""
database.py — SQLite database layer for MagiJournal user data.

Handles all CRUD operations for diary entries, tasks, dreams, bookmarks,
favorites, and search history. Uses WAL mode for concurrent access.

User data is stored in user_data.db, separate from reference/source data
which lives in picatrix_calendar/picatrix_calendar.db.
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Tuple, Any
from contextlib import contextmanager


DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_data.db")


class Database:
    """SQLite database layer for MagiJournal user data."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self):
        """Context manager for database connections with WAL mode."""
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
        """Initialize database schema."""
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

            # Indexes for common queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_diary_date ON diary_entries(date);
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_tasks_date ON tasks(date);
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_dreams_date ON dream_journal(date);
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_bookmarks_date ON bookmarks(date);
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_favorites_date ON favorites(date);
            """)

    # ─── Diary Entries ───────────────────────────────────────────────

    def add_diary(self, date: str, content: str) -> int:
        """Add a new diary entry. Returns the new row id."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO diary_entries (date, content) VALUES (?, ?);",
                (date, content)
            )
            return cursor.lastrowid

    def update_diary(self, entry_id: int, content: str) -> bool:
        """Update an existing diary entry's content. Returns True if row was updated."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE diary_entries SET content = ?, updated_at = datetime('now') WHERE id = ?;",
                (content, entry_id)
            )
            return cursor.rowcount > 0

    def get_diary(self, entry_id: int) -> Optional[sqlite3.Row]:
        """Get a single diary entry by id, or None if not found."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM diary_entries WHERE id = ?;",
                (entry_id,)
            )
            return cursor.fetchone()

    def get_diary_by_date(self, date: str) -> List[sqlite3.Row]:
        """Get all diary entries for a specific date."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM diary_entries WHERE date = ? ORDER BY created_at;",
                (date,)
            )
            return cursor.fetchall()

    def get_all_diary(self) -> List[sqlite3.Row]:
        """Get all diary entries ordered by date descending."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM diary_entries ORDER BY date DESC, created_at DESC;"
            )
            return cursor.fetchall()

    def delete_diary(self, entry_id: int) -> bool:
        """Delete a diary entry. Returns True if row was deleted."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM diary_entries WHERE id = ?;",
                (entry_id,)
            )
            return cursor.rowcount > 0

    # ─── Tasks ───────────────────────────────────────────────────────

    def add_task(self, date: str, text: str) -> int:
        """Add a new task. Returns the new row id."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO tasks (date, text) VALUES (?, ?);",
                (date, text)
            )
            return cursor.lastrowid

    def toggle_task(self, task_id: int) -> bool:
        """Toggle task done status. Returns True if row was updated."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE tasks SET done = CASE WHEN done = 0 THEN 1 ELSE 0 END WHERE id = ?;",
                (task_id,)
            )
            return cursor.rowcount > 0

    def get_tasks(self, date: str) -> List[sqlite3.Row]:
        """Get all tasks for a specific date."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM tasks WHERE date = ? ORDER BY created_at;",
                (date,)
            )
            return cursor.fetchall()

    def get_all_tasks(self) -> List[sqlite3.Row]:
        """Get all tasks ordered by date."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM tasks ORDER BY date DESC, created_at;"
            )
            return cursor.fetchall()

    def delete_task(self, task_id: int) -> bool:
        """Delete a task. Returns True if deleted."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?;", (task_id,))
            return cursor.rowcount > 0

    def update_task(self, task_id: int, text: str) -> bool:
        """Update task text. Returns True if updated."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE tasks SET text = ? WHERE id = ?;",
                (text, task_id)
            )
            return cursor.rowcount > 0

    # ─── Dream Journal ───────────────────────────────────────────────

    def add_dream(self, date: str, content: str) -> int:
        """Add a dream journal entry. Returns the new row id."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO dream_journal (date, content) VALUES (?, ?);",
                (date, content)
            )
            return cursor.lastrowid

    def get_dream(self, dream_id: int) -> Optional[sqlite3.Row]:
        """Get a single dream entry by id, or None if not found."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM dream_journal WHERE id = ?;",
                (dream_id,)
            )
            return cursor.fetchone()

    def get_dreams_by_date(self, date: str) -> List[sqlite3.Row]:
        """Get all dream entries for a specific date."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM dream_journal WHERE date = ? ORDER BY created_at;",
                (date,)
            )
            return cursor.fetchall()

    def get_all_dreams(self) -> List[sqlite3.Row]:
        """Get all dream entries ordered by date descending."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM dream_journal ORDER BY date DESC, created_at DESC;"
            )
            return cursor.fetchall()

    def update_dream(self, dream_id: int, content: str) -> bool:
        """Update a dream entry. Returns True if updated."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE dream_journal SET content = ? WHERE id = ?;",
                (content, dream_id)
            )
            return cursor.rowcount > 0

    def delete_dream(self, dream_id: int) -> bool:
        """Delete a dream entry. Returns True if deleted."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM dream_journal WHERE id = ?;", (dream_id,))
            return cursor.rowcount > 0

    # ─── Bookmarks ───────────────────────────────────────────────────

    def add_bookmark(self, date: str, note: str) -> int:
        """Add a new bookmark. Returns the new row id."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO bookmarks (date, note) VALUES (?, ?);",
                (date, note)
            )
            return cursor.lastrowid

    def remove_bookmark(self, bookmark_id: int) -> bool:
        """Remove a bookmark by id. Returns True if deleted."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM bookmarks WHERE id = ?;",
                (bookmark_id,)
            )
            return cursor.rowcount > 0

    def get_bookmarks(self, date: str) -> List[sqlite3.Row]:
        """Get all bookmarks for a specific date."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM bookmarks WHERE date = ? ORDER BY created_at;",
                (date,)
            )
            return cursor.fetchall()

    def get_all_bookmarks(self) -> List[sqlite3.Row]:
        """Get all bookmarks ordered by date descending."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM bookmarks ORDER BY date DESC, created_at DESC;"
            )
            return cursor.fetchall()

    def update_bookmark(self, bookmark_id: int, note: str) -> bool:
        """Update a bookmark's note. Returns True if updated."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE bookmarks SET note = ? WHERE id = ?;",
                (note, bookmark_id)
            )
            return cursor.rowcount > 0

    # ─── Favorites ───────────────────────────────────────────────────

    def add_favorite(self, date: str, note: str) -> int:
        """Add a new favorite. Returns the new row id."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO favorites (date, note) VALUES (?, ?);",
                (date, note)
            )
            return cursor.lastrowid

    def remove_favorite(self, favorite_id: int) -> bool:
        """Remove a favorite by id. Returns True if deleted."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM favorites WHERE id = ?;",
                (favorite_id,)
            )
            return cursor.rowcount > 0

    def get_favorites(self, date: str) -> List[sqlite3.Row]:
        """Get all favorites for a specific date."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM favorites WHERE date = ? ORDER BY created_at;",
                (date,)
            )
            return cursor.fetchall()

    def get_all_favorites(self) -> List[sqlite3.Row]:
        """Get all favorites ordered by date descending."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM favorites ORDER BY date DESC, created_at DESC;"
            )
            return cursor.fetchall()

    def update_favorite(self, favorite_id: int, note: str) -> bool:
        """Update a favorite's note. Returns True if updated."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE favorites SET note = ? WHERE id = ?;",
                (note, favorite_id)
            )
            return cursor.rowcount > 0

    # ─── Search History ──────────────────────────────────────────────

    def add_search_history(self, query: str) -> int:
        """Record a search query. Returns the new row id."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO search_history (query) VALUES (?);",
                (query,)
            )
            return cursor.lastrowid

    def get_search_history(self, limit: int = 50) -> List[sqlite3.Row]:
        """Get recent search history entries."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM search_history ORDER BY created_at DESC LIMIT ?;",
                (limit,)
            )
            return cursor.fetchall()

    def clear_search_history(self) -> int:
        """Clear all search history. Returns number of rows deleted."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM search_history;")
            return cursor.rowcount

    # ─── Search ──────────────────────────────────────────────────────

    def search_entries(self, keyword: str) -> dict:
        """
        Search across diary entries, tasks, dreams, bookmarks, and favorites.
        Returns a dict with keys: diary, tasks, dreams, bookmarks, favorites.
        Each value is a list of matching rows.
        """
        like_pattern = f"%{keyword}%"
        results = {}

        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM diary_entries WHERE content LIKE ? ORDER BY date DESC;",
                (like_pattern,)
            )
            results["diary"] = cursor.fetchall()

            cursor.execute(
                "SELECT * FROM tasks WHERE text LIKE ? ORDER BY date DESC;",
                (like_pattern,)
            )
            results["tasks"] = cursor.fetchall()

            cursor.execute(
                "SELECT * FROM dream_journal WHERE content LIKE ? ORDER BY date DESC;",
                (like_pattern,)
            )
            results["dreams"] = cursor.fetchall()

            cursor.execute(
                "SELECT * FROM bookmarks WHERE note LIKE ? ORDER BY date DESC;",
                (like_pattern,)
            )
            results["bookmarks"] = cursor.fetchall()

            cursor.execute(
                "SELECT * FROM favorites WHERE note LIKE ? ORDER BY date DESC;",
                (like_pattern,)
            )
            results["favorites"] = cursor.fetchall()

        return results

    # ─── Utility ─────────────────────────────────────────────────────

    def close(self):
        """No-op for context-managed connections; provided for API symmetry."""
        pass

    def __repr__(self):
        return f"Database(db_path={self.db_path!r})"


# ─── Module-level convenience ────────────────────────────────────────

_instance: Optional[Database] = None


def get_database(db_path: str = DB_PATH) -> Database:
    """Get or create a module-level Database instance."""
    global _instance
    if _instance is None or _instance.db_path != db_path:
        _instance = Database(db_path)
    return _instance
