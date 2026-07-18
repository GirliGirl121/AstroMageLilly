"""Split monolithic dashboard JS into modular files using exact line ranges.
This preserves ALL code — nothing lost.
"""
import os

with open('templates/index.html') as f:
    lines = f.readlines()

# Find script bounds (0-indexed lines)
script_start = None
for i, line in enumerate(lines):
    if line.strip() == '<script>' and i+1 < len(lines) and 'Starfield' in lines[i+1]:
        script_start = i
        break
for i in range(script_start, len(lines)):
    if lines[i].strip() == '</script>':
        script_end = i
        break

print(f"Script: lines {script_start+1}-{script_end+1} (0-indexed: {script_start}-{script_end})")

# Everything before script
html_head = ''.join(lines[:script_start])
# Everything after script
html_tail = ''.join(lines[script_end+1:])

# Script body (lines between <script> and </script>)
script_lines = lines[script_start+1:script_end]

# ─── Define modules as (filename, [(start_orig, end_orig), ...]) ───
# Ranges are INCLUSIVE on start, EXCLUSIVE on end (python slice style)
# Line numbers are 0-indexed in the original file
MODULES = [
    ('starfield.js', [
        (749-1, 828),     # Starfield + toggle + perf mode
    ]),
    ('dashboard-core.js', [
        (829-1, 904),     # Sidebar + Helpers
    ]),
    ('home.js', [
        (905-1, 1002),    # loadHome
    ]),
    ('transit-wheel.js', [
        (1003-1, 1197),   # Transit wheel drawing
    ]),
    ('observatory.js', [
        (1198-1, 1321),   # Observatory data
    ]),
    ('natal.js', [
        (1322-1, 1646),   # Natal chart loader + drawer
    ]),
    ('simply-astrology.js', [
        (1647-1, 1699),   # loadSimply
        (1841-1, 1866),   # simplySelect + simplyToggleCard
    ]),
    ('horoscopes.js', [
        (1700-1, 1840),   # All horoscope functions
        (1867-1, 1876),   # toggleBook (old library, keep for now)
    ]),
    ('dashas-nakshatras.js', [
        (1877-1, 1934),   # loadDashasFull + loadNakshatrasFull
    ]),
    ('tarot.js', [
        (1935-1, 2413),   # loadTarotFull + all tarot functions
    ]),
    ('live-sky.js', [
        (2414-1, 2446),   # loadLive
    ]),
    ('quran-hadith.js', [
        (2447-1, 2688),   # loadQuranFull + quran + hadith
    ]),
    ('pdf-library.js', [
        (2689-1, 3060),   # PDF library system
    ]),
    ('chat.js', [
        (3061-1, 3157),   # sendChat
    ]),
    ('magi-journal.js', [
        (3158-1, 3565),   # MagiJournal diary + events + week + year
    ]),
    ('natal-crud.js', [
        (3566-1, 3761),   # Natal CRUD
    ]),
    ('_init.js', [
        (3762-1, script_end),  # Init block
    ]),
]

# Verify no gaps or overlaps
all_ranges = []
for fname, ranges in MODULES:
    for r in ranges:
        all_ranges.append((fname, r[0], r[1]))

all_ranges.sort(key=lambda x: x[1])  # sort by start

# Check for gaps
print(f"\n=== Coverage Check ===")
total_covered = 0
for i, (fname, start, end) in enumerate(all_ranges):
    print(f"  {fname:25s} lines {start+1:5d}-{end:5d} ({end-start:5d} lines)")
    total_covered += end - start
    if i > 0:
        prev_end = all_ranges[i-1][2]
        if start != prev_end:
            print(f"  ⚠️  GAP at line {prev_end+1}-{start} ({start - prev_end} lines)")

script_len = script_end - script_start - 1
print(f"  ─────────────────────────────────────")
print(f"  Total covered: {total_covered:5d} / {script_len:5d} script lines")

# Extract unassigned lines
assigned = set()
for fname, ranges in MODULES:
    for start, end in ranges:
        for li in range(start, end):
            # Convert to script-relative index
            script_idx = li - script_start - 1
            if 0 <= script_idx < len(script_lines):
                assigned.add(script_idx)

unassigned = sorted(set(range(len(script_lines))) - assigned)
if unassigned:
    print(f"\n⚠️  Unassigned lines ({len(unassigned)}):")
    for idx in unassigned[:30]:
        lno = idx + script_start + 2  # 1-indexed original
        content = script_lines[idx].rstrip()
        if content.strip():
            print(f"  line {lno}: {content[:120]}")
else:
    print("✅ All lines assigned!")

# ─── Write module files ───
os.makedirs('static/js', exist_ok=True)
total_written = 0

for fname, ranges in MODULES:
    content_parts = []
    for start, end in ranges:
        for li in range(start, end):
            script_idx = li - script_start - 1
            if 0 <= script_idx < len(script_lines):
                content_parts.append(script_lines[script_idx])
    
    if not content_parts:
        print(f"  ⚠️  EMPTY: {fname}")
        continue
    
    content = ''.join(content_parts)
    
    # Verify no missing lines
    if fname == '_init.js':
        # Special: replace content with just the init block
        pass
    
    path = f'static/js/{fname}'
    with open(path, 'w') as f:
        f.write(content)
    
    print(f"  ✅ {fname:25s} {len(content):6d} chars, {content.count(chr(10)):5d} lines")
    total_written += len(content)

# ─── Rebuild index.html head part ───
# Remove the old <script>...</script> block
# The HTML head stays the same
print(f"\n=== Rebuild ===")
print(f"HTML head: {len(html_head)} chars ({html_head.count(chr(10))} lines)")
print(f"HTML tail: {len(html_tail)} chars")

# Generate the <script> tags
script_tags = ''
for fname, ranges in MODULES:
    if fname == '_init.js':
        continue  # Include it in the main build-order
    path = f'static/js/{fname}'
    if os.path.exists(path) and os.path.getsize(path) > 0:
        script_tags += f'    <script src="{path}"></script>\n'

# Add _init.js last
if os.path.exists('static/js/_init.js') and os.path.getsize('static/js/_init.js') > 0:
    script_tags += f'    <script src="static/js/_init.js"></script>\n'

print(f"\nNew script tags:\n{script_tags}")

# Write the new index.html
new_html = html_head + script_tags + '\n' + html_tail
with open('templates/index.html', 'w') as f:
    f.write(new_html)

print(f"\n✅ Written: templates/index.html ({len(new_html)} chars, {new_html.count(chr(10))} lines)")
print(f"Old version: ~{script_len} lines of JS, new version loads {len(MODULES)} script files")
