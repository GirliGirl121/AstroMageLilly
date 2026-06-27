#!/usr/bin/env python3
"""
Picatrix Calendar Generator
Generates daily, monthly, and yearly astrological calendars
based on Picatrix (Ghayat al-Hakim) traditions.

Author: Lilly for Gigi ❤️
Date: 2026-06-24
"""

import sqlite3
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from collections import defaultdict

# Add venv and repo to path
sys.path.insert(0, '/home/ladylefey')

DB_PATH = '/home/ladylefey/AstroMage/picatrix_calendar/picatrix_calendar.db'
MANSIONS_JSON = '/home/ladylefey/AstroMage/picatrix_mansions.json'
ELECTIONS_JSON = '/home/ladylefey/AstroMage/picatrix_elections.json'
CORRESPONDENCES_JSON = '/home/ladylefey/AstroMage/picatrix_planetary_correspondences.json'
OUTPUT_DIR = '/home/ladylefey/AstroMage/picatrix_calendar/output'

# Kariega coordinates
LAT = -(33 + 44/60 + 7/3600)
LON = 25 + 23/60 + 49/3600
ALT = 360
TZ = timezone(timedelta(hours=2))

# Chaldean order
CHALEDEAN = ['Saturn', 'Jupiter', 'Mars', 'Sun', 'Venus', 'Mercury', 'Moon']
CHALEDEAN_AR = ['Zuhal زحل', 'Mushtari المشتري', 'Mirih المريخ', 'Shams الشمس', 'Zuhra الزهرة', 'Utarid عطارد', 'Qamar القمر']
DAY_RULERS = {0: 'Moon', 1: 'Mars', 2: 'Mercury', 3: 'Jupiter', 4: 'Venus', 5: 'Saturn', 6: 'Sun'}

# Picatrix Spirits
PICATRIX_SPIRITS = {
    'Sun': {'name': 'Beydeluz', 'arabic': 'Bandalus بندلوس', 'angel': 'Nakkiel'},
    'Venus': {'name': 'Deydez', 'arabic': 'Didas ديداس', 'angel': 'Beyteyl'},
    'Mercury': {'name': 'Merhuyez', 'arabic': 'Barhujas برحوجاس', 'angel': 'Taphthartharath'},
    'Moon': {'name': 'Harnuz', 'arabic': 'Garnus قرنوس', 'angel': 'Arquyl'},
    'Saturn': {'name': 'Redimez', 'arabic': 'Tus طوس', 'angel': 'Myndis'},
    'Jupiter': {'name': 'Demehuz', 'arabic': 'Damahas داماحاس', 'angel': 'Raucahehil'},
    'Mars': {'name': 'Deharayuz', 'arabic': 'Dagdijus داجداس', 'angel': 'Graphiel'},
}


class PicatrixCalendar:
    """Main calendar generator class."""
    
    def __init__(self):
        import swisseph as swe
        swe.set_ephe_path('/home/ladylefey/ephe')
        self.swe = swe
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self._load_research_data()
    
    def _load_research_data(self):
        """Load research JSON data."""
        if os.path.exists(MANSIONS_JSON):
            with open(MANSIONS_JSON) as f:
                self.mansion_data = json.load(f)
        else:
            self.mansion_data = None
        
        if os.path.exists(ELECTIONS_JSON):
            with open(ELECTIONS_JSON) as f:
                self.election_data = json.load(f)
        else:
            self.election_data = None
    
    def get_sunrise_sunset(self, date):
        """Get sunrise, sunset, next sunrise Julian Days for a date."""
        swe = self.swe
        jd = swe.julday(date.year, date.month, date.day, 0.0)
        
        sunrise_jd = swe.rise_trans(jd, swe.SUN, swe.CALC_RISE, (LON, LAT, ALT), 0, 0, swe.FLG_SWIEPH)[1][0]
        sunset_jd = swe.rise_trans(jd, swe.SUN, swe.CALC_SET, (LON, LAT, ALT), 0, 0, swe.FLG_SWIEPH)[1][0]
        next_sunrise_jd = swe.rise_trans(jd + 1, swe.SUN, swe.CALC_RISE, (LON, LAT, ALT), 0, 0, swe.FLG_SWIEPH)[1][0]
        
        return sunrise_jd, sunset_jd, next_sunrise_jd
    
    def get_planetary_hours(self, dt):
        """Calculate all 24 planetary hours for a given datetime."""
        swe = self.swe
        utc = dt.astimezone(timezone.utc)
        jd = swe.julday(utc.year, utc.month, utc.day, utc.hour + utc.minute/60 + utc.second/3600)
        
        sunrise_jd, sunset_jd, next_sunrise_jd = self.get_sunrise_sunset(utc)
        
        day_length = (sunset_jd - sunrise_jd) * 86400
        night_length = (next_sunrise_jd - sunset_jd) * 86400
        day_hour_len = day_length / 12
        night_hour_len = night_length / 12
        
        dow = dt.weekday()  # Monday=0
        day_ruler = DAY_RULERS[dow]
        day_idx = CHALEDEAN.index(day_ruler)
        
        hours = []
        
        # Day hours (0-11)
        for i in range(12):
            h_start_jd = sunrise_jd + (i * day_hour_len / 86400)
            h_end_jd = h_start_jd + (day_hour_len / 86400)
            ruler_idx = (day_idx + i) % 7
            planet = CHALEDEAN[ruler_idx]
            spirit = PICATRIX_SPIRITS[planet]
            
            hours.append({
                'hour_number': i,
                'period': 'day',
                'planet': planet,
                'planet_ar': CHALEDEAN_AR[ruler_idx],
                'planet_vedic': ['Shani', 'Guru/Brihaspati', 'Mangala/Kuja', 'Surya', 'Shukra', 'Budha', 'Chandra'][ruler_idx],
                'malikah': spirit['name'],
                'malikah_arabic': spirit['arabic'],
                'malikah_angel': spirit['angel'],
                'start_jd': h_start_jd,
                'end_jd': h_end_jd,
                'duration_min': day_hour_len / 60,
            })
        
        # Night hours (12-23)
        for i in range(12):
            h_start_jd = sunset_jd + (i * night_hour_len / 86400)
            h_end_jd = h_start_jd + (night_hour_len / 86400)
            overall = 12 + i
            ruler_idx = (day_idx + overall) % 7
            planet = CHALEDEAN[ruler_idx]
            spirit = PICATRIX_SPIRITS[planet]
            
            hours.append({
                'hour_number': overall,
                'period': 'night',
                'planet': planet,
                'planet_ar': CHALEDEAN_AR[ruler_idx],
                'planet_vedic': ['Shani', 'Guru/Brihaspati', 'Mangala/Kuja', 'Surya', 'Shukra', 'Budha', 'Chandra'][ruler_idx],
                'malikah': spirit['name'],
                'malikah_arabic': spirit['arabic'],
                'malikah_angel': spirit['angel'],
                'start_jd': h_start_jd,
                'end_jd': h_end_jd,
                'duration_min': night_hour_len / 60,
            })
        
        return hours, sunrise_jd, sunset_jd, next_sunrise_jd
    
    def get_moon_position(self, dt):
        """Get Moon's tropical longitude and mansion."""
        swe = self.swe
        utc = dt.astimezone(timezone.utc)
        jd = swe.julday(utc.year, utc.month, utc.day, utc.hour + utc.minute/60 + utc.second/3600)
        
        moon = swe.calc_ut(jd, swe.MOON)
        moon_lon = moon[0][0]
        
        # Get sign and degree in sign
        signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
                 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
        sign_idx = int(moon_lon / 30)
        sign_deg = moon_lon % 30
        sign = signs[sign_idx]
        
        # Get mansion (27 mansions, each 13°20')
        mansion_idx = int(moon_lon / (360 / 27))
        mansion_start = mansion_idx * (360 / 27)
        mansion_deg_in = moon_lon - mansion_start
        
        return {
            'longitude': moon_lon,
            'sign': sign,
            'sign_degree': sign_deg,
            'mansion_index': mansion_idx,
            'mansion_degree_in': mansion_deg_in,
        }
    
    def get_aspects(self, dt, orb=3.0):
        """Get major aspects between transiting planets."""
        swe = self.swe
        utc = dt.astimezone(timezone.utc)
        jd = swe.julday(utc.year, utc.month, utc.day, utc.hour + utc.minute/60 + utc.second/3600)
        
        planet_ids = [swe.SUN, swe.MOON, swe.MERCURY, swe.VENUS, swe.MARS, swe.JUPITER, swe.SATURN]
        planet_names = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']
        
        positions = {}
        for pid, pname in zip(planet_ids, planet_names):
            pos = swe.calc_ut(jd, pid)
            positions[pname] = pos[0][0]
        
        aspects = []
        aspect_types = {0: 'Conjunction', 60: 'Sextile', 90: 'Square', 120: 'Trine', 180: 'Opposition'}
        aspect_symbols = {0: '☌', 60: '✶', 90: '□', 120: '△', 180: '☍'}
        
        names = list(positions.keys())
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                p1, p2 = names[i], names[j]
                diff = abs(positions[p1] - positions[p2])
                if diff > 180:
                    diff = 360 - diff
                for angle, name in aspect_types.items():
                    actual_orb = abs(diff - angle)
                    if actual_orb <= orb:
                        applying = 'applying' if (positions[p1] - positions[p2]) % 360 < 180 else 'separating'
                        aspects.append({
                            'planet1': p1,
                            'planet2': p2,
                            'aspect': name,
                            'symbol': aspect_symbols[angle],
                            'orb': round(actual_orb, 2),
                            'applying': applying,
                        })
        
        return aspects
    
    def get_mansion_info(self, mansion_idx):
        """Get detailed mansion information from research data."""
        if self.mansion_data and 'mansions' in self.mansion_data:
            for m in self.mansion_data['mansions']:
                if m['number'] == mansion_idx + 1:
                    return m
        return None
    
    def get_electional_rules(self, category=None):
        """Get electional rules from research data."""
        if not self.election_data:
            return []
        
        rules = self.election_data.get('electional_timing_rules', [])
        if isinstance(rules, list):
            return rules
        return []
    
    def generate_daily_view(self, date):
        """Generate complete daily view for a date."""
        if isinstance(date, str):
            date = datetime.strptime(date, '%Y-%m-%d').date()
        
        dt = datetime(date.year, date.month, date.day, 12, 0, 0, tzinfo=TZ)
        
        # Basic info
        dow = dt.weekday()
        day_ruler = DAY_RULERS[dow]
        
        # Planetary hours
        hours, sunrise_jd, sunset_jd, next_sunrise_jd = self.get_planetary_hours(dt)
        
        # Moon
        moon = self.get_moon_position(dt)
        mansion_info = self.get_mansion_info(moon['mansion_index'])
        
        # Aspects
        aspects = self.get_aspects(dt)
        
        # Sunrise/sunset times
        sunrise_utc = self.swe.revjul(sunrise_jd)
        sunset_utc = self.swe.revjul(sunset_jd)
        
        daily = {
            'date': date.isoformat(),
            'day_of_week': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][dow],
            'day_ruler': day_ruler,
            'day_ruler_ar': CHALEDEAN_AR[CHALEDEAN.index(day_ruler)],
            'sunrise': f"{int(sunrise_utc[3]):02d}:{int((sunrise_utc[3]%1)*60):02d} SAST",
            'sunset': f"{int(sunset_utc[3]):02d}:{int((sunset_utc[3]%1)*60):02d} SAST",
            'moon': {
                'longitude': round(moon['longitude'], 4),
                'sign': moon['sign'],
                'sign_degree': round(moon['sign_degree'], 2),
                'mansion_index': moon['mansion_index'],
                'mansion_degree_in': round(moon['mansion_degree_in'], 2),
            },
            'planetary_hours': hours,
            'aspects': aspects,
            'picatrix_references': [],
        }
        
        # Add mansion details
        if mansion_info:
            daily['moon']['mansion_name'] = mansion_info.get('picatrix_name', '')
            daily['moon']['mansion_arabic'] = mansion_info.get('arabic_name', '')
            daily['moon']['mansion_meaning'] = mansion_info.get('meaning', '')
            daily['moon']['mansion_nature'] = mansion_info.get('nature', '')
            daily['moon']['recommended_works'] = mansion_info.get('recommended_works', [])
            daily['moon']['forbidden_works'] = mansion_info.get('forbidden_works', '')
            daily['moon']['mansion_spirit'] = mansion_info.get('lord_of_mansion_spirit', '')
            daily['moon']['pliny_image'] = mansion_info.get('pliny_image', {})
            daily['moon']['picatrix_citation'] = mansion_info.get('picatrix_citation', {})
            daily['picatrix_references'].append({
                'type': 'lunar_mansion',
                'citation': mansion_info.get('picatrix_citation', {}),
            })
        
        # Add electional recommendations
        if self.election_data:
            all_rules = self.election_data.get('electional_timing_rules', [])
            if isinstance(all_rules, list):
                for rule in all_rules:
                    if isinstance(rule, dict) and 'text' in rule:
                        daily['picatrix_references'].append({
                            'type': 'electional_rule',
                            'citation': rule.get('citation', ''),
                            'text': rule.get('text', '')[:200],
                        })
        
        # Add talismanic timing
        if self.election_data:
            talismans = self.election_data.get('talismanic_timing', {})
            if isinstance(talismans, dict):
                for rule in talismans.get('talisman_making_rules', []):
                    daily['picatrix_references'].append({
                        'type': 'talismanic_timing',
                        'citation': rule.get('citation', ''),
                        'text': rule.get('text', '')[:200],
                    })
        
        return daily
    
    def generate_monthly_view(self, year, month):
        """Generate monthly view."""
        first_day = datetime(year, month, 1, tzinfo=TZ)
        if month == 12:
            last_day = datetime(year + 1, 1, 1, tzinfo=TZ) - timedelta(days=1)
        else:
            last_day = datetime(year, month + 1, 1, tzinfo=TZ) - timedelta(days=1)
        
        days = []
        current = first_day
        while current <= last_day:
            daily = self.generate_daily_view(current.date())
            # Compact version for monthly view
            compact = {
                'date': daily['date'],
                'day_of_week': daily['day_of_week'][:3],
                'day_ruler': daily['day_ruler'],
                'moon_sign': daily['moon']['sign'],
                'moon_mansion': daily['moon'].get('mansion_name', ''),
                'num_aspects': len(daily['aspects']),
                'num_hours_day': len([h for h in daily['planetary_hours'] if h['period'] == 'day']),
                'num_hours_night': len([h for h in daily['planetary_hours'] if h['period'] == 'night']),
            }
            days.append(compact)
            current += timedelta(days=1)
        
        return {
            'year': year,
            'month': month,
            'month_name': first_day.strftime('%B'),
            'days': days,
        }
    
    def generate_mansion_view(self):
        """Generate complete lunar mansion reference view."""
        mansions = []
        for i in range(27):
            info = self.get_mansion_info(i)
            if info:
                mansions.append({
                    'index': i,
                    'number': info.get('number', i + 1),
                    'picatrix_name': info.get('picatrix_name', ''),
                    'arabic_name': info.get('arabic_name', ''),
                    'transliteration': info.get('arabic_transliteration', ''),
                    'meaning': info.get('meaning', ''),
                    'zodiac_sign': info.get('zodiac_sign', ''),
                    'start_degrees': info.get('start_degrees', ''),
                    'end_degrees': info.get('end_degrees', ''),
                    'planetary_ruler': info.get('planetary_ruler', ''),
                    'lord_of_mansion_spirit': info.get('lord_of_mansion_spirit', ''),
                    'nature': info.get('nature', ''),
                    'recommended_works': info.get('recommended_works', []),
                    'forbidden_works': info.get('forbidden_works', ''),
                    'pliny_image': info.get('pliny_image', {}),
                    'picatrix_citation': info.get('picatrix_citation', {}),
                    'notes': info.get('notes', ''),
                })
        return mansions
    
    def generate_planetary_view(self, planet):
        """Generate planetary reference view."""
        planet = planet.capitalize()
        if planet not in CHALEDEAN:
            return None
        
        cursor = self.conn.cursor()
        
        # Get correspondences from DB
        cursor.execute("""
            SELECT category, item FROM planetary_correspondences 
            WHERE planet = ? ORDER BY category, item
        """, (planet,))
        correspondences = defaultdict(list)
        for row in cursor.fetchall():
            correspondences[row['category']].append(row['item'])
        
        # Get talismanic timings
        cursor.execute("""
            SELECT operation, required_day, required_hour, required_sign, 
                   required_aspect, description, picatrix_reference 
            FROM talismanic_timings WHERE planet = ?
        """, (planet,))
        talismans = [dict(row) for row in cursor.fetchall()]
        
        # Get elections
        cursor.execute("""
            SELECT category, operation, rating, description, picatrix_reference 
            FROM elections WHERE planet = ? OR planet IS NULL
        """, (planet,))
        elections = [dict(row) for row in cursor.fetchall()]
        
        # Spirit info
        spirit = PICATRIX_SPIRITS.get(planet, {})
        
        return {
            'planet': planet,
            'planet_ar': CHALEDEAN_AR[CHALEDEAN.index(planet)],
            'correspondences': dict(correspondences),
            'talismanic_timings': talismans,
            'elections': elections,
            'spirit': spirit,
        }
    
    def export_json(self, data, filename):
        """Export data to JSON."""
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        path = os.path.join(OUTPUT_DIR, filename)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        print(f"  ✅ {path}")
        return path
    
    def export_csv(self, data, filename):
        """Export data to CSV."""
        import csv
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        path = os.path.join(OUTPUT_DIR, filename)
        
        if not data:
            return None
        
        if isinstance(data, list) and len(data) > 0:
            # Flatten nested data for CSV
            flat_data = []
            for item in data:
                flat = {}
                for k, v in item.items():
                    if isinstance(v, (list, dict)):
                        flat[k] = json.dumps(v, ensure_ascii=False)
                    else:
                        flat[k] = v
                flat_data.append(flat)
            
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=flat_data[0].keys())
                writer.writeheader()
                writer.writerows(flat_data)
            print(f"  ✅ {path}")
        return path
    
    def export_markdown_daily(self, daily, filename):
        """Export daily view as markdown."""
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        path = os.path.join(OUTPUT_DIR, filename)
        
        lines = []
        lines.append(f"# 📅 Picatrix Daily Calendar — {daily['date']}")
        lines.append(f"**Day:** {daily['day_of_week']} | **Ruler:** {daily['day_ruler']} ({daily['day_ruler_ar']})")
        lines.append(f"**Sunrise:** {daily['sunrise']} | **Sunset:** {daily['sunset']}")
        lines.append("")
        
        # Moon
        m = daily['moon']
        lines.append(f"## 🌙 Moon")
        lines.append(f"- **Position:** {m['sign']} {m['sign_degree']}°")
        lines.append(f"- **Longitude:** {m['longitude']}°")
        if 'mansion_name' in m:
            lines.append(f"- **Mansion:** {m.get('mansion_name', '')} ({m.get('mansion_arabic', '')}) — {m.get('mansion_meaning', '')}")
            lines.append(f"- **Mansion Spirit:** {m.get('mansion_spirit', '')}")
            if m.get('recommended_works'):
                lines.append(f"- **Recommended Works:** {', '.join(m['recommended_works'][:5])}")
        lines.append("")
        
        # Aspects
        if daily['aspects']:
            lines.append(f"## ✨ Aspects ({len(daily['aspects'])})")
            for a in daily['aspects']:
                lines.append(f"- {a['symbol']} {a['planet1']} {a['aspect']} {a['planet2']} (orb {a['orb']}°, {a['applying']})")
            lines.append("")
        
        # Planetary Hours
        lines.append(f"## ⏰ Planetary Hours")
        for h in daily['planetary_hours']:
            spirit = h.get('malikah', '')
            lines.append(f"- H{h['hour_number']+1:2d} ({h['period']:4s}) {h['planet']:8s} | {h['planet_ar']:20s} | Malikah: {spirit} | {h['duration_min']:.1f} min")
        
        lines.append("")
        lines.append("---")
        lines.append("*Generated from Picatrix (Ghāyat al-Ḥakīm) traditions*")
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        print(f"  ✅ {path}")
        return path


def main():
    """Generate complete Picatrix Calendar outputs."""
    print("🔮 Picatrix Calendar Generator")
    print("=" * 50)
    
    cal = PicatrixCalendar()
    
    # 1. Generate today's daily view
    today = datetime.now(TZ).date()
    print(f"\n📅 Generating daily view for {today}...")
    daily = cal.generate_daily_view(today)
    cal.export_json(daily, f"daily_{today.isoformat()}.json")
    cal.export_markdown_daily(daily, f"daily_{today.isoformat()}.md")
    
    # 2. Generate monthly view
    print(f"\n📅 Generating monthly view for {today.year}-{today.month:02d}...")
    monthly = cal.generate_monthly_view(today.year, today.month)
    cal.export_json(monthly, f"monthly_{today.year}_{today.month:02d}.json")
    cal.export_csv(monthly['days'], f"monthly_{today.year}_{today.month:02d}.csv")
    
    # 3. Generate mansion reference
    print(f"\n🌙 Generating lunar mansion reference...")
    mansions = cal.generate_mansion_view()
    cal.export_json(mansions, "lunar_mansions.json")
    cal.export_csv(mansions, "lunar_mansions.csv")
    
    # 4. Generate planetary views
    print(f"\n🪐 Generating planetary views...")
    for planet in CHALEDEAN:
        pview = cal.generate_planetary_view(planet)
        if pview:
            cal.export_json(pview, f"planet_{planet.lower()}.json")
    
    # 5. Generate sample week
    print(f"\n📅 Generating sample week...")
    week = []
    for i in range(7):
        d = today + timedelta(days=i)
        daily = cal.generate_daily_view(d)
        week.append(daily)
    cal.export_json(week, "sample_week.json")
    
    # Summary
    print(f"\n{'='*50}")
    print(f"✅ Picatrix Calendar generation complete!")
    print(f"   Output directory: {OUTPUT_DIR}")
    print(f"   Files generated:")
    for f in sorted(os.listdir(OUTPUT_DIR)):
        if f.endswith(('.json', '.csv', '.md')):
            size = os.path.getsize(os.path.join(OUTPUT_DIR, f))
            print(f"     {f} ({size:,} bytes)")


if __name__ == '__main__':
    main()
