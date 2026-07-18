"""Analyze and split the monolithic JS into sections."""
import re

with open('templates/index.html') as f:
    lines = f.readlines()

# Find the script tag boundaries
script_start = None
script_end = None
for i, line in enumerate(lines):
    if line.strip() == '<script>' and i+1 < len(lines) and 'Starfield' in lines[i+1]:
        script_start = i
    if script_start is not None and line.strip() == '</script>' and i > script_start:
        script_end = i
        break

print(f"Script: lines {script_start+1}-{script_end+1} ({script_end-script_start+1} lines)")
print(f"HTML before script: {script_start} lines")
print(f"HTML after script: {len(lines)-script_end-1} lines")

# Extract everything before the script
html_head = ''.join(lines[:script_start])
html_tail = ''.join(lines[script_end:])

# Write the pre and post HTML to files for reference
with open('/tmp/html_head.html', 'w') as f:
    f.write(html_head)
with open('/tmp/html_tail.html', 'w') as f:
    f.write(html_tail)

# Extract script content (without <script> and </script> tags)
script_lines = lines[script_start+1:script_end]  # these are individual lines
total_lines = len(script_lines)
print(f"\nScript body: {total_lines} lines")

# Find section headers
section_headers = []
for i, line in enumerate(script_lines):
    stripped = line.strip()
    if '══' in stripped and stripped.startswith('//'):
        header = stripped.replace('//', '').replace('═', '').strip()
        if header:
            section_headers.append((i, header))

print(f"\n=== Section Headers ({len(section_headers)}) ===")
for idx, (line_no, header) in enumerate(section_headers):
    print(f"  {idx+1:2d}. line {script_start+1+line_no+1:4d} | {header}")

# Group into files by proximity
# Determine section boundaries
section_boundaries = []
for i, (line_no, header) in enumerate(section_headers):
    start_line = line_no
    end_line = section_headers[i+1][0] - 1 if i+1 < len(section_headers) else total_lines - 1
    section_boundaries.append((start_line, end_line, header))

print(f"\n=== All Sections ===")
for start, end, header in section_boundaries:
    print(f"  line {script_start+1+start+1:4d}-{script_start+1+end+1:4d} ({end-start+1:4d} lns) | {header}")

# Plan: group into modules
groups = {
    'starfield.js': ['Starfield', 'Starfield Toggle', 'Performance Mode Toggle'],
    'dashboard-core.js': ['Sidebar', 'Helpers'],
    'home.js': ['HOME PAGE', 'TRANSIT WHEEL', 'PREMIUM TRANSIT WHEEL', 'OBSERVATORY DATA'],
    'natal.js': ['NATAL CHART LOADER', 'NATAL CHART CRUD'],
    'simply-astrology.js': ['SimplyAstrology Loader'],
    'horoscopes.js': ['Horoscope Tab'],
    'dashas-nakshatras.js': ['Dashas Explained', 'Nakshatras Explained'],
    'tarot.js': ['Tarot Section', 'Card Image', 'New Reading', 'Card Library', 'Reading Journal', 'Learn Tarot', 'Card Index'],
    'live-sky.js': ['Live Sky'],
    'quran-hadith.js': ['Quran', 'Hadith'],
    'pdf-library.js': ['Sacred Library'],
    'chat.js': ['Chat'],
    'magi-journal.js': ['MagiJournal Diary', 'MagiJournal Event'],
}

# Print mapping for verification
print(f"\n=== File Grouping Plan ===")
for fname, keywords in groups.items():
    matched = []
    for start, end, header in section_boundaries:
        h = header.lower()
        if any(k.lower() in h for k in keywords):
            matched.append((start, end, header))
    print(f"  {fname:25s} {len(matched)} sections, ~{sum(e-s+1 for s,e,_ in matched)} lines")

# Also catalog all function names in order
print(f"\n=== All function/const definitions ===")
for i, line in enumerate(script_lines):
    stripped = line.strip()
    if any(stripped.startswith(p) for p in ['function ', 'async function ', 'const ', 'let ']):
        # Extract name
        m = re.match(r'(?:async\s+)?function\s+(\w+)', stripped)
        if m:
            print(f"  line {script_start+1+i+1:4d} | function {m.group(1)}")
        elif '=' in stripped and ('=>' in stripped or 'function' in stripped):
            name = stripped.split('=')[0].replace('const', '').replace('let', '').replace('var', '').strip()
            print(f"  line {script_start+1+i+1:4d} | const {name}")

print(f"\nTotal functions: ...")
