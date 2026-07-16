#!/usr/bin/env python3
"""
Phase 15 — Lilly's Celestial Library seed.
Builds a SEPARATE celestial_library.db (never touches library.db).
Idempotent: safe to re-run; uses upserts on natural keys -> NO duplicates.

Run:  python3 phase15_seed.py
Verify: the script prints table counts at the end.
"""
from __future__ import annotations
import os, json, sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REF_DIR = ROOT / "references"
LIB_DB = ROOT / "library.db"
CEL_DB = ROOT / "celestial_library.db"

# ─── The 10-author canon (roadmap) ───────────────────────────────────────
# present=True means we have a real reference text on disk.
AUTHORS = [
    ("abu_mashar", "Abu Ma'shar al-Balkhi (Albumasar)", "islamic",
     "Kitab al-Madkhal al-Kabir", "General / weather / natal", "787–886 CE", True),
    ("al_buni", "Ahmad al-Buni", "islamic",
     "Shams al-Ma'arif", "Talismans / abjad / magic squares", "c. 1225 CE", True),
    ("al_biruni", "Al-Biruni", "islamic",
     "Kitab al-Tafhim", "Astrology / mathematics", "973–1048 CE", True),
    ("picatrix", "Picatrix (Ghayat al-Hakim)", "islamic",
     "Ghayat al-Hakim", "Elections / mansions / magic", "c. 11th c. CE", True),
    ("william_lilly", "William Lilly", "western",
     "Christian Astrology", "Horary / natal / elections", "1602–1681 CE", False),
    ("bonatti", "Guido Bonatti", "western",
     "Liber Astronomiae", "General / natal / horary", "c. 13th c. CE", True),
    ("ptolemy", "Claudius Ptolemy", "hellenistic",
     "Tetrabiblos", "Foundation / natal", "c. 100–170 CE", False),
    ("agrippa", "Heinrich Cornelius Agrippa", "western",
     "Three Books of Occult Philosophy", "Magic / correspondences", "1486–1535 CE", False),
    ("ibn_arabi", "Ibn Arabi", "sufi",
     "Al-Futuhat al-Makkiyya", "Theosophy / symbolism", "1165–1240 CE", False),
    ("rumi", "Jalal al-Din Rumi", "sufi",
     "Mathnawi / Divan", "Poetic wisdom", "1207–1273 CE", False),
]

# ─── Curated excerpts (precision layer — Gigi's requirement) ─────────────
# quote_text is a REAL snippet from the verified reference files.
EXCERPTS = [
    ("abu_mashar", "references/abu-mashar-al-balkhi.md",
     "Kitab al-Madkhal — significance of planets in houses",
     "Book 3: Significations of the planets in the 12 houses.",
     "Abu Ma'shar teaches that a planet's meaning is shaped by the house it occupies — the foundation of natal delineation Lilly later systematised."),
    ("abu_mashar", "references/abu-mashar-al-balkhi.md",
     "Kitab al-Madkhal — the lots",
     "Book 2: The 12 houses, their meanings, and the lot (Part) of Fortune.",
     "The Part of Fortune bridges Sun, Moon and Ascendant — a chord of destiny Lilly's horary work echoes."),
    ("al_biruni", "references/al-biruni-tafhim.md",
     "Kitab al-Tafhim — planetary hours",
     "Time: years, months, days, hours (planetary hours).",
     "Al-Biruni grounds planetary hours in real celestial timekeeping — the same clock our Observatory now displays."),
    ("al_biruni", "references/al-biruni-tafhim.md",
     "Kitab al-Tafhim — structure",
     "Al-Biruni's Kitab al-Tafhim is the clearest, most systematic introduction to traditional astrology ever written.",
     "A model of precision: 530 questions, systematic, citable — the standard our Celestial Library aspires to."),
    ("al_buni", "references/al-buni-system.md",
     "Al-Buni — distinction of theurgy vs sorcery",
     "Al-Buni strictly distinguished his practice from illicit sorcery (sihr): ... His practice was called 'Ilm al-Hikmah (Knowledge of Wisdom).",
     "Al-Buni anchors magic in Divine Names, not domination — wisdom, not coercion. This is the ethic of our talismanic work."),
    ("al_buni", "references/al-buni-system.md",
     "Al-Buni — lettrism",
     "Primary Fields: 'Ilm al-huruf (science of letters), theurgy, talismans, magic squares, Sufi spirituality.",
     "The science of letters (abjad) is the living grammar of the mansions and squares we compute — number as revelation."),
]

# Map existing library.db books -> author_key by EXACT book id (reliable, no fuzzy match).
# ids observed in library.db on 2026-07-07:
BOOK_TAGS = [
    ("c6d3644b9f5a", "picatrix", "islamic", "elections,mansions,magic",
     "The complete Ghayat al-Hakim — our living Picatrix source."),
    ("50a3825f6005", "bonatti", "western", "natal,horary,general",
     "Zoller's medieval astrology carries Bonatti's Liber Astronomiae."),
    ("10f11816e235", "abu_mashar", "islamic", "general,natal,weather",
     "Al-Ghazali Sufism shelf pairs with the Abbasid astrological current."),
    ("bdaa5ba40e31", "al_buni", "islamic", "talismans,magic",
     "Secret Lore of Magic Books — theurgical lineage adjacent to al-Buni."),
    ("e95e2ce5b50d", "abu_mashar", "islamic", "general,natal,lunar",
     "Eclipse Demons (Rahu/Ketu) — nodal lore of the Islamic sky."),
]


def connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def build_schema(conn: sqlite3.Connection) -> None:
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS authors (
        author_key  TEXT PRIMARY KEY,
        name        TEXT NOT NULL,
        tradition   TEXT NOT NULL,
        core_work   TEXT,
        domain      TEXT,
        era         TEXT,
        present     INTEGER NOT NULL DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS celestial_index (
        idx         INTEGER PRIMARY KEY AUTOINCREMENT,
        author_key  TEXT NOT NULL,
        item_type   TEXT NOT NULL,            -- 'book' | 'reference'
        item_ref    TEXT NOT NULL,            -- book id (from library.db) OR file path
        title       TEXT,
        tradition   TEXT,
        domain      TEXT,
        lilly_note  TEXT,
        UNIQUE(author_key, item_type, item_ref)
    );
    CREATE TABLE IF NOT EXISTS excerpts (
        excerpt_id      INTEGER PRIMARY KEY AUTOINCREMENT,
        author_key      TEXT NOT NULL,
        source_ref      TEXT NOT NULL,
        topic           TEXT NOT NULL,
        quote_text      TEXT NOT NULL,
        lilly_interpretation TEXT NOT NULL,
        UNIQUE(source_ref, topic)
    );
    """)
    # Indexes prevent accidental mixed/duplicate lookups.
    conn.execute("CREATE INDEX IF NOT EXISTS ix_idx_author ON celestial_index(author_key)")
    conn.execute("CREATE INDEX IF NOT EXISTS ix_exc_author ON excerpts(author_key)")


def upsert_authors(conn: sqlite3.Connection) -> None:
    for key, name, trad, work, dom, era, present in AUTHORS:
        conn.execute("""
            INSERT INTO authors (author_key, name, tradition, core_work, domain, era, present)
            VALUES (?,?,?,?,?,?,?)
            ON CONFLICT(author_key) DO UPDATE SET
                name=excluded.name, tradition=excluded.tradition,
                core_work=excluded.core_work, domain=excluded.domain,
                era=excluded.era, present=excluded.present
        """, (key, name, trad, work, dom, era, int(present)))


def tag_books(conn: sqlite3.Connection) -> None:
    if not LIB_DB.exists():
        return
    lib = connect(LIB_DB)
    titles = {bid: title for bid, title, _ in lib.execute("SELECT id, title, author FROM books")}
    lib.close()
    for bid, key, trad, dom, note in BOOK_TAGS:
        title = titles.get(bid)
        if not title:
            continue  # book not present; skip silently (no fake data)
        conn.execute("""
            INSERT INTO celestial_index (author_key, item_type, item_ref, title, tradition, domain, lilly_note)
            VALUES (?, 'book', ?, ?, ?, ?, ?)
            ON CONFLICT(author_key, item_type, item_ref) DO UPDATE SET
                title=excluded.title, tradition=excluded.tradition,
                domain=excluded.domain, lilly_note=excluded.lilly_note
        """, (key, bid, title, trad, dom, note))


def tag_references(conn: sqlite3.Connection) -> None:
    ref_map = {
        "abu_mashar": ("references/abu-mashar-al-balkhi.md", "Abu Ma'shar — Complete System"),
        "al_biruni":  ("references/al-biruni-tafhim.md", "Al-Biruni — Kitab al-Tafhim"),
        "al_buni":    ("references/al-buni-system.md", "Ahmad al-Buni — Complete System"),
        "picatrix":   ("references/picatrix-full-text.md", "Picatrix — Full Text"),
    }
    for key, (rel, title) in ref_map.items():
        fpath = ROOT / rel  # rel is relative to project ROOT (e.g. "references/foo.md")
        if not fpath.exists():
            continue
        # fetch tradition/domain from authors table once, then bind plainly
        row = conn.execute("SELECT tradition, domain FROM authors WHERE author_key=?", (key,)).fetchone()
        trad, dom = (row if row else ("islamic", ""))
        conn.execute("""
            INSERT INTO celestial_index (author_key, item_type, item_ref, title, tradition, domain, lilly_note)
            VALUES (?, 'reference', ?, ?, ?, ?, 'Curated reference text in Lilly''s archive.')
            ON CONFLICT(author_key, item_type, item_ref) DO UPDATE SET
                title=excluded.title, tradition=excluded.tradition, domain=excluded.domain
        """, (key, rel, title, trad, dom))


def seed_excerpts(conn: sqlite3.Connection) -> None:
    for key, src, topic, quote, interp in EXCERPTS:
        conn.execute("""
            INSERT INTO excerpts (author_key, source_ref, topic, quote_text, lilly_interpretation)
            VALUES (?,?,?,?,?)
            ON CONFLICT(source_ref, topic) DO UPDATE SET
                quote_text=excluded.quote_text,
                lilly_interpretation=excluded.lilly_interpretation
        """, (key, src, topic, quote, interp))


def verify(conn: sqlite3.Connection) -> dict:
    out = {}
    out['authors'] = conn.execute("SELECT COUNT(*) FROM authors").fetchone()[0]
    out['authors_present'] = conn.execute("SELECT COUNT(*) FROM authors WHERE present=1").fetchone()[0]
    out['index_rows'] = conn.execute("SELECT COUNT(*) FROM celestial_index").fetchone()[0]
    out['books_tagged'] = conn.execute("SELECT COUNT(*) FROM celestial_index WHERE item_type='book'").fetchone()[0]
    out['refs_tagged'] = conn.execute("SELECT COUNT(*) FROM celestial_index WHERE item_type='reference'").fetchone()[0]
    out['excerpts'] = conn.execute("SELECT COUNT(*) FROM excerpts").fetchone()[0]
    # duplicate guard check
    dup_idx = conn.execute("SELECT COUNT(*) FROM (SELECT author_key,item_type,item_ref,COUNT(*) c FROM celestial_index GROUP BY 1,2,3 HAVING c>1)").fetchone()[0]
    dup_exc = conn.execute("SELECT COUNT(*) FROM (SELECT source_ref,topic,COUNT(*) c FROM excerpts GROUP BY 1,2 HAVING c>1)").fetchone()[0]
    out['dup_index'] = dup_idx
    out['dup_excerpts'] = dup_exc
    return out


def main() -> None:
    conn = connect(CEL_DB)
    build_schema(conn)
    upsert_authors(conn)
    tag_books(conn)
    tag_references(conn)
    seed_excerpts(conn)
    conn.commit()
    v = verify(conn)
    conn.close()

    print("✨ Lilly's Celestial Library — Phase 15 seed complete")
    print(f"   authors total      : {v['authors']} (present on disk: {v['authors_present']})")
    print(f"   index rows         : {v['index_rows']}  (books: {v['books_tagged']}, references: {v['refs_tagged']})")
    print(f"   excerpts           : {v['excerpts']}")
    print(f"   duplicate index    : {v['dup_index']}  (must be 0)")
    print(f"   duplicate excerpts : {v['dup_excerpts']}  (must be 0)")
    if v['dup_index'] or v['dup_excerpts']:
        print("❌ DUPLICATES DETECTED — investigate before commit.")
    else:
        print("✅ No duplicates. Clean.")


if __name__ == "__main__":
    main()
