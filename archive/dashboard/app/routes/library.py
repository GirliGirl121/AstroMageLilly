"""Library — PDF import, OCR, books, search."""
from __future__ import annotations

from flask import Blueprint, jsonify, request, send_file

from library_engine import (
    get_all_books, get_book, get_book_page, get_book_toc,
    search_library, update_reading_progress, add_bookmark, get_bookmarks,
    add_highlight, get_highlights, add_note, get_notes, delete_book,
    import_pdfs_from_directory, PROCESSED_DIR,
)

bp = Blueprint('library', __name__, url_prefix='/api/library')


@bp.route('/books', methods=['GET'])
def api_library_books():
    return jsonify(get_all_books())


@bp.route('/book/<book_id>', methods=['GET'])
def api_library_book(book_id):
    book = get_book(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    return jsonify(book)


@bp.route('/book/<book_id>/page/<int:page_number>', methods=['GET'])
def api_library_page(book_id, page_number):
    page = get_book_page(book_id, page_number)
    if not page:
        return jsonify({'error': 'Page not found'}), 404
    return jsonify(page)


@bp.route('/book/<book_id>/toc', methods=['GET'])
def api_library_toc(book_id):
    return jsonify(get_book_toc(book_id))


@bp.route('/book/<book_id>/search', methods=['GET'])
def api_library_search_in_book(book_id):
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': "Missing query parameter 'q'"}), 400
    return jsonify({'query': query, 'results': search_library(query, book_id)})


@bp.route('/search', methods=['GET'])
def api_library_search():
    query = request.args.get('q', '')
    book_id = request.args.get('book', '')
    if not query:
        return jsonify({'error': "Missing query parameter 'q'"}), 400
    results = search_library(query, book_id if book_id else None)
    return jsonify({'query': query, 'results': results})


@bp.route('/book/<book_id>/progress', methods=['POST'])
def api_library_progress(book_id):
    data = request.json or {}
    update_reading_progress(book_id, data.get('page', 1), data.get('total', 0))
    return jsonify({'ok': True})


@bp.route('/book/<book_id>/bookmark', methods=['POST'])
def api_library_bookmark(book_id):
    data = request.json or {}
    add_bookmark(book_id, page=data.get('page', 0), note=data.get('note', ''))
    return jsonify({'ok': True})


@bp.route('/book/<book_id>/bookmarks', methods=['GET'])
def api_library_bookmarks(book_id):
    return jsonify(get_bookmarks(book_id))


@bp.route('/book/<book_id>/highlight', methods=['POST'])
def api_library_highlight(book_id):
    data = request.json or {}
    add_highlight(book_id, page=data.get('page', 0), text=data.get('text', ''), note=data.get('note', ''))
    return jsonify({'ok': True})


@bp.route('/book/<book_id>/highlights', methods=['GET'])
def api_library_highlights(book_id):
    return jsonify(get_highlights(book_id))


@bp.route('/book/<book_id>/note', methods=['POST'])
def api_library_note(book_id):
    data = request.json or {}
    add_note(book_id, page=data.get('page', 0), text=data.get('text', ''))
    return jsonify({'ok': True})


@bp.route('/book/<book_id>/notes', methods=['GET'])
def api_library_notes(book_id):
    return jsonify(get_notes(book_id))


@bp.route('/book/<book_id>', methods=['DELETE'])
def api_library_delete(book_id):
    delete_book(book_id)
    return jsonify({'ok': True})


@bp.route('/import', methods=['POST'])
def api_library_import():
    data = request.json or {}
    force_ocr = data.get('force_ocr', False)
    directory = data.get('directory', str(PROCESSED_DIR))
    results = import_pdfs_from_directory(directory, force_ocr=force_ocr)
    return jsonify({'imported': results})


@bp.route('/cover/<book_id>', methods=['GET'])
def api_library_cover(book_id):
    cover_path = PROCESSED_DIR / f'{book_id}_cover.png'
    if cover_path.exists():
        return send_file(str(cover_path))
    return jsonify({'error': 'No cover'}), 404


# ─── Library Reference Texts ─────────────────────────────────────────────

@bp.route('/references')
def api_library_references():
    refs_data = _get_library_refs()
    return jsonify(refs_data)


@bp.route('/reference/<ref_id>')
def api_library_reference(ref_id):
    refs_data = _get_library_refs()
    for ref in refs_data:
        if ref.get('id') == ref_id or ref.get('title', '').lower().replace(' ', '-') == ref_id:
            return jsonify(ref)
    return jsonify({'error': 'Reference not found'}), 404


def _get_library_refs():
    """Load sacred library reference texts from data file."""
    import json
    from pathlib import Path
    refs_path = Path(__file__).resolve().parent.parent.parent / 'data' / 'library_references.json'
    if refs_path.exists():
        with open(refs_path, encoding='utf-8') as f:
            return json.load(f)
    return []
