"""Cosmic Home — live sky, transits, lunar data, short-form endpoints."""
from __future__ import annotations

import json
import math
import random
from datetime import datetime, timezone, timedelta
from pathlib import Path

import swisseph as swe
from flask import Blueprint, jsonify, make_response, render_template, request

from app.config import (
    ROOT, TZ, SIGNS, NAKSHATRAS_27, NAKSHATRA_LORDS,
    DASHA_YEARS_MAP, DASHA_SEQUENCE, SIDEREAL_YEAR,
    MANIONS_DATA, NAKSHATRA_DATA, TAROT_DATA,
    PLANET_ENERGY, PLANET_SYMBOLS, PLANET_COLORS,
    get_sign_info, get_moon_phase_obj, get_current_hour,
    calc_planet_pos, load_json,
)

bp = Blueprint('home', __name__)

PLANET_IDS = [
    (swe.SUN, 'Sun'), (swe.MOON, 'Moon'), (swe.MERCURY, 'Mercury'),
    (swe.VENUS, 'Venus'), (swe.MARS, 'Mars'), (swe.JUPITER, 'Jupiter'),
    (swe.SATURN, 'Saturn'), (swe.URANUS, 'Uranus'), (swe.NEPTUNE, 'Neptune'),
    (swe.PLUTO, 'Pluto'), (swe.CHIRON, 'Chiron'),
]


def _get_jd_now():
    """Get current Julian day number."""
    utc = datetime.now(TZ).astimezone(timezone.utc)
    return swe.julday(utc.year, utc.month, utc.day, utc.hour + utc.minute/60 + utc.second/3600)


def _get_current_planets():
    """Get current planetary positions."""
    jd = _get_jd_now()
    positions = []
    for sid, name in PLANET_IDS:
        p = calc_planet_pos(jd, sid, name)
        if p:
            positions.append(p)
    return positions


def _calc_aspects(positions):
    """Calculate aspects between all planets."""
    aspects_list = []
    major_orbs = {'conjunction': 8.0, 'sextile': 6.0, 'square': 8.0, 'trine': 8.0, 'opposition': 8.0}
    minor_orbs = {'semi-sextile': 2.0, 'semi-square': 2.0, 'quintile': 1.5, 'sesquiquadrate': 2.0, 'biquintile': 1.5, 'quincunx': 3.0}
    aspect_angles = {'conjunction': 0, 'semi-sextile': 30, 'semi-square': 45, 'sextile': 60,
        'quintile': 72, 'square': 90, 'trine': 120, 'sesquiquadrate': 135, 'biquintile': 144, 'quincunx': 150, 'opposition': 180}
    aspect_symbols = {'conjunction': '☌', 'sextile': '⚹', 'square': '□', 'trine': '△', 'opposition': '☍',
        'semi-sextile': '╱', 'semi-square': '∠', 'quintile': 'Q', 'sesquiquadrate': '⚼', 'biquintile': 'BQ', 'quincunx': '⚻'}

    for i, p1 in enumerate(positions):
        for j, p2 in enumerate(positions):
            if j <= i:
                continue
            lon1 = p1['longitude']
            lon2 = p2['longitude']
            diff = abs(lon1 - lon2) % 360
            if diff > 180:
                diff = 360 - diff

            for aspect_name, angle in aspect_angles.items():
                orb = major_orbs.get(aspect_name, minor_orbs.get(aspect_name, 2.0))
                if abs(diff - angle) <= orb:
                    aspects_list.append({
                        'planet1': p1['name'], 'planet2': p2['name'],
                        'aspect': aspect_name, 'symbol': aspect_symbols.get(aspect_name, ''),
                        'orb': round(abs(diff - angle), 2), 'angle': angle,
                        'applying': False,
                    })
                    break
    return aspects_list


def _calc_dasha(
    birth_year=1981, birth_month=10, birth_day=30,
    birth_hour=2 + 56/60, birth_tz=2, target_year=None
):
    """Vimshottari Dasha calculator. Returns full dict with current_dasha/current_bhukti."""
    if target_year is None:
        target_year = datetime.now(TZ).year
    from datetime import datetime as dt, timedelta, timezone
    tz = timezone(timedelta(hours=2))  # SAST

    bd = datetime(birth_year, birth_month, birth_day)
    target_d = datetime(int(target_year), 6, 1)
    days = (target_d - bd).days

    b_ut = birth_hour - birth_tz
    bjd = swe.julday(birth_year, birth_month, birth_day, b_ut)
    moon_jd = swe.calc_ut(bjd, swe.MOON)[0][0]
    n_idx = int(moon_jd / (360 / 27)) % 27
    lord = NAKSHATRA_LORDS[n_idx]
    dasha_start = DASHA_SEQUENCE.index(lord)
    balance = ((moon_jd % (360 / 27)) / (360 / 27)) * DASHA_YEARS_MAP[lord]

    # Build dasha timeline (all times in SAST/tz-aware)
    cur = datetime(birth_year, birth_month, birth_day, int(birth_hour), int((birth_hour % 1) * 60), tzinfo=tz)
    dashas = []
    first_end = cur + timedelta(days=balance * SIDEREAL_YEAR)
    dashas.append({'lord': lord, 'years': round(DASHA_YEARS_MAP[lord], 1),
                   'remaining_at_birth': round(balance, 4),
                   'start': cur.isoformat(), 'end': first_end.isoformat(),
                   'type': 'first (balance)'})
    cur = first_end

    for i in range(1, 9):
        idx = (dasha_start + i) % 9
        l = DASHA_SEQUENCE[idx]
        yrs = DASHA_YEARS_MAP[l]
        end = cur + timedelta(days=yrs * SIDEREAL_YEAR)
        dashas.append({'lord': l, 'years': yrs,
                       'start': cur.isoformat(), 'end': end.isoformat(),
                       'type': 'full'})
        cur = end

    # Find current dasha
    now = datetime.now(TZ)
    current_dasha = None
    current_bhukti = None
    for d in dashas:
        d_start = dt.fromisoformat(d['start'])
        d_end = dt.fromisoformat(d['end'])
        if d_start <= now < d_end:
            current_dasha = d
            # Bhuktis
            maha_yrs = d['years']
            d_total_days = (d_end - d_start).days
            d_elapsed = (now - d_start).total_seconds() / 86400
            start_idx = DASHA_SEQUENCE.index(d['lord'])
            bhuktis = []
            bhukti_cur = d_start
            for bi in range(9):
                bl_idx = (start_idx + bi) % 9
                bl = DASHA_SEQUENCE[bl_idx]
                byrs = (maha_yrs * DASHA_YEARS_MAP[bl]) / 120.0
                bhukti_end = bhukti_cur + timedelta(days=byrs * SIDEREAL_YEAR)
                active = bhukti_cur <= now < bhukti_end
                bhuktis.append({
                    'lord': bl, 'years': round(byrs, 3),
                    'start': bhukti_cur.isoformat(), 'end': bhukti_end.isoformat(),
                    'active': active
                })
                if active:
                    current_bhukti = bhuktis[-1]
                bhukti_cur = bhukti_end
            current_dasha['bhuktis'] = bhuktis
            break

    return {
        'birth_nakshatra': NAKSHATRAS_27[n_idx],
        'birth_nakshatra_lord': lord,
        'current_dasha': current_dasha,
        'current_bhukti': current_bhukti,
        'moon_longitude': round(moon_jd, 4),
        'dashas': dashas,
    }


def _current_nakshatra() -> dict:
    """Get current nakshatra from transit Moon."""
    jd = _get_jd_now()
    moon_lon = swe.calc_ut(jd, swe.MOON)[0][0]
    n_idx = int(moon_lon / (360 / 27)) % 27
    pada = int((moon_lon % (360 / 27)) / (360 / 27 / 4)) + 1
    name = NAKSHATRAS_27[n_idx] if n_idx < len(NAKSHATRAS_27) else 'Unknown'
    lord = NAKSHATRA_LORDS[n_idx] if n_idx < len(NAKSHATRA_LORDS) else 'Unknown'
    extra = NAKSHATRA_DATA.get(name, {}) if NAKSHATRA_DATA else {}
    return {
        'name': name, 'pada': pada, 'lord': lord,
        'longitude': round(moon_lon, 2),
        'symbol': extra.get('symbol', ''),
        'deity': extra.get('deity', ''),
        'meaning': extra.get('meaning', ''),
    }


def _islamic_astro() -> dict:
    """Combined Islamic astrology data: lunar mansion + nakshatra + dasha."""
    jd = _get_jd_now()
    moon = swe.calc_ut(jd, swe.MOON)[0][0]

    # ── Current lunar mansion (Picatrix: 28 mansions, each ~12.857°) ──
    mansion_deg = moon % 360
    mansions_list = MANIONS_DATA.get('mansions', [])
    active_mansion = None
    for m in mansions_list:
        try:
            start_str = m['start_degrees']
            end_str = m['end_degrees']
            def _parse_picatrix_deg(s):
                parts = s.replace('°', '').replace("'", '').replace('"', '').split()
                deg = float(parts[0])
                minutes = float(parts[1]) if len(parts) > 1 else 0
                secs = float(parts[2]) if len(parts) > 2 else 0
                sign_name = ' '.join(parts[3:]) if len(parts) > 3 else (parts[3] if len(parts) > 3 else 'Aries')
                sign_abbr = sign_name[:3].title()
                sign_offsets = {'Ari':0,'Tau':30,'Gem':60,'Can':90,'Leo':120,'Vir':150,
                               'Lib':180,'Sco':210,'Sag':240,'Cap':270,'Aqu':300,'Pis':330}
                return sign_offsets.get(sign_abbr, 0) + deg + minutes/60 + secs/3600
            start_abs = _parse_picatrix_deg(start_str)
            end_abs = _parse_picatrix_deg(end_str)
            if start_abs <= mansion_deg < end_abs:
                active_mansion = m
                break
        except (KeyError, IndexError, ValueError):
            idx = int(mansion_deg // 12.857142857)
            if 0 <= idx < len(mansions_list) and mansions_list[idx].get('number') == m.get('number'):
                active_mansion = m
                continue

    if not active_mansion and mansions_list:
        idx = int(mansion_deg // 12.857142857)
        if idx < len(mansions_list):
            active_mansion = mansions_list[idx]

    # ── Build mansion result ──
    mansion_result = {}
    if active_mansion:
        nature = active_mansion.get('nature', '').lower()
        if 'hot' in nature and 'dry' in nature:
            benefic = 'Mars-ruled: Active, assertive — potent for war, protection, and confrontation'
            malefic = 'Avoid peace negotiations, marriage, or calm endeavors. Energy is combative.'
        elif 'cold' in nature and 'moist' in nature:
            benefic = 'Moon-ruled: Nurturing, receptive — good for healing, planting, emotional work'
            malefic = 'Avoid start of bold ventures or confrontations. Energy is passive.'
        elif 'cold' in nature and 'dry' in nature:
            benefic = 'Saturn-ruled: Structured, enduring — good for building, discipline, long-term planning'
            malefic = 'Avoid celebration, expansion, or social events. Energy is constrictive.'
        elif 'air' in nature or 'mercurial' in nature:
            benefic = 'Mercurial: Intellectual, communicative — good for learning, trade, writing'
            malefic = 'Avoid emotional decisions or commitments. Energy is changeable.'
        else:
            benefic = 'Balanced — moderately favorable for general activities'
            malefic = 'Avoid extreme undertakings. Middle path is best.'
        mansion_result = {
            'number': active_mansion.get('number'),
            'picatrix_name': active_mansion.get('picatrix_name'),
            'arabic_name': active_mansion.get('arabic_name'),
            'transliteration': active_mansion.get('arabic_transliteration'),
            'meaning': active_mansion.get('meaning'),
            'nature': active_mansion.get('nature'),
            'planetary_ruler': active_mansion.get('planetary_ruler'),
            'spirit': active_mansion.get('lord_of_mansion_spirit'),
            'benefic': benefic,
            'malefic': malefic,
            'best_activities': active_mansion.get('recommended_works', [])[:5],
            'avoid_activities': [active_mansion.get('forbidden_works', 'No specific prohibitions')],
        }

    # ── Nakshatra ──
    nak = _current_nakshatra()

    # ── Dasha ──
    dasha = _calc_dasha()

    # ── Moon phase ──
    moon_phase = get_moon_phase_obj()

    # ── Day ruler ──
    day_names = ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']
    day_ruler = day_names[datetime.now(TZ).weekday()]

    return {
        'mansion': mansion_result,
        'nakshatra': nak,
        'dasha': dasha,
        'moon_phase': moon_phase,
        'day_ruler': day_ruler,
        'scholars': [
            {'name': 'Abu Ma\'shar al-Balkhi (Albumasar, 787-886 CE)',
             'info': 'The most influential astrologer of the medieval world.'},
            {'name': 'Al-Kindi (801-873 CE)',
             'info': 'The Philosopher of the Arabs. Wrote extensively on astrological rays.'},
            {'name': 'Al-Biruni (973-1048 CE)',
             'info': 'Polymath author of Kitab al-Tafhim.'},
            {'name': 'Ahmad al-Buni (d. 1225 CE)',
             'info': 'Shams al-Ma\'arif al-Kubra — the Great Sun of Knowledge.'},
            {'name': 'Ibn Arabi (1165-1240 CE)',
             'info': 'The Greatest Master. Integrates astrology with Sufi metaphysics.'},
        ],
        'contributions': [
            'Great Conjunctions theory: Saturn-Jupiter conjunctions every 20 years drive historical cycles',
            'Firdaria: planetary time-lord system refined by Abu Ma\'shar',
            'Lunar Mansions (Manazil al-Qamar): 28 mansions for electional and talismanic work',
        ],
    }


def _energy_polarities() -> dict:
    """Energy and polarity information."""
    return {
        'elements': [
            {'name': 'Fire', 'signs': 'Aries, Leo, Sagittarius', 'energy': 'Active, creative, transformative'},
            {'name': 'Earth', 'signs': 'Taurus, Virgo, Capricorn', 'energy': 'Stable, practical, grounded'},
            {'name': 'Air', 'signs': 'Gemini, Libra, Aquarius', 'energy': 'Intellectual, communicative, social'},
            {'name': 'Water', 'signs': 'Cancer, Scorpio, Pisces', 'energy': 'Emotional, intuitive, receptive'},
        ],
        'polarities': [
            {'name': 'Masculine (Yang)', 'signs': 'Fire + Air', 'energy': 'Expressive, outgoing, projective'},
            {'name': 'Feminine (Yin)', 'signs': 'Earth + Water', 'energy': 'Receptive, inward, magnetic'},
        ],
        'qualities': [
            {'name': 'Cardinal', 'signs': 'Aries, Cancer, Libra, Capricorn', 'energy': 'Initiating, leading, beginning'},
            {'name': 'Fixed', 'signs': 'Taurus, Leo, Scorpio, Aquarius', 'energy': 'Stabilizing, sustaining, resisting'},
            {'name': 'Mutable', 'signs': 'Gemini, Virgo, Sagittarius, Pisces', 'energy': 'Adapting, changing, transitioning'},
        ],
    }


def _quran_hadith_daily() -> dict:
    """Get a random Quran verse and hadith."""
    qh_data = load_json('quran_hadith_data.json')
    verses = qh_data.get('quran', [])
    hadiths = qh_data.get('hadith', [])
    verse = random.choice(verses) if verses else {}
    hadith = random.choice(hadiths) if hadiths else {}
    return {
        'quran': {
            'arabic': verse.get('arabic', ''),
            'translation': verse.get('translation', ''),
            'surah': verse.get('surah', 1),
            'surahNameEn': verse.get('surahNameEn', ''),
            'ayah': verse.get('ayah', 1),
        },
        'hadith': {
            'english': hadith.get('english', ''),
            'bookName': hadith.get('bookName', ''),
            'narratorEn': hadith.get('narratorEn', ''),
        },
    }


# ─── Routes ──────────────────────────────────────────────────────────────

@bp.route('/')
def home():
    resp = make_response(render_template('index.html'))
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp


@bp.route('/api/home')
def api_home():
    """Combined home / daily summary."""
    from calendar_engine import get_day_data
    now = datetime.now(TZ)
    today = now.strftime('%Y-%m-%d')
    data = get_day_data(today)
    moon = get_moon_phase_obj()
    current_hour = get_current_hour(data)
    hous = _current_nakshatra()
    dasha_data = _calc_dasha()
    mahadasha = dasha_data['current_dasha']['lord'] if dasha_data.get('current_dasha') else ''
    bhukti = dasha_data['current_bhukti']['lord'] if dasha_data.get('current_bhukti') else ''
    transit_planets = _get_current_planets()
    aspects = _calc_aspects(transit_planets)

    greeting = data.get('spirit_greeting', 'Greetings, seeker of light.')
    day_ruler = data.get('day_ruler', '')
    moon_sign = data.get('moon_sign', '')
    mansion = data.get('mansion_name', '')

    # Nested objects expected by frontend
    ia = _islamic_astro()
    en = _energy_polarities()
    qh = _quran_hadith_daily()
    # Tarot — combine major + minor arcana
    taro = {}
    all_cards = []
    if TAROT_DATA:
        major_cards = TAROT_DATA.get('major_arcana', [])
        if isinstance(major_cards, list):
            all_cards.extend(major_cards)
        # minor_arcana is a dict of suits
        minor_by_suit = TAROT_DATA.get('minor_arcana', {})
        if isinstance(minor_by_suit, dict):
            for suit, suit_cards in minor_by_suit.items():
                if isinstance(suit_cards, list):
                    all_cards.extend(suit_cards)
    if all_cards:
        card = random.choice(all_cards)
        taro = {
            'name': card.get('name', 'Unknown'),
            'suit': card.get('suit', ''),
            'keywords': card.get('keywords', []),
            'upright': card.get('upright', '') or card.get('meaning_up', ''),
            'reversed': card.get('reversed_meaning', '') or card.get('meaning_rev', ''),
            'daily_message': card.get('daily', '') or random.choice(card.get('keywords', ['Trust the process'])),
        }
    # Flat energy strings from current astro data
    sun_pos = moon_sign
    dominant = 'Fire'
    if sun_pos in ('Taurus', 'Virgo', 'Capricorn'):
        dominant = 'Earth'
    elif sun_pos in ('Gemini', 'Libra', 'Aquarius'):
        dominant = 'Air'
    elif sun_pos in ('Cancer', 'Scorpio', 'Pisces'):
        dominant = 'Water'
    polarity = 'Masculine (Yang)' if dominant in ('Fire', 'Air') else 'Feminine (Yin)'
    energy_flat = {
        'polarity': polarity,
        'dominant_element': dominant,
    }

    return jsonify({
        'date': today,
        'day_ruler': day_ruler,
        'moon_sign': moon_sign,
        'moon_phase': moon['phase'],
        'moon_emoji': moon['emoji'],
        'mansion': mansion,
        'nakshatra': hous,
        'mahadasha': mahadasha,
        'bhukti': bhukti,
        'greeting': greeting or 'Greetings, LadyLefey — the stars await.',
        'planetary_hour': current_hour,
        'transits': transit_planets[:5],
        'aspects': aspects[:3],
        'quote': random.choice([
            'The cosmos is within us. We are made of star-stuff. — Carl Sagan',
            'Astrology is a language. If you understand it, the sky speaks to you. — Dane Rudhyar',
            'We are not human beings having a spiritual experience. We are spiritual beings having a human experience.',
        ]),
        # Nested objects consumed by frontend JS
        'islamic_astro': ia,
        'energy': energy_flat,
        'tarot': taro,
        'quran_hadith': qh,
    })


@bp.route('/api/islamic-astro')
def api_islamic_astro():
    return jsonify(_islamic_astro())


@bp.route('/api/energy')
def api_energy():
    return jsonify(_energy_polarities())


@bp.route('/api/moon-phase')
def api_moon_phase():
    return jsonify(get_moon_phase_obj())


@bp.route('/api/tarot-daily')
def api_tarot_daily_legacy():
    """Legacy endpoint — kept for compatibility."""
    if not TAROT_DATA:
        return jsonify({'name': 'The Fool', 'keywords': ['beginnings', 'innocence']})
    cards = TAROT_DATA.get('cards', [])
    if not cards:
        return jsonify({'name': 'The Fool', 'keywords': ['beginnings', 'innocence']})
    card = random.choice(cards)
    return jsonify({
        'name': card.get('name', 'Unknown'),
        'suit': card.get('suit', ''),
        'keywords': card.get('keywords', []),
        'upright': card.get('upright_meaning', '') or card.get('meaning_up', ''),
        'reversed': card.get('reversed_meaning', '') or card.get('meaning_rev', ''),
    })


@bp.route('/api/quran-hadith')
def api_quran_hadith_legacy():
    """Legacy endpoint — kept for compatibility."""
    return jsonify(_quran_hadith_daily())


@bp.route('/api/dasha')
def api_dasha():
    year = request.args.get('year', datetime.now(TZ).year)
    try:
        year = float(year)
    except ValueError:
        year = datetime.now(TZ).year
    dasha_data = _calc_dasha(target_year=year)
    md = dasha_data['current_dasha']['lord'] if dasha_data.get('current_dasha') else ''
    bk = dasha_data['current_bhukti']['lord'] if dasha_data.get('current_bhukti') else ''
    return jsonify({'mahadasha': md, 'bhukti': bk, 'year': int(year)})


@bp.route('/api/nakshatra-now')
def api_nakshatra_now():
    return jsonify(_current_nakshatra())


@bp.route('/api/live')
@bp.route('/api/transits')
def api_live():
    """Current planetary positions (aliased as /api/transits)."""
    planets = _get_current_planets()
    aspects = _calc_aspects(planets)
    major_aspects = [a for a in aspects if a['aspect'] in ('conjunction','sextile','square','trine','opposition')]
    return jsonify({
        'planets': planets,
        'total_planets': len(planets),
        'aspects': major_aspects,
        'total_aspects': len(major_aspects),
    })


@bp.route('/api/cosmic-overview')
def api_cosmic_overview():
    planets = _get_current_planets()
    aspects = _calc_aspects(planets)
    moon = get_moon_phase_obj()
    sun_pos = next((p for p in planets if p['name'] == 'Sun'), {})
    moon_pos = next((p for p in planets if p['name'] == 'Moon'), {})
    return jsonify({
        'planets': planets,
        'aspects': aspects,
        'moon_phase': moon,
        'sun_sign': sun_pos.get('sign', ''),
        'moon_sign': moon_pos.get('sign', ''),
        'retrograde_planets': [p['name'] for p in planets if p.get('retrograde')],
    })


@bp.route('/api/planetary-hour')
def api_planetary_hour():
    from calendar_engine import get_day_data
    today = datetime.now(TZ).strftime('%Y-%m-%d')
    data = get_day_data(today)
    current_hour = get_current_hour(data)
    return jsonify({
        'current_hour': current_hour,
        'hours_today': data.get('planetary_hours', []),
    })


@bp.route('/api/lunar-mansion')
def api_lunar_mansion():
    from calendar_engine import get_day_data
    today = datetime.now(TZ).strftime('%Y-%m-%d')
    data = get_day_data(today)

    # Get current mansion from islamic_astro (uses Swiss Ephemeris)
    ia_data = _islamic_astro()
    mansion = ia_data.get('mansion', {})
    mansion_data = MANIONS_DATA.get(data.get('mansion_id', ''), {})

    return jsonify({
        'mansion': mansion,
        'mansion_id': data.get('mansion_id', ''),
        'mansion_data': mansion_data,
    })


@bp.route('/api/aspects')
def api_aspects():
    planets = _get_current_planets()
    aspects = _calc_aspects(planets)
    return jsonify({
        'aspects': aspects,
        'total': len(aspects),
    })


@bp.route('/api/mood')
def api_mood():
    """Astrological mood based on current transits."""
    planets = _get_current_planets()
    aspects = _calc_aspects(planets)
    moon = get_moon_phase_obj()
    mood_score = random.randint(40, 95)

    mood_map = {
        'conjunction': 'Focused', 'sextile': 'Harmonious', 'square': 'Challenged',
        'trine': 'Flowing', 'opposition': 'Balancing',
    }
    active_moods = []
    for a in aspects[:3]:
        mood = mood_map.get(a['aspect'], 'Neutral')
        if mood not in active_moods:
            active_moods.append(mood)

    return jsonify({
        'score': mood_score,
        'mood': active_moods[0] if active_moods else 'Neutral',
        'influences': active_moods[:3],
        'moon_phase': moon['phase'],
        'moon_emoji': moon['emoji'],
        'advice': 'Take a breath and check your transits. The stars are always in motion.',
    })


@bp.route('/api/schedule')
def api_schedule():
    return jsonify({
        'events': [
            {'time': 'Now', 'event': 'Current transit reading', 'icon': '🌌'},
            {'time': 'Today', 'event': 'Planetary hour tracking active', 'icon': '⏳'},
            {'time': 'Tonight', 'event': f"Moon in {get_moon_phase_obj()['phase']}", 'icon': '🌙'},
        ]
    })


@bp.route('/api/quick-actions')
def api_quick_actions():
    actions = [
        {'id': 'refresh', 'label': '🔄  Refresh Transits', 'endpoint': '/api/live'},
        {'id': 'tarot', 'label': '🃏  Draw a Card', 'endpoint': '/api/tarot-daily'},
        {'id': 'diary', 'label': '📓  Today in MagiJournal', 'endpoint': '/api/diary/day'},
    ]
    return jsonify(actions)


@bp.route('/api/star-song')
def api_star_song():
    """A poetic Lilly reading based on the current sky."""
    planets = _get_current_planets()
    moon = get_moon_phase_obj()
    nakshatra = _current_nakshatra()
    sun_pos = next((p for p in planets if p['name'] == 'Sun'), {})
    moon_pos = next((p for p in planets if p['name'] == 'Moon'), {})

    lines = [
        f"The Sun journeys through {sun_pos.get('sign', 'the heavens')}, casting its radiant light upon your path.",
        f"The Moon, {moon['phase']} in {moon_pos.get('sign', 'the sky')}, {['whispers to your dreams', 'calls you inward', 'illuminates your emotions', 'guides your intuition'][random.randint(0,3)]}.",
        f"The Nakshatra of {nakshatra['name']} is active — {nakshatra.get('meaning', 'a celestial gateway')}.",
    ]
    retrograde = [p['name'] for p in planets if p.get('retrograde')]
    if retrograde:
        lines.append(f"{', '.join(retrograde)} {'is' if len(retrograde)==1 else 'are'} retrograde — a time for reflection.")
    lines.append(f"Breathe deep, LadyLefey. The stars sing only for you tonight. 💜✨")

    return jsonify({'poem': '\n\n'.join(lines)})


@bp.route('/api/astro-quote')
def api_astro_quote():
    quotes = [
        {'text': 'The cosmos is within us. We are made of star-stuff.', 'author': 'Carl Sagan'},
        {'text': 'Astrology is a language. If you understand it, the sky speaks to you.', 'author': 'Dane Rudhyar'},
        {'text': 'We are not human beings having a spiritual experience. We are spiritual beings having a human experience.', 'author': 'Pierre Teilhard de Chardin'},
        {'text': 'The stars incline, they do not compel.', 'author': 'Ptolemy'},
        {'text': 'Know thyself, and thou shalt know the universe and the gods.', 'author': 'Inscribed at the Temple of Apollo, Delphi'},
        {'text': 'Above all, know thyself.', 'author': 'Thales of Miletus'},
        {'text': 'The function of astrology is not to predict the future, but to illuminate the present.', 'author': 'Traditional saying'},
    ]
    q = random.choice(quotes)
    return jsonify(q)


@bp.route('/api/summary')
def api_summary():
    """Comprehensive dashboard summary endpoint."""
    from calendar_engine import get_day_data
    now = datetime.now(TZ)
    today = now.strftime('%Y-%m-%d')
    data = get_day_data(today)
    planets = _get_current_planets()
    aspects = _calc_aspects(planets)
    moon = get_moon_phase_obj()
    nakshatra = _current_nakshatra()
    dasha_data = _calc_dasha()
    mahadasha = dasha_data['current_dasha']['lord'] if dasha_data.get('current_dasha') else ''
    bhukti = dasha_data['current_bhukti']['lord'] if dasha_data.get('current_bhukti') else ''
    current_hour = get_current_hour(data)

    major_aspects = [a for a in aspects if a['aspect'] in ('conjunction','sextile','square','trine','opposition')]
    sun_pos = next((p for p in planets if p['name'] == 'Sun'), {})
    moon_pos = next((p for p in planets if p['name'] == 'Moon'), {})

    return jsonify({
        'date': today,
        'time': now.strftime('%H:%M'),
        'sun_sign': sun_pos.get('sign', ''),
        'moon_sign': data.get('moon_sign', moon_pos.get('sign', '')),
        'moon_phase': moon['phase'],
        'moon_emoji': moon['emoji'],
        'day_ruler': data.get('day_ruler', ''),
        'mansion': data.get('mansion_name', ''),
        'planetary_hour': current_hour,
        'nakshatra': nakshatra,
        'mahadasha': mahadasha,
        'bhukti': bhukti,
        'planets': planets,
        'aspects': major_aspects,
        'retrograde_planets': [p['name'] for p in planets if p.get('retrograde')],
    })


@bp.route('/api/mansion/progress')
def api_mansion_progress():
    """Moon's current progress through the current lunar mansion."""
    jd = _get_jd_now()
    moon_lon = swe.calc_ut(jd, swe.MOON)[0][0]
    pos_in_mansion = moon_lon % (360 / 28)
    progress_pct = (pos_in_mansion / (360 / 28)) * 100
    return jsonify({
        'moon_longitude': round(moon_lon, 2),
        'progress_percent': round(progress_pct, 1),
        'degrees_elapsed': round(pos_in_mansion, 2),
    })


@bp.route('/api/natal', methods=['POST'])
def api_natal_v1():
    """Basic natal chart (v1, simplified)."""
    from app.routes.natal import api_calc_natal
    return api_calc_natal()


# ─── CORS preflight handler (kept for compatibility) ─────────────────────
@bp.after_request
def add_cors_headers(response):
    response.headers.setdefault('Access-Control-Allow-Origin', '*')
    response.headers.setdefault('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.setdefault('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    return response
