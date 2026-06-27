# Picatrix Astrological Calendar

A comprehensive, searchable, and navigable calendar system based on the **Picatrix (Ghāyat al-Ḥakīm)** and related medieval Arabic astrological-magical traditions.

## Overview

This calendar organizes all time-sensitive astrological and magical information from the Picatrix into structured database and output formats.

## Project Structure

```
/home/ladylefey/AstroMage/picatrix_calendar/
├── schema.py              # SQLite database schema + reference data loader
├── generator.py           # Calendar generator (daily/monthly/mansion/planetary views)
├── picatrix_calendar.db   # SQLite database with all reference data
├── output/                # Generated output files
│   ├── daily_YYYY-MM-DD.json    # Daily view (JSON)
│   ├── daily_YYYY-MM-DD.md      # Daily view (Markdown)
│   ├── monthly_YYYY_MM.json     # Monthly view (JSON)
│   ├── monthly_YYYY_MM.csv      # Monthly view (CSV)
│   ├── lunar_mansions.json      # Complete mansion reference
│   ├── lunar_mansions.csv       # Mansion reference (CSV)
│   ├── planet_*.json            # Planetary correspondence views
│   └── sample_week.json         # 7-day sample
└── README.md              # This file
```

## Source Data

Research JSON files extracted from the Picatrix:
- `/home/ladylefey/AstroMage/picatrix_mansions.json` — Lunar mansions with spirits, images, operations
- `/home/ladylefey/AstroMage/picatrix_elections.json` — Electional rules, fixed stars, weather, agriculture, medical, ritual
- `/home/ladylefey/AstroMage/picatrix_planetary_correspondences.json` — Planetary tables

## Database Schema

### Tables

| Table | Description |
|-------|-------------|
| `calendar_dates` | Per-date astronomical data (sunrise, sunset, day ruler) |
| `planetary_hours` | 24 planetary hours per date with malikah spirits |
| `moon_data` | Moon position, sign, mansion per date |
| `planetary_aspects` | Major aspects between transiting planets |
| `elections` | Electional rules (recommended/forbidden operations) |
| `lunar_mansions_reference` | Complete 27-mansion reference |
| `planetary_correspondences` | Colors, metals, stones, incenses per planet |
| `fixed_stars` | Fixed stars with Picatrix references |
| `seasonal_correspondences` | Seasonal operations by sign |
| `talismanic_timings` | Talisman-making timing rules |

## Usage

### Generate Calendar
```bash
source /home/ladylefey/venv/bin/activate
python3 /home/ladylefey/AstroMage/picatrix_calendar/generator.py
```

### Query Database
```bash
sqlite3 /home/ladylefey/AstroMage/picatrix_calendar/picatrix_calendar.db
SELECT * FROM lunar_mansions_reference WHERE element = 'Fire';
SELECT * FROM planetary_correspondences WHERE planet = 'Venus' AND category = 'stone';
SELECT * FROM talismanic_timings WHERE planet = 'Mars';
```

### Python API
```python
from generator import PicatrixCalendar

cal = PicatrixCalendar()
daily = cal.generate_daily_view('2026-06-24')
monthly = cal.generate_monthly_view(2026, 6)
mansions = cal.generate_mansion_view()
planet = cal.generate_planetary_view('Venus')
```

## Calendar Views

### Daily View
- Date, day ruler, sunrise/sunset
- Moon position (longitude, sign, mansion)
- Mansion spirit and recommended works
- Major planetary aspects
- All 24 planetary hours with Picatrix malikah spirits
- Picatrix source citations

### Monthly View
- Compact daily summaries for a month
- Moon sign changes, mansion transitions
- Aspect counts, hour distributions

### Lunar Mansion View (27 mansions)
- Arabic name, transliteration, Picatrix name
- Meaning, zodiac position, planetary ruler
- Mansion spirit (from Book IV, Chapter 9)
- Recommended works, forbidden works
- Pliny image descriptions
- Picatrix source citations

### Planetary View (7 planets)
- Colors, metals, stones, incenses
- Plants, animals, body parts, professions
- Talismanic timing rules
- Electional rules
- Malikah spirit and angel

## Sources

### Primary
- **Picatrix (Ghāyat al-Ḥakīm)** — Arabic text, translated by David Pingree (Warburg Institute)
- **Picatrix: The Latin Version** — ed. David Pingree
- **Picatrix: A Medieval Treatise on Astral Magic** — trans. John Michael Greer & Christopher Warnock

### Secondary / Cross-Reference
- **Abu Ma'shar** — Great Introduction to Astrology, On the Revolutions of the Years of the World
- **Al-Biruni** — The Book of Instruction in the Elements of the Art of Astrology
- **Al-Qabisi** — The Introduction to Astrology
- **Al-Kindi** — On the Stellar Rays
- **Ibn Arabi** — The Bezels of Wisdom (Fusus al-Hikam)
- **Nineveh Shadrach** — Magic That Works
- **Stephanie Johnson** — Lunar Mansions: The Arabs and the Moon

## Confidence Levels

- **high**: Directly stated in Picatrix text
- **medium**: Inferred from Picatrix context or well-attested secondary sources
- **low**: Modern interpretation or disputed attribution

## Notes

- All correspondences are from the Picatrix unless otherwise noted
- Lunar mansion system follows the Arabic 27-mansion tradition (not the Hindu 27 Nakshatra system, though they overlap)
- Planetary hours use sunrise-based unequal hours with continuous Chaldean sequence
- Coordinates default to Kariega, South Africa (33°44'S, 25°24'E)

## Generated Output Formats

| Format | Use Case |
|--------|----------|
| JSON | API consumption, further processing |
| CSV | Spreadsheet analysis, data science |
| Markdown | Human-readable reports |
| SQLite | Queryable database, application backend |

---

*Generated by Lilly for Gigi ❤️, 2026-06-24*
*Based on the Picatrix (Ghāyat al-Ḥakīm) tradition*
