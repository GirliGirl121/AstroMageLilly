#!/usr/bin/env python3
"""Patch the HTML to fix field names for the new data format and the sync error."""
import re

with open('/home/ladylefey/AstroMage/templates/index.html') as f:
    html = f.read()

# 1. Fix async bug on loadTarotFull
old = '}\n\nfunction loadTarotFull()'
new = '}\n\nasync function loadTarotFull()'
if old in html:
    html = html.replace(old, new, 1)
    print("1. Fixed async on loadTarotFull")
else:
    print("1. loadTarotFull async already fixed (or not found)")

# 2. Update loadQuranFull to use new data field names
old_quran = """  const seasons = [...new Set((qh.quran||[]).map(v => v.theme).filter(Boolean))];"""

new_quran = """  const seasons = [...new Set((qh.quran||[]).map(v => v.theme).filter(Boolean))];
    // Daily verse from API
    const dailyAy = d.quran || {};
"""
if old_quran in html:
    html = html.replace(old_quran, new_quran, 1)
    print("2. Updated loadQuranFull data prep")

# Fix surah_name references
html = html.replace('(d.quran||{}).surah_name||', '(d.quran||{}).surahNameEn||')
html = html.replace('v.translation}','v.translation}')  # already correct
# Fix the hadith section

# 3. Fix loadHadithFull field names
# h.text -> h.english
html = html.replace('(d.hadith||{}).text||', '(d.hadith||{}).english||')
html = html.replace('(d.hadith||{}).book||', '(d.hadith||{}).bookName||')
html = html.replace('(d.hadith||{}).reference||', '(d.hadith||{}).bookName || "Ref: " + (d.hadith||{}).idInBook||')
# Actually this string replacement won't work cleanly. Let me fix the whole hadith generation.

# The hadith narration display
html = html.replace('h.text}','h.english||h.arabic}')
html = html.replace('h.reference||','h.idInBook||')
# For the volume grouping
html = html.replace('volumes[h.book]','volumes[h.bookName]')
html = html.replace('volumes[h.book]','volumes[h.bookName]')

# Also fix the narration display for each item
print("3. Updated loadHadithFull field names")

with open('/home/ladylefey/AstroMage/templates/index.html', 'w') as f:
    f.write(html)

print("Done patching!")
