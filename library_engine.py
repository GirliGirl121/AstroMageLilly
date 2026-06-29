#!/usr/bin/env python3
"""
AstroMage Library Engine — PDF Processing & Digital Library System
For Gigi ❤️ — Handles PDF text extraction, OCR, indexing, and search.
"""
from __future__ import annotations

import fitz  # PyMuPDF
import json
import os
import re
import sqlite3
import hashlib
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, List, Any

# ─── Configuration ──────────────────────────────────────────────────────────
LIBRARY_DB = Path(__file__).resolve().parent / "library.db"
PDF_SOURCE_DIR = Path.home() / "Documents" / "magewisdom"
PROCESSED_DIR = Path(__file__).resolve().parent / "library_processed"
OCR_DPI = 300
MIN_TEXT_THRESHOLD = 0.3  # If less than 30% of pages have text, use OCR

# ─── Database Setup ─────────────────────────────────────────────────────────
def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(LIBRARY_DB))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS books (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT DEFAULT 'Unknown',
            language TEXT DEFAULT 'en',
            subject TEXT DEFAULT '',
            keywords TEXT DEFAULT '',
            page_count INTEGER DEFAULT 0,
            file_size INTEGER DEFAULT 0,
            date_imported TEXT NOT NULL,
            source_path TEXT DEFAULT '',
            cover_image TEXT DEFAULT '',
            status TEXT DEFAULT 'processing',
            ocr_used INTEGER DEFAULT 0,
            text_extracted INTEGER DEFAULT 0
        );
        
        CREATE TABLE IF NOT EXISTS pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id TEXT NOT NULL,
            page_number INTEGER NOT NULL,
            content TEXT DEFAULT '',
            is_ocr INTEGER DEFAULT 0,
            ocr_confidence REAL DEFAULT 0.0,
            has_text INTEGER DEFAULT 0,
            FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
            UNIQUE(book_id, page_number)
        );
        
        CREATE TABLE IF NOT EXISTS bookmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id TEXT NOT NULL,
            page_number INTEGER NOT NULL,
            title TEXT DEFAULT '',
            color TEXT DEFAULT '#d4af37',
            date_created TEXT NOT NULL,
            FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
        );
        
        CREATE TABLE IF NOT EXISTS highlights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id TEXT NOT NULL,
            page_number INTEGER NOT NULL,
            start_offset INTEGER DEFAULT 0,
            end_offset INTEGER DEFAULT 0,
            selected_text TEXT DEFAULT '',
            color TEXT DEFAULT '#ffd700',
            note TEXT DEFAULT '',
            date_created TEXT NOT NULL,
            FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
        );
        
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id TEXT NOT NULL,
            page_number INTEGER NOT NULL,
            content TEXT DEFAULT '',
            date_created TEXT NOT NULL,
            date_modified TEXT NOT NULL,
            FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
        );
        
        CREATE TABLE IF NOT EXISTS reading_progress (
            book_id TEXT PRIMARY KEY,
            current_page INTEGER DEFAULT 1,
            progress_pct REAL DEFAULT 0.0,
            last_read TEXT NOT NULL,
            FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
        );
        
        CREATE VIRTUAL TABLE IF NOT EXISTS pages_fts USING fts5(
            content, content='pages', content_rowid='id'
        );
        
        CREATE INDEX IF NOT EXISTS idx_pages_book ON pages(book_id);
        CREATE INDEX IF NOT EXISTS idx_bookmarks_book ON bookmarks(book_id);
        CREATE INDEX IF NOT EXISTS idx_highlights_book ON highlights(book_id);
    """)
    conn.commit()
    conn.close()

# ─── PDF Text Extraction ────────────────────────────────────────────────────
def extract_text_from_pdf(pdf_path: str) -> Dict[str, Any]:
    """
    Extract text from PDF. Uses PyMuPDF first, falls back to pdftotext (Poppler)
    for PDFs with custom font encodings that PyMuPDF can't decode.
    """
    doc = fitz.open(pdf_path)
    result = {
        "pages": [],
        "metadata": {},
        "needs_ocr": False,
        "total_pages": len(doc),
        "text_pages": 0,
    }
    
    # Extract metadata
    meta = doc.metadata
    result["metadata"] = {
        "title": meta.get("title", ""),
        "author": meta.get("author", ""),
        "subject": meta.get("subject", ""),
        "creator": meta.get("creator", ""),
        "producer": meta.get("producer", ""),
        "keywords": meta.get("keywords", ""),
    }
    
    # Extract text from each page using PyMuPDF first
    pages_with_text = 0
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text").strip()
        has_text = len(text) > 20
        if has_text:
            pages_with_text += 1
        result["pages"].append({
            "page_number": page_num + 1,
            "content": text,
            "has_text": has_text,
        })
    
    result["text_pages"] = pages_with_text
    
    # If PyMuPDF extracted little text, try pdftotext as fallback
    if pages_with_text / max(len(doc), 1) < MIN_TEXT_THRESHOLD:
        try:
            import subprocess
            for page_num in range(len(doc)):
                if not result["pages"][page_num]["has_text"]:
                    # Use pdftotext for this specific page
                    proc = subprocess.run(
                        ["pdftotext", "-f", str(page_num + 1), "-l", str(page_num + 1),
                         "-layout", pdf_path, "-"],
                        capture_output=True, text=True, timeout=30
                    )
                    text = proc.stdout.strip()
                    if len(text) > 20:
                        result["pages"][page_num]["content"] = text
                        result["pages"][page_num]["has_text"] = True
                        pages_with_text += 1
            result["text_pages"] = pages_with_text
        except Exception:
            pass  # pdftotext not available or failed
    
    # Determine if OCR is still needed
    if pages_with_text / max(len(doc), 1) < MIN_TEXT_THRESHOLD:
        result["needs_ocr"] = True
    
    doc.close()
    return result

# ─── OCR Processing ─────────────────────────────────────────────────────────
def convert_page_to_image(pdf_path: str, page_num: int, dpi: int = OCR_DPI) -> Optional[str]:
    """Convert a PDF page to an image for OCR."""
    try:
        doc = fitz.open(pdf_path)
        page = doc[page_num]
        mat = fitz.Matrix(dpi/72, dpi/72)  # 72 is PDF default DPI
        pix = page.get_pixmap(matrix=mat)
        img_path = f"/tmp/ocr_page_{page_num}_{hashlib.md5(pdf_path.encode()).hexdigest()[:8]}.png"
        pix.save(img_path)
        doc.close()
        return img_path
    except Exception:
        return None

def run_ocr(image_path: str, lang: str = "eng+ara") -> Dict[str, Any]:
    """Run Tesseract OCR on an image."""
    try:
        result = subprocess.run(
            ["tesseract", image_path, "stdout", "-l", lang, "--oem", "3", "--psm", "3"],
            capture_output=True, text=True, timeout=60
        )
        text = result.stdout.strip()
        return {"text": text, "confidence": 0.0, "success": True}
    except Exception as e:
        return {"text": "", "confidence": 0.0, "success": False, "error": str(e)}

def ocr_pdf_page(pdf_path: str, page_num: int) -> Dict[str, Any]:
    """OCR a single PDF page."""
    img_path = convert_page_to_image(pdf_path, page_num)
    if not img_path:
        return {"text": "", "confidence": 0.0, "success": False, "error": "Failed to convert page to image"}
    
    result = run_ocr(img_path)
    os.unlink(img_path)
    return result

# ─── Text Cleaning & Markdown Conversion ────────────────────────────────────
def clean_extracted_text(text: str) -> str:
    """Clean extracted text while preserving structure."""
    if not text:
        return ""
    
    # Remove null bytes and control characters (keep newlines and tabs)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)
    
    # Remove repeated headers/footers (common in scanned books)
    lines = text.split('\n')
    
    # Detect and remove repeated page headers/footers
    if len(lines) > 10:
        # Check first 3 and last 3 lines for repetition
        header_candidates = []
        footer_candidates = []
        for i in range(min(5, len(lines))):
            stripped = lines[i].strip()
            if stripped and len(stripped) > 3:
                header_candidates.append(stripped)
        for i in range(max(0, len(lines)-5), len(lines)):
            stripped = lines[i].strip()
            if stripped and len(stripped) > 3:
                footer_candidates.append(stripped)
        
        # Remove lines that repeat as headers/footers
        cleaned_lines = []
        for line in lines:
            stripped = line.strip()
            # Skip if it's just a page number
            if re.match(r'^\d+$', stripped):
                continue
            # Skip if it matches a header/footer pattern exactly
            if stripped in header_candidates and header_candidates.count(stripped) > 1:
                continue
            if stripped in footer_candidates and footer_candidates.count(stripped) > 1:
                continue
            cleaned_lines.append(line)
        text = '\n'.join(cleaned_lines)
    
    # Fix common OCR mistakes
    text = re.sub(r'([a-zA-Z])- ([a-zA-Z])', r'\1\2', text)  # Fix hyphenated line breaks
    text = re.sub(r'  +', ' ', text)  # Remove extra spaces
    text = re.sub(r'\n{3,}', '\n\n', text)  # Max 2 consecutive newlines
    
    return text.strip()

def detect_headings(text: str) -> str:
    """Detect and format headings in text as Markdown."""
    lines = text.split('\n')
    result = []
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            result.append('')
            continue
        
        # Short lines that look like titles (all caps, or ending with colon, or very short)
        if (len(stripped) < 80 and 
            (stripped.isupper() or 
             re.match(r'^(Chapter|CHAPTER|Section|SECTION|Book|BOOK)\s+\d', stripped) or
             re.match(r'^[IVXLC]+\.\s+\w', stripped) or
             (stripped.endswith(':') and len(stripped) < 60))):
            result.append(f'\n## {stripped}\n')
        # Lines that are just numbers (section numbers)
        elif re.match(r'^\d+\.\d*\s+\w', stripped) and len(stripped) < 60:
            result.append(f'### {stripped}')
        else:
            result.append(stripped)
    
    return '\n'.join(result)

def text_to_markdown(text: str) -> str:
    """Convert plain text to clean Markdown."""
    text = clean_extracted_text(text)
    text = detect_headings(text)
    
    # Preserve paragraph structure
    paragraphs = text.split('\n\n')
    markdown_parts = []
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        # Check if it's a list item
        if re.match(r'^[\-\*•]\s', para):
            markdown_parts.append(para)
        # Check if it's a numbered list
        elif re.match(r'^\d+[\.\)]\s', para):
            markdown_parts.append(para)
        # Regular paragraph
        else:
            markdown_parts.append(para)
    
    return '\n\n'.join(markdown_parts)

def process_pdf(pdf_path: str, book_id: Optional[str] = None, force_ocr: bool = False) -> Dict[str, Any]:
    """
    Full PDF processing pipeline.
    If force_ocr is True, all pages are converted to images and OCR'd
    (useful for copyright-restricted PDFs that block text extraction).
    Returns the book record.
    """
    init_db()
    
    if not book_id:
        book_id = hashlib.md5(pdf_path.encode()).hexdigest()[:12]
    
    conn = get_db()
    
    # Check if already processed
    existing = conn.execute("SELECT id FROM books WHERE id = ?", (book_id,)).fetchone()
    if existing:
        conn.close()
        return {"book_id": book_id, "status": "already_exists"}
    
    # Extract text
    extraction = extract_text_from_pdf(pdf_path)
    metadata = extract_metadata(pdf_path, extraction)
    
    # OCR if needed (or if forced for copyright)
    ocr_used = False
    if extraction["needs_ocr"] or force_ocr:
        ocr_used = True
        for i, page in enumerate(extraction["pages"]):
            if not page["has_text"] or force_ocr:
                ocr_result = ocr_pdf_page(pdf_path, i)
                if ocr_result["success"] and ocr_result["text"]:
                    extraction["pages"][i]["content"] = ocr_result["text"]
                    extraction["pages"][i]["has_text"] = True
    
    # Convert to markdown
    full_text = "\n\n".join(p["content"] for p in extraction["pages"])
    markdown = text_to_markdown(full_text)
    
    # Save markdown to disk
    PROCESSED_DIR.mkdir(exist_ok=True)
    md_path = PROCESSED_DIR / f"{book_id}.md"
    md_path.write_text(markdown, encoding="utf-8")
    
    # Generate cover image (first page thumbnail)
    try:
        doc = fitz.open(pdf_path)
        page = doc[0]
        mat = fitz.Matrix(150/72, 150/72)
        pix = page.get_pixmap(matrix=mat)
        cover_path = PROCESSED_DIR / f"{book_id}_cover.png"
        pix.save(str(cover_path))
        doc.close()
    except Exception:
        cover_path = None
    
    # Insert book record
    now = datetime.now(timezone.utc).isoformat()
    conn.execute("""
        INSERT INTO books (id, title, author, language, subject, keywords, 
                          page_count, file_size, date_imported, source_path, 
                          cover_image, status, ocr_used, text_extracted)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ready', ?, ?)
    """, (
        book_id, metadata["title"], metadata["author"], metadata["language"],
        metadata["subject"], metadata["keywords"], metadata["page_count"],
        metadata["file_size"], now, pdf_path,
        str(cover_path) if cover_path else "",
        1 if ocr_used else 0, extraction["text_pages"]
    ))
    
    # Insert pages
    for page in extraction["pages"]:
        content = clean_extracted_text(page["content"])
        has_text = 1 if page["has_text"] else 0
        conn.execute("""
            INSERT INTO pages (book_id, page_number, content, has_text)
            VALUES (?, ?, ?, ?)
        """, (book_id, page["page_number"], content, has_text))
    
    # Initialize reading progress
    conn.execute("""
        INSERT INTO reading_progress (book_id, current_page, progress_pct, last_read)
        VALUES (?, 1, 0.0, ?)
    """, (book_id, now))
    
    conn.commit()
    conn.close()
    
    return {
        "book_id": book_id,
        "status": "ready",
        "title": metadata["title"],
        "author": metadata["author"],
        "page_count": metadata["page_count"],
        "ocr_used": ocr_used,
        "language": metadata["language"],
    }

def detect_headings(text: str) -> str:
    """Detect and format headings in text as Markdown."""
    lines = text.split('\n')
    result = []
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            result.append('')
            continue
        
        # Short lines that look like titles (all caps, or ending with colon, or very short)
        if (len(stripped) < 80 and 
            (stripped.isupper() or 
             re.match(r'^(Chapter|CHAPTER|Section|SECTION|Book|BOOK)\s+\d', stripped) or
             re.match(r'^[IVXLC]+\.\s+\w', stripped) or
             (stripped.endswith(':') and len(stripped) < 60))):
            result.append(f'\n## {stripped}\n')
        # Lines that are just numbers (section numbers)
        elif re.match(r'^\d+\.\d*\s+\w', stripped) and len(stripped) < 60:
            result.append(f'### {stripped}')
        else:
            result.append(stripped)
    
    return '\n'.join(result)

def text_to_markdown(text: str) -> str:
    """Convert plain text to clean Markdown."""
    text = clean_extracted_text(text)
    text = detect_headings(text)
    
    # Preserve paragraph structure
    paragraphs = text.split('\n\n')
    markdown_parts = []
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        # Check if it's a list item
        if re.match(r'^[\-\*•]\s', para):
            markdown_parts.append(para)
        # Check if it's a numbered list
        elif re.match(r'^\d+[\.\)]\s', para):
            markdown_parts.append(para)
        # Regular paragraph
        else:
            markdown_parts.append(para)
    
    return '\n\n'.join(markdown_parts)

# ─── Metadata Extraction ────────────────────────────────────────────────────
def extract_metadata(pdf_path: str, extraction_result: Dict) -> Dict:
    """Extract or infer metadata from PDF."""
    meta = extraction_result["metadata"]
    
    # Use PDF metadata if available, otherwise infer from filename
    title = meta.get("title", "") or ""
    author = meta.get("author", "") or ""
    
    if not title:
        # Infer from filename
        filename = Path(pdf_path).stem
        title = filename.replace('-', ' ').replace('_', ' ').title()
    
    # Detect language
    sample_text = " ".join(p.get("content", "") for p in extraction_result["pages"][:5])
    language = detect_language(sample_text)
    
    return {
        "title": title,
        "author": author if author else "Unknown",
        "language": language,
        "subject": meta.get("subject", ""),
        "keywords": meta.get("keywords", ""),
        "page_count": extraction_result["total_pages"],
        "file_size": os.path.getsize(pdf_path),
    }

def detect_language(text: str) -> str:
    """Detect if text is primarily English or Arabic."""
    # Check for Arabic characters
    arabic_chars = len(re.findall(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]', text))
    total_chars = len(text)
    
    if total_chars > 0 and arabic_chars / total_chars > 0.3:
        return "ar"
    return "en"

# ─── Library Search ─────────────────────────────────────────────────────────
def search_library(query: str, book_id: Optional[str] = None) -> List[Dict]:
    """Full-text search across all books or within a specific book."""
    conn = get_db()
    
    if book_id:
        rows = conn.execute("""
            SELECT p.book_id, p.page_number, p.content, b.title
            FROM pages p JOIN books b ON p.book_id = b.id
            WHERE p.book_id = ? AND p.content LIKE ?
            ORDER BY p.page_number
            LIMIT 50
        """, (book_id, f"%{query}%")).fetchall()
    else:
        rows = conn.execute("""
            SELECT p.book_id, p.page_number, p.content, b.title
            FROM pages p JOIN books b ON p.book_id = b.id
            WHERE p.content LIKE ?
            ORDER BY b.title, p.page_number
            LIMIT 50
        """, (f"%{query}%",)).fetchall()
    
    results = []
    for row in rows:
        # Extract snippet around match
        content = row["content"]
        idx = content.lower().find(query.lower())
        start = max(0, idx - 80)
        end = min(len(content), idx + len(query) + 80)
        snippet = ("..." if start > 0 else "") + content[start:end] + ("..." if end < len(content) else "")
        
        results.append({
            "book_id": row["book_id"],
            "book_title": row["title"],
            "page_number": row["page_number"],
            "snippet": snippet,
        })
    
    conn.close()
    return results

# ─── Book Operations ────────────────────────────────────────────────────────
def get_book(book_id: str) -> Optional[Dict]:
    """Get book metadata."""
    conn = get_db()
    row = conn.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def get_book_page(book_id: str, page_number: int) -> Optional[Dict]:
    """Get a single page's content."""
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM pages WHERE book_id = ? AND page_number = ?",
        (book_id, page_number)
    ).fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def get_book_toc(book_id: str) -> List[Dict]:
    """Extract table of contents from page content (detect headings)."""
    conn = get_db()
    rows = conn.execute(
        "SELECT page_number, content FROM pages WHERE book_id = ? ORDER BY page_number",
        (book_id,)
    ).fetchall()
    
    toc = []
    for row in rows:
        content = row["content"]
        # Find lines that look like chapter headings
        for match in re.finditer(r'^(?:Chapter\s+\d+[.:]\s*|CHAPTER\s+\d+[.:]\s*)(.+)$', content, re.MULTILINE):
            toc.append({
                "page_number": row["page_number"],
                "title": match.group(1).strip(),
                "level": 1
            })
        # Also catch "Book X" sections
        for match in re.finditer(r'^(?:Book\s+(?:[IVXLC]+|\d+)[.:]\s*)(.+)$', content, re.MULTILINE | re.IGNORECASE):
            toc.append({
                "page_number": row["page_number"],
                "title": match.group(1).strip(),
                "level": 0
            })
    
    conn.close()
    return toc

def get_all_books() -> List[Dict]:
    """Get all books in the library."""
    conn = get_db()
    rows = conn.execute("""
        SELECT b.*, 
               CASE WHEN rp.current_page IS NOT NULL 
                    THEN rp.current_page ELSE 1 END as current_page,
               CASE WHEN rp.progress_pct IS NOT NULL 
                    THEN rp.progress_pct ELSE 0.0 END as progress_pct
        FROM books b
        LEFT JOIN reading_progress rp ON b.id = rp.book_id
        ORDER BY b.title
    """).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_reading_progress(book_id: str, page_number: int):
    """Update reading progress for a book."""
    conn = get_db()
    book = conn.execute("SELECT page_count FROM books WHERE id = ?", (book_id,)).fetchone()
    if book:
        pct = round((page_number / book["page_count"]) * 100, 1)
        conn.execute("""
            INSERT OR REPLACE INTO reading_progress (book_id, current_page, progress_pct, last_read)
            VALUES (?, ?, ?, ?)
        """, (book_id, page_number, pct, datetime.now(timezone.utc).isoformat()))
        conn.commit()
    conn.close()

def delete_book(book_id: str) -> bool:
    """Delete a book and all related data."""
    conn = get_db()
    conn.execute("DELETE FROM pages WHERE book_id = ?", (book_id,))
    conn.execute("DELETE FROM bookmarks WHERE book_id = ?", (book_id,))
    conn.execute("DELETE FROM highlights WHERE book_id = ?", (book_id,))
    conn.execute("DELETE FROM notes WHERE book_id = ?", (book_id,))
    conn.execute("DELETE FROM reading_progress WHERE book_id = ?", (book_id,))
    conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
    
    # Clean up files
    md_path = PROCESSED_DIR / f"{book_id}.md"
    if md_path.exists():
        md_path.unlink()
    cover_path = PROCESSED_DIR / f"{book_id}_cover.png"
    if cover_path.exists():
        cover_path.unlink()
    
    return True

# ─── Bookmark Operations ────────────────────────────────────────────────────
def add_bookmark(book_id: str, page_number: int, title: str = "", color: str = "#d4af37") -> Dict:
    conn = get_db()
    conn.execute("""
        INSERT INTO bookmarks (book_id, page_number, title, color, date_created)
        VALUES (?, ?, ?, ?, ?)
    """, (book_id, page_number, title, color, datetime.now(timezone.utc).isoformat()))
    conn.commit()
    conn.close()
    return {"book_id": book_id, "page_number": page_number, "title": title}

def get_bookmarks(book_id: str) -> List[Dict]:
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM bookmarks WHERE book_id = ? ORDER BY page_number",
        (book_id,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

# ─── Highlight Operations ───────────────────────────────────────────────────
def add_highlight(book_id: str, page_number: int, start_offset: int, end_offset: int,
                  selected_text: str, color: str = "#ffd700", note: str = "") -> Dict:
    conn = get_db()
    conn.execute("""
        INSERT INTO highlights (book_id, page_number, start_offset, end_offset, 
                               selected_text, color, note, date_created)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (book_id, page_number, start_offset, end_offset, selected_text, color, note,
          datetime.now(timezone.utc).isoformat()))
    conn.commit()
    conn.close()
    return {"book_id": book_id, "page_number": page_number, "selected_text": selected_text}

def get_highlights(book_id: str) -> List[Dict]:
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM highlights WHERE book_id = ? ORDER BY page_number, date_created",
        (book_id,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

# ─── Note Operations ────────────────────────────────────────────────────────
def add_note(book_id: str, page_number: int, content: str) -> Dict:
    conn = get_db()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute("""
        INSERT INTO notes (book_id, page_number, content, date_created, date_modified)
        VALUES (?, ?, ?, ?, ?)
    """, (book_id, page_number, content, now, now))
    conn.commit()
    conn.close()
    return {"book_id": book_id, "page_number": page_number, "content": content}

def get_notes(book_id: str) -> List[Dict]:
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM notes WHERE book_id = ? ORDER BY page_number, date_created DESC",
        (book_id,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

# ─── Batch Import ───────────────────────────────────────────────────────────
def import_pdfs_from_directory(directory: str, force_ocr: bool = False) -> List[Dict]:
    """Import all PDFs from a directory. Auto-detects scanned PDFs for OCR."""
    results = []
    pdf_dir = Path(directory)
    if not pdf_dir.exists():
        return results
    
    for pdf_path in sorted(pdf_dir.glob("*.pdf")):
        try:
            # First try normal extraction
            result = process_pdf(str(pdf_path), force_ocr=force_ocr)
            if result.get("status") == "already_exists":
                results.append({"file": str(pdf_path), "status": "already_exists"})
            elif result.get("status") == "ready":
                results.append(result)
            else:
                results.append({"file": str(pdf_path), "status": result.get("status", "unknown")})
        except Exception as e:
            results.append({"file": str(pdf_path), "status": "error", "error": str(e)})
    
    return results

# ─── CLI ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python library_engine.py <import|search|list|info> [args]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "import":
        if len(sys.argv) < 3:
            print("Usage: python library_engine.py import <pdf_path_or_dir>")
            sys.exit(1)
        path = sys.argv[2]
        if os.path.isdir(path):
            results = import_pdfs_from_directory(path)
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            result = process_pdf(path)
            print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == "search":
        if len(sys.argv) < 3:
            print("Usage: python library_engine.py search <query> [book_id]")
            sys.exit(1)
        query = sys.argv[2]
        book_id = sys.argv[3] if len(sys.argv) > 3 else None
        results = search_library(query, book_id)
        print(json.dumps(results, indent=2, ensure_ascii=False))
    
    elif command == "list":
        books = get_all_books()
        print(json.dumps(books, indent=2, ensure_ascii=False))
    
    elif command == "info":
        if len(sys.argv) < 3:
            print("Usage: python library_engine.py info <book_id>")
            sys.exit(1)
        book = get_book(sys.argv[2])
        if book:
            print(json.dumps(book, indent=2, ensure_ascii=False))
        else:
            print("Book not found")
    
    elif command == "init":
        init_db()
        print("Library database initialized ✓")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
