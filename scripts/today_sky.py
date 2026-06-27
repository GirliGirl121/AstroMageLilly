#!/usr/bin/env python3
"""Just today's transit sky — no natal overlay."""
import swisseph as swe
from datetime import datetime, timezone, timedelta

swe.set_ephe_path('/home/ladylefey/ephe')
TZ = timezone(timedelta(hours=2))
now = datetime.now(TZ)
now_utc = now - timedelta(hours=2)
jd = swe.julday(now_utc.year, now_utc.month, now_utc.day,
                now_utc.hour + now_utc.minute/60 + now_utc.second/3600)

PLANETS = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mercury': swe.MERCURY,
    'Venus': swe.VENUS, 'Mars': swe.MARS, 'Jupiter': swe.JUPITER,
    'Saturn': swe.SATURN, 'Uranus': swe.URANUS, 'Neptune': swe.NEPTUNE,
    'Pluto': swe.PLUTO
}
SYMBOLS = {'Sun': '\u2609', 'Moon': '\u263d', 'Mercury': '\u263f', 'Venus': '\u2640', 'Mars': '\u2642',
           'Jupiter': '\u2643', 'Saturn': '\u2644', 'Uranus': '\u2645', 'Neptune': '\u2646', 'Pluto': '\u2647'}
SIGNS = ['Ari', 'Tau', 'Gem', 'Can', 'Leo', 'Vir', 'Lib', 'Sco', 'Sag', 'Cap', 'Aqu', 'Pis']
SIGN_SYMBOLS = ['\u2648', '\u2649', '\u264a', '\u264b', '\u264c', '\u264d', '\u264e', '\u264f', '\u2650', '\u2651', '\u2652', '\u2653']


def sign_info(lon):
    d, m = divmod(lon, 30)
    return SIGNS[int(d)], SIGN_SYMBOLS[int(d)], f'{int(m)}*{int((m % 1)*60):02d}\''


print(f'=== TODAY\'S SKY ===')
print(f'{now.strftime("%A, %d %B %Y at %H:%M")} SAST')
print()

positions = {}
for name, sid in PLANETS.items():
    pos = swe.calc_ut(jd, sid)[0][0]
    s, sym, deg = sign_info(pos)
    positions[name] = {'lon': pos, 'sign': s, 'symbol': sym}
    print(f'  {s}{sym} {SYMBOLS[name]} {deg}')

print()
print('--- Aspects (orb <= 3*) ---')
ASPECTS = [('Conjunction', 0, 8), ('Sextile', 60, 6), ('Square', 90, 6),
           ('Trine', 120, 6), ('Opposition', 180, 6)]

names = list(positions.keys())
for i, n1 in enumerate(names):
    for n2 in names[i+1:]:
        diff = abs(positions[n1]['lon'] - positions[n2]['lon'])
        if diff > 180:
            diff = 360 - diff
        for asp_name, asp_angle, max_orb in ASPECTS:
            orb = abs(diff - asp_angle)
            if orb <= 3:
                p1 = positions[n1]
                p2 = positions[n2]
                print(f'  {p1["sign"]}{p1["symbol"]} {SYMBOLS[n1]} {asp_name} {p2["sign"]}{p2["symbol"]} {SYMBOLS[n2]}  ({orb:.1f}*)')
                break

print()
print('--- Lunar ---')
moon = positions['Moon']['lon']
nak_idx = int(moon // 13.333333333333334)
pada = int((moon % 13.333333333333334) // 3.333333333333334) + 1
NAKS = ['Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
        'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
        'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
        'Mula', 'Purva Ashada', 'Uttara Ashada', 'Shravana', 'Dhanishta', 'Shatabhisha',
        'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati']
print(f'  Moon nakshatra: {NAKS[nak_idx]} (Pada {pada})')

phase_angle = (positions['Moon']['lon'] - positions['Sun']['lon']) % 360
if phase_angle < 45:
    phase = '\U0001f311 New Moon'
elif phase_angle < 90:
    phase = '\U0001f312 Waxing Crescent'
elif phase_angle < 135:
    phase = '\U0001f313 First Quarter'
elif phase_angle < 180:
    phase = '\U0001f314 Waxing Gibbous'
elif phase_angle < 225:
    phase = '\U0001f315 Full Moon'
elif phase_angle < 270:
    phase = '\U0001f316 Waning Gibbous'
elif phase_angle < 315:
    phase = '\U0001f317 Last Quarter'
else:
    phase = '\U0001f318 Waning Crescent'
print(f'  Moon phase: {phase}')

# Planetary hour
day_names = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
day_ruler = day_names[now.weekday()]
print(f'  Day ruler: {day_ruler}')
