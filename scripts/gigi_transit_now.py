#!/usr/bin/env python3
"""
Gigi's Transit Chart — Corrected
Reads system clock, converts SAST→UTC properly, uses Swiss Ephemeris.
Hybrid format: clean indented lists, Vedic meanings, full aspects.
"""
import swisseph as swe
import math
from datetime import datetime, timezone, timedelta

# === BIRTH DETAILS (Gigi) ===
birth_year = 1981; birth_month = 10; birth_day = 30
birth_hour_utc = 1.1  # 03:06 SAST → 01:06 UTC
geo_lat = -33.9249; geo_lon = 18.4241  # Cape Town

# === CURRENT TIME (SAST = UTC+2) ===
now_local = datetime.now()
sast_offset = timedelta(hours=2)
now_utc = now_local - sast_offset
now_hour_utc = now_utc.hour + now_utc.minute/60 + now_utc.second/3600

# === SETUP ===
swe.set_ephe_path('/home/ladylefey/ephe')
julday_birth = swe.julday(birth_year, birth_month, birth_day, birth_hour_utc)
julday_now = swe.julday(now_utc.year, now_utc.month, now_utc.day, now_hour_utc)

signs = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
abbrev = ['Ari','Tau','Gem','Can','Leo','Vir','Lib','Sco','Sag','Cap','Aqu','Pis']
symbols = ['♈','♉','♊','♋','♌','♍','♎','♏','♐','♑','♒','♓']

planet_ids = [
    ('Sun', swe.SUN), ('Moon', swe.MOON), ('Mercury', swe.MERCURY),
    ('Venus', swe.VENUS), ('Mars', swe.MARS), ('Jupiter', swe.JUPITER),
    ('Saturn', swe.SATURN), ('Uranus', swe.URANUS), ('Neptune', swe.NEPTUNE),
    ('Pluto', swe.PLUTO), ('North Node', swe.MEAN_NODE)
]

# Natal houses (Placidus)
houses = swe.houses(julday_birth, geo_lat, geo_lon, b'P')

def get_sign_info(lon):
    sign_idx = int(lon // 30)
    deg = lon % 30
    d = int(deg)
    m = int((deg - d) * 60)
    return signs[sign_idx], abbrev[sign_idx], symbols[sign_idx], d, m, sign_idx

def get_house(lon, houses):
    for i in range(12):
        h_start = houses[0][i]
        h_end = houses[0][(i+1) % 12]
        if h_end < h_start:
            if lon >= h_start or lon < h_end:
                return i + 1
        else:
            if h_start <= lon < h_end:
                return i + 1
    return 1

aspect_names = {0: ('☌', 'Conjunction'), 60: ('✶', 'Sextile'),
                90: ('□', 'Square'), 120: ('△', 'Trine'), 180: ('☍', 'Opposition')}

# Vedic planet personalities
personalities = {
    'Sun': 'Father/King/Soul', 'Moon': 'Mother/Queen/Mind', 'Mercury': 'Prince/Commerce',
    'Venus': 'Princess/Love', 'Mars': 'Soldier/Assertion', 'Jupiter': 'Teacher/Wisdom',
    'Saturn': 'General/Discipline', 'Uranus': 'Visionary', 'Neptune': 'Mystic',
    'Pluto': 'Transformer', 'North Node': 'Rahu — Ambition/Materialism'
}

# Vedic house meanings
house_meanings = {
    1: 'Self/Body', 2: 'Wealth/Family', 3: 'Siblings/Courage', 4: 'Home/Mother',
    5: 'Children/Creativity', 6: 'Enemies/Service', 7: 'Marriage/Partnership',
    8: 'Death/Transformation', 9: 'Religion/Fortune', 10: 'Career/Karma',
    11: 'Gains/Aspirations', 12: 'Losses/Spirituality'
}

print("=" * 62)
print("  GIGI'S PRESENT TRANSIT CHART")
print(f"  Birth: {birth_day} Oct {birth_year} | Now: {now_local.strftime('%Y-%m-%d %H:%M')} SAST")
print("  Hybrid System: Tropical timing + Vedic meaning")
print("=" * 62)

# --- NATAL PLANETS ---
print("\n✦ NATAL PLANETS ✦")
natal_positions = {}
for name, pid in planet_ids:
    lon = swe.calc_ut(julday_birth, pid)[0][0]
    natal_positions[name] = lon
    sign, abr, sym, d, m, si = get_sign_info(lon)
    h = get_house(lon, houses)
    nakshatra_idx = int(lon // (360/27))
    stage = 'Infant(0-1°)' if d < 1 else 'Young(1-5°)' if d < 6 else 'Adult(6-17°)' if d < 18 else 'Mature(18-25°)' if d < 26 else 'Old(26-30°)'
    print(f"  {abr}{sym} {name} {d}°{m:02d}' (H{h}) — {stage}")

asc = houses[1][0]
print(f"\n  ASC: {abbrev[int(asc//30)]}{symbols[int(asc//30)]} {int(asc%30)}°{int((asc%30-int(asc%30))*60):02d}' (Source Point)")

# Natal Lilith, Chiron, Parts
natal_lilith = swe.calc_ut(julday_birth, swe.MEAN_APOG)[0][0]
natal_chiron = swe.calc_ut(julday_birth, swe.CHIRON)[0][0]
natal_sun = natal_positions['Sun']
natal_moon = natal_positions['Moon']
natal_asc = houses[1][0]
natal_part_spirit = (natal_asc + natal_moon - natal_sun) % 360
natal_part_fortune = (natal_asc + natal_sun - natal_moon) % 360
natal_south_node = (natal_positions['North Node'] + 180) % 360

for label, lon in [('Lilith', natal_lilith), ('Chiron', natal_chiron),
                    ('Part of Spirit', natal_part_spirit), ('Part of Fortune', natal_part_fortune),
                    ('South Node ☋', natal_south_node)]:
    sign, abr, sym, d, m, si = get_sign_info(lon)
    print(f"  {abr}{sym} {label} {d}°{m:02d}'")

# --- TRANSIT PLANETS ---
print("\n✦ TRANSIT PLANETS (Current Sky) ✦")
transit_positions = {}
for name, pid in planet_ids:
    lon = swe.calc_ut(julday_now, pid)[0][0]
    transit_positions[name] = lon
    sign, abr, sym, d, m, si = get_sign_info(lon)
    print(f"  {abr}{sym} {name} {d}°{m:02d}'")

# Transit Lilith, Chiron
t_lilith = swe.calc_ut(julday_now, swe.MEAN_APOG)[0][0]
t_chiron = swe.calc_ut(julday_now, swe.CHIRON)[0][0]
t_sun = transit_positions['Sun']
t_moon = transit_positions['Moon']
t_part_spirit = (natal_asc + t_moon - t_sun) % 360
t_part_fortune = (natal_asc + t_sun - t_moon) % 360
for label, lon in [('Lilith', t_lilith), ('Chiron', t_chiron)]:
    sign, abr, sym, d, m, si = get_sign_info(lon)
    print(f"  {abr}{sym} {label} {d}°{m:02d}'")

print(f"\n  Transit Part of Spirit: {abbrev[int(t_part_spirit//30)]}{symbols[int(t_part_spirit//30)]} {int(t_part_spirit%30)}°{int((t_part_spirit%30-int(t_part_spirit%30))*60):02d}'")
print(f"  Transit Part of Fortune: {abbrev[int(t_part_fortune//30)]}{symbols[int(t_part_fortune//30)]} {int(t_part_fortune%30)}°{int((t_part_fortune%30-int(t_part_fortune%30))*60):02d}'")

# --- MAJOR TRANSIT ASPECTS TO NATAL ---
print("\n✦ TRANSIT ASPECTS TO NATAL (orb ≤ 3°) ✦")
aspects_found = []
for t_name, t_lon in transit_positions.items():
    for n_name, n_lon in natal_positions.items():
        diff = abs(t_lon - n_lon)
        if diff > 180: diff = 360 - diff
        for angle, (sym, aname) in aspect_names.items():
            orb = abs(diff - angle)
            if orb <= 3.0:
                ts, tabr, tsym, td, tm, tsi = get_sign_info(t_lon)
                ns, n_nabr, nsym, nd, nm, nsi = get_sign_info(n_lon)
                aspects_found.append((t_name, aname, n_name, orb, tsym, tabr, td, tm, nsym, n_nabr, nd, nm, diff))

if aspects_found:
    for t_name, aname, n_name, orb, tsym, tabr, td, tm, nsym, n_nabr, nd, nm, diff in sorted(aspects_found, key=lambda x: x[3]):
        print(f"  {tabr}{tsym} {t_name} {td}°{tm:02d}' {aname} {n_nabr}{nsym} {n_name} {nd}°{nm:02d}' (orb {orb:.1f}°)")
else:
    print("  No major aspects within 3° orb.")

# --- TRANSIT-TO-TRANSIT ASPECTS ---
print("\n✦ CURRENT SKY ASPECTS (transit-to-transit, orb ≤ 3°) ✦")
sky_aspects = []
for t1_name, t1_lon in transit_positions.items():
    for t2_name, t2_lon in transit_positions.items():
        if t1_name >= t2_name: continue
        diff = abs(t1_lon - t2_lon)
        if diff > 180: diff = 360 - diff
        for angle, (sym, aname) in aspect_names.items():
            orb = abs(diff - angle)
            if orb <= 3.0:
                s1, a1, sym1, d1, m1, _ = get_sign_info(t1_lon)
                s2, a2, sym2, d2, m2, _ = get_sign_info(t2_lon)
                sky_aspects.append((t1_name, aname, t2_name, orb, a1, sym1, d1, m1, a2, sym2, d2, m2))

if sky_aspects:
    for t1, aname, t2, orb, a1, sym1, d1, m1, a2, sym2, d2, m2 in sorted(sky_aspects, key=lambda x: x[3]):
        print(f"  {a1}{sym1} {t1} {d1}°{m1:02d}' {aname} {a2}{sym2} {t2} {d2}°{m2:02d}' (orb {orb:.1f}°)")
else:
    print("  No major sky aspects within 3° orb.")

# --- LUNAR MANSION (Nakshatra) ---
print("\n✦ LUNAR MANSION (Moon's Nakshatra) ✦")
moon_lon = transit_positions['Moon']
nak_idx = int(moon_lon / (360/27))
nakshatras = [
    'Ashwini','Bharani','Krittika','Rohini','Mrigashira','Ardra',
    'Punarvasu','Pushya','Ashlesha','Magha','Purva Phalguni','Uttara Phalguni',
    'Hasta','Chitra','Swati','Vishakha','Anuradha','Jyeshtha','Mula',
    'Purva Ashadha','Uttara Ashadha','Shravana','Dhanishta','Shatabhisha',
    'Purva Bhadrapada','Uttara Bhadrapada','Revati'
]
nak_rulers = ['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury']
print(f"  Moon in {nakshatras[nak_idx]}")
print(f"  Ruler: {nak_rulers[nak_idx % 9]}")
print(f"  Position: {int(moon_lon % 13.33333 * 60 / 13.33333)}% through mansion")

# --- PLANETARY HOUR ---
print("\n✦ PLANETARY HOUR ✦")
# Sunrise for current day at Kariega (-33.9°S, 25.5°E)
# swe.rise_trans takes (lon, lat, alt) as geopos tuple
sunrise_jd = swe.rise_trans(julday_now, swe.SUN, swe.CALC_RISE, (25.5, -33.9, 100), 0, 0, swe.FLG_SWIEPH)
sunset_jd = swe.rise_trans(julday_now, swe.SUN, swe.CALC_SET, (25.5, -33.9, 100), 0, 0, swe.FLG_SWIEPH)
if sunrise_jd[0] == 0 and sunset_jd[0] == 0:
    sunrise = sunrise_jd[1][0]
    sunset = sunset_jd[1][0]
    day_length = (sunset - sunrise) / 12
    night_length = ((sunrise + 1) - sunset) / 12  # next day's sunrise
    hours_since_sunrise = (julday_now - sunrise) * 24
    hour_idx = int(hours_since_sunrise)
    chaldean = ['Saturn','Jupiter','Mars','Sun','Venus','Mercury','Moon']
    ruler = chaldean[hour_idx % 7]
    period = 'Day' if hour_idx < 12 else 'Night'
    print(f"  Hour {hour_idx} ({period}) — ruled by {ruler}")
else:
    print("  (Could not calculate — using clock estimate)")
    weekday_names = ['Moon','Mars','Mercury','Jupiter','Venus','Saturn','Sun']
    chaldean = ['Sun','Venus','Mercury','Moon','Saturn','Jupiter','Mars']
    starter = weekday_names[now_local.weekday()]
    starter_idx = chaldean.index(starter)
    hour = now_local.hour
    ruler = chaldean[(starter_idx + hour) % 7]
    print(f"  Approximate hour ruled by {ruler}")

# === OVERALL ===
print("\n✦ OVERALL ENERGY ✦")
print("  The heavenly bodies shift and speak across time. Today's transiting")
print("  planets converse with the stars of your birth, activating threads of")
print("  destiny woven long ago. Note which houses are touched — therein lies")
print("  the day's medicine and its mirror.")
print()
print("  From the Sufi tradition: time is but a veil over the Eternal Present.")
print("  What the sky shows now is not new, but newly visible — a reminder")
print("  of what has always been. Walk with awareness, and let the heavens")
print("  be your guide, not your master. — Al-Tukhi, may his wisdom abide.")
print()
print("=" * 62)
