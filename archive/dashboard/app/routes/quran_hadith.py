"""Quran & Hadith — paginated API with search."""
from __future__ import annotations

from flask import Blueprint, jsonify, request

bp = Blueprint('quran_hadith', __name__, url_prefix='/api')

QH_DATA_CACHE = None
QH_PATH = None


def _get_qh():
    global QH_DATA_CACHE, QH_PATH
    if QH_DATA_CACHE is None:
        if QH_PATH is None:
            from pathlib import Path
            QH_PATH = Path(__file__).resolve().parent.parent.parent / 'data' / 'quran_hadith_data.json'
        import json
        if QH_PATH.exists():
            with open(QH_PATH, encoding='utf-8') as f:
                QH_DATA_CACHE = json.load(f)
        else:
            QH_DATA_CACHE = {'quran': [], 'hadith': []}
    return QH_DATA_CACHE


def set_qh_path(path):
    """Allow override of data path for testing."""
    global QH_PATH, QH_DATA_CACHE
    QH_PATH = path
    QH_DATA_CACHE = None


@bp.route('/quran/verses')
def api_quran_verses():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    data = _get_qh()
    verses = data.get('quran', [])
    total = len(verses)
    start = (page - 1) * per_page
    end = min(start + per_page, total)
    page_verses = verses[start:end]
    themes = sorted(set(v.get('theme', '') for v in verses if v.get('theme')))
    return jsonify({
        'verses': page_verses, 'total': total,
        'page': page, 'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page,
        'themes': themes,
    })


@bp.route('/hadith/books')
def api_hadith_books():
    data = _get_qh()
    hadiths = data.get('hadith', [])
    books = {}
    for h in hadiths:
        bn = h.get('bookName', 'Unknown')
        if bn not in books:
            books[bn] = {'bookName': bn, 'count': 0, 'emoji': '📜'}
        books[bn]['count'] += 1
    return jsonify(list(books.values()))


@bp.route('/hadith/chapters')
def api_hadith_chapters():
    book = request.args.get('book', '').strip()
    data = _get_qh()
    hadiths = data.get('hadith', [])
    if book:
        hadiths = [h for h in hadiths if h.get('bookName') == book]
    chapters = {}
    for h in hadiths:
        ch = str(h.get('chapterId', ''))
        if ch not in chapters:
            chapters[ch] = {'chapterId': ch, 'count': 0, 'bookName': h.get('bookName', '')}
        chapters[ch]['count'] += 1
    sorted_chs = sorted(chapters.values(), key=lambda c: int(c['chapterId']) if c['chapterId'].isdigit() else 0)
    return jsonify(sorted_chs)


@bp.route('/hadith/narrations')
def api_hadith_narrations():
    book = request.args.get('book', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    search = request.args.get('search', '').strip().lower()
    chapter = request.args.get('chapter', '').strip()
    data = _get_qh()
    hadiths = data.get('hadith', [])
    if book:
        hadiths = [h for h in hadiths if h.get('bookName') == book]
    if chapter:
        hadiths = [h for h in hadiths if str(h.get('chapterId', '')) == chapter]
    if search:
        hadiths = [h for h in hadiths if
            search in (h.get('english', '') or '').lower()
            or search in (h.get('narratorEn', '') or '').lower()
            or search in (h.get('arabic', '') or '')
            or search in (h.get('bookName', '') or '').lower()]
    total = len(hadiths)
    start = (page - 1) * per_page
    end = min(start + per_page, total)
    page_nar = hadiths[start:end]
    return jsonify({
        'narrations': page_nar, 'total': total,
        'page': page, 'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page,
        'search': search,
    })
