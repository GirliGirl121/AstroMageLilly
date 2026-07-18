"""Diary / MagiJournal — web diary, tasks, dreams, bookmarks."""
from __future__ import annotations

from datetime import datetime

from flask import Blueprint, jsonify, request

from web_diary_db import get_diary_db
from app.config import TZ

bp = Blueprint('diary', __name__, url_prefix='/api/diary')


def _get_day_data(date_str: str) -> dict:
    """Return astronomical day data for the diary."""
    from app.config import swe, load_json
    from calendar_engine import get_day_data
    data = get_day_data(date_str)
    man = load_json('picatrix_mansions.json')
    naks = load_json('nakshatra_data.json')
    data['mansion_info'] = m = man.get(data.get('mansion_id', ''), {})
    data['book_recommendations'] = [
        {'title': 'Picatrix (Ghāyat al-Ḥakīm)', 'author': 'Anonymous, c. 11th C.', 'category': 'Magic'},
        {'title': 'Shams al-Maʿārif', 'author': 'Ahmad al-Būnī (d. 1225)', 'category': 'Letter Magic'},
        {'title': 'The Goal of the Wise', 'author': 'Attributed to Maslama al-Qurṭubī', 'category': 'Hermetic'},
        {'title': 'Al-Tukhi: The Fulfillment of Needs', 'author': 'Abdul Fattah al-Tawukhi', 'category': 'Astrology'},
    ]
    return data


@bp.route('/day')
def api_diary_day():
    date_str = request.args.get('date', datetime.now(TZ).strftime('%Y-%m-%d'))
    data = _get_day_data(date_str)
    return jsonify(data)


@bp.route('/save', methods=['POST'])
def api_diary_save():
    db = get_diary_db()
    data = request.json or {}
    db.save_entry(data.get('date', ''), data.get('content', ''))
    return jsonify({'ok': True})


@bp.route('/task/add', methods=['POST'])
def api_diary_task_add():
    db = get_diary_db()
    data = request.json or {}
    db.add_task(data.get('date', ''), data.get('text', ''))
    return jsonify({'ok': True})


@bp.route('/task/toggle', methods=['POST'])
def api_diary_task_toggle():
    db = get_diary_db()
    data = request.json or {}
    db.toggle_task(data.get('id'))
    return jsonify({'ok': True})


@bp.route('/task/delete', methods=['POST'])
def api_diary_task_delete():
    db = get_diary_db()
    data = request.json or {}
    db.delete_task(data.get('id'))
    return jsonify({'ok': True})


@bp.route('/dream/save', methods=['POST'])
def api_diary_dream_save():
    db = get_diary_db()
    data = request.json or {}
    db.save_dream(data.get('date', ''), data.get('dream', ''))
    return jsonify({'ok': True})


@bp.route('/bookmark/toggle', methods=['POST'])
def api_diary_bookmark_toggle():
    db = get_diary_db()
    data = request.json or {}
    db.toggle_bookmark(data.get('date', ''))
    return jsonify({'ok': True})


@bp.route('/favorite/toggle', methods=['POST'])
def api_diary_favorite_toggle():
    db = get_diary_db()
    data = request.json or {}
    db.toggle_favorite(data.get('date', ''))
    return jsonify({'ok': True})


@bp.route('/search')
def api_diary_search():
    db = get_diary_db()
    q = request.args.get('q', '')
    return jsonify(db.search_entries(q))


@bp.route('/bookmarks')
def api_diary_bookmarks():
    db = get_diary_db()
    return jsonify(db.get_all_bookmarks())


@bp.route('/favorites')
def api_diary_favorites():
    db = get_diary_db()
    return jsonify(db.get_all_favorites())


@bp.route('/bookmark/remove', methods=['POST'])
def api_diary_bookmark_remove():
    db = get_diary_db()
    data = request.json or {}
    db.remove_bookmark(data.get('id'))
    return jsonify({'ok': True})


@bp.route('/favorite/remove', methods=['POST'])
def api_diary_favorite_remove():
    db = get_diary_db()
    data = request.json or {}
    db.remove_favorite(data.get('id'))
    return jsonify({'ok': True})


@bp.route('/month')
def api_diary_month():
    from calendar_engine import get_month_data
    year = int(request.args.get('year', datetime.now(TZ).year))
    month = int(request.args.get('month', datetime.now(TZ).month))
    try:
        data = get_month_data(year, month)
        results = []
        for d in data:
            results.append({
                'date': d.get('date'),
                'day': int(d.get('date', '0').split('-')[2]),
                'moon_sign': d.get('moon_sign', ''),
                'moon_mansion': d.get('moon_mansion', ''),
                'day_ruler': d.get('day_ruler', ''),
                'mansion_index': d.get('mansion_index', -1),
                'aspects_count': len(d.get('aspects', [])),
            })
        return jsonify({'year': year, 'month': month, 'days': results})
    except Exception as e:
        return jsonify({'error': str(e), 'days': []})


@bp.route('/search-history')
def api_diary_search_history():
    db = get_diary_db()
    return jsonify(db.get_search_history(10))
