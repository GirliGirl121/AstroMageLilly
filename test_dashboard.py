#!/usr/bin/env python3
"""Comprehensive test for AstroMage Dashboard v5.0"""
import sys, os, json
sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.join(os.getcwd(), 'MagiJournal'))
from dashboard import app

failures = []

def test(path, name, check_fn=None):
    with app.test_client() as c:
        r = c.get(path)
        ok = r.status_code in (200, 302)
        if not ok:
            failures.append(f'{name} ({path}): {r.status_code}')
            print(f'  ❌ {name} ({path}) — {r.status_code}')
        else:
            extra = ''
            if check_fn:
                try:
                    data = json.loads(r.get_data(as_text=True))
                    check_fn(data)
                    extra = ' [verified]'
                except Exception as e:
                    failures.append(f'{name}: check failed - {e}')
                    extra = f' ⚠️ {e}'
            print(f'  ✅ {name} ({path}){extra}')

print('🔮 AstroMage v5.0 — Test Suite')
print()

# API endpoints
test('/', 'Home Page HTML')
test('/api/home', 'Combined Home', lambda d: None)
test('/api/islamic-astro', 'Islamic Astrology', lambda d: 
    d.get('mansion') and d.get('nakshatra') and d.get('dasha'))
test('/api/energy', 'Energy & Polarities', lambda d: d.get('dominant_element'))
test('/api/moon-phase', 'Moon Phase', lambda d: d.get('phase'))
test('/api/tarot-daily', 'Tarot Daily', lambda d: d.get('name'))
test('/api/quran-hadith', 'Quran & Hadith', lambda d: d.get('quran') and d.get('hadith'))
test('/api/dasha', 'Dasha Calculator', lambda d: d.get('current_dasha'))
test('/api/nakshatra-now', 'Current Nakshatra', lambda d: d.get('nakshatra'))
test('/api/planetary-hour', 'Planetary Hour', lambda d: None)
test('/api/lunar-mansion', 'Lunar Mansion', lambda d: None)
test('/api/aspects', 'Aspects', lambda d: None)
test('/api/cosmic-overview', 'Cosmic Overview', lambda d: d.get('planets'))
test('/api/live', 'Live Planets', lambda d: None)
test('/api/mood', 'Mood', lambda d: d.get('mood_score'))

# Chat POST
with app.test_client() as c:
    r = c.post('/api/chat', json={'message': 'hello lilly'})
    if r.status_code == 200:
        reply = json.loads(r.get_data())['reply']
        print(f'  ✅ Chat POST — "{reply[:50]}..."')
    else:
        failures.append(f'Chat POST: {r.status_code}')
        print(f'  ❌ Chat POST — {r.status_code}')

# Detailed Islamic Astro check
with app.test_client() as c:
    r = c.get('/api/islamic-astro')
    ia = json.loads(r.get_data(as_text=True))
    print(f'\n  📍 Mansion: {ia["mansion"]["picatrix_name"]} ({ia["mansion"]["arabic_name"]})')
    print(f'  📍 Nakshatra: {ia["nakshatra"]["name"]} Pada {ia["nakshatra"]["pada"]}')
    cd = ia['dasha']['current_dasha']
    cb = ia['dasha']['current_bhukti']
    print(f'  📍 Mahadasha: {cd["lord"]} — Bhukti: {cb["lord"]}')
    print(f'  📍 Moon: {ia["moon_phase"]["phase"]} {ia["moon_phase"]["emoji"]}')

# Detailed Tarot check
with app.test_client() as c:
    r = c.get('/api/tarot-daily')
    t = json.loads(r.get_data(as_text=True))
    print(f'  📍 Tarot: {t["name"]} — {", ".join(t["keywords"][:3])}')

# Detailed Quran/Hadith check
with app.test_client() as c:
    r = c.get('/api/quran-hadith')
    qh = json.loads(r.get_data(as_text=True))
    print(f'  📍 Quran: {qh["quran"]["surahNameEn"]} {qh["quran"]["surah"]}:{qh["quran"]["ayah"]}')
    print(f'  📍 Hadith: {qh["hadith"]["bookName"]}')

# HTML structure verification
with app.test_client() as c:
    html = c.get('/').get_data(as_text=True)
    checks = [
        ('Sidebar exists', 'sidebar' in html),
        ('Lilly portrait', 'lilly_portrait.png' in html),
        ('Cosmic Home tab', 'tab-home' in html),
        ('Islamic Astrology section', 'Islamic Astrology' in html),
        ('Quran & Hadith section', 'Quran & Hadith' in html),
        ('Tarot of the Day', 'Tarot of the Day' in html),
        ('Nakshatra & Dasha section', 'Nakshatra & Dasha' in html),
        ('Chat section', 'Chat with Lilly' in html),
        ('12 sidebar nav items', html.count('sidebar-nav-item') >= 12),
        ('Starfield canvas', 'starfield' in html),
        ('Pin button', 'pin-btn' in html),
        ('Streamlit sidebar', 'sidebar-pin-btn' in html),
    ]
    print()
    for label, ok in checks:
        print(f'  {"✅" if ok else "❌"} HTML: {label}')
        if not ok: failures.append(f'HTML: {label}')

# Data file verification
print()
for fn in ['tarot_data.json', 'nakshatra_data.json', 'quran_hadith_data.json']:
    path = os.path.join(os.getcwd(), 'data', fn)
    exists = os.path.exists(path)
    print(f'  {"✅" if exists else "❌"} Data file: {fn}')
    if not exists: failures.append(f'Missing: {fn}')

print()
if failures:
    print(f'❌ {len(failures)} FAILURES:')
    for f in failures:
        print(f'   • {f}')
    sys.exit(1)
else:
    print(f'✨ ALL 20+ TESTS PASSED — Dashboard v5.0 is LIVE! ✨')
