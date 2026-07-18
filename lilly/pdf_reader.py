"""
lilly/pdf_reader.py
Lilly's ability to read PDF books from Gigi's library.

Why this file exists:
    Gigi has occult and astrology PDFs on her SD card.
    This module extracts text from them, handles long books
    by chunking, and searches for files by name.
"""

from pathlib import Path
from typing import List, Optional

try:
    import PyPDF2
    _PDF_AVAILABLE = True
except ImportError:
    _PDF_AVAILABLE = False


def is_available() -> bool:
    """Check if PyPDF2 is installed."""
    return _PDF_AVAILABLE


def extract_text(pdf_path: str | Path) -> str:
    """Extract all text from a PDF file."""
    if not _PDF_AVAILABLE:
        raise RuntimeError("PyPDF2 is not installed. Run: pip install PyPDF2")

    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    text_parts = []
    with open(path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

    return "\n\n".join(text_parts)


def chunk_text(text: str, max_chars: int = 4000, overlap: int = 200) -> List[str]:
    """
    Split long text into overlapping chunks for LLM context windows.
    Overlap helps maintain continuity between chunks.
    """
    if len(text) <= max_chars:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        if end >= len(text):
            chunks.append(text[start:])
            break

        # Try to break at a paragraph
        search_text = text[start:end]
        last_para = search_text.rfind("\n\n")
        if last_para > max_chars // 2:
            end = start + last_para
        else:
            # Try to break at a sentence
            last_sentence = search_text.rfind(". ")
            if last_sentence > max_chars // 2:
                end = start + last_sentence + 1

        chunks.append(text[start:end])
        start = end - overlap  # overlap for context

    return chunks


def find_pdf(name: str, search_dirs: List[Path]) -> Optional[Path]:
    """
    Search for a PDF by partial name in common directories.
    'picatrix' matches 'picatrix-translation.pdf'
    """
    name_lower = name.lower().replace(".pdf", "")
    for directory in search_dirs:
        if not directory.exists():
            continue
        for path in directory.rglob("*.pdf"):
            if name_lower in path.name.lower():
                return path
    return None


def read_pdf_for_llm(pdf_path: str | Path, max_chars: int = 8000) -> str:
    """
    Extract text from PDF, suitable for LLM context.
    For very long books, returns first N chars with a note.
    """
    text = extract_text(pdf_path)
    if len(text) > max_chars:
        truncated = text[:max_chars]
        # Try to end at a sentence
        last_dot = truncated.rfind(".")
        if last_dot > max_chars * 0.8:
            truncated = truncated[:last_dot + 1]
        return truncated + f"\n\n[PDF continues... {len(text)} total characters]"
    return text

