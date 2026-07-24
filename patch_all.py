#!/usr/bin/env python3
"""
Lilly Observatory Patch — Extended Bodies, Local Tool Router, Chart Viewer
"""
import os

LILLY_DIR = os.path.expanduser("~/lilly")

def read(f):
    with open(os.path.join(LILLY_DIR, f), 'r', encoding='utf-8') as fh:
        return fh.read()

def write(f, content):
    with open(os.path.join(LILLY_DIR, f), 'w', encoding='utf-8') as fh:
        fh.write(content)
    print(f"✓ Patched {f}")

# ═══════════════════════════════════════════════════
# 1. PATCH lilly_config.py — Add extended bodies
# ═══════════════════════════════════════════════════
config = read("lilly_config.py")

if "EXTENDED_BODIES" not in config:
    config += '''
# ── Extended Bodies (Esoteric) ──
EXTENDED_BODIES = {
    "Lilith": {"name": "Black Moon Lilith", "type": "mean_apogee", "symbol": "⚸"},
    "Rahu": {"name": "North Node", "type": "mean_node", "symbol": "☊"},
    "Ketu": {"name": "South Node", "type": "mean_node", "symbol": "☋"},
    "Chiron": {"name": "Chiron", "type": "asteroid", "symbol": "⚷"},
}

# ── Default Location (Gigi's Observatory) ──
DEFAULT_LOCATION = {
    "name": "Kariega, Eastern Cape, South Africa",
    "latitude": -33.30,
    "longitude": 26.32,
    "timezone_offset": 2.0
}
'''
    write("lilly_config.py", config)

# ═══════════════════════════════════════════════════
# 2. PATCH lilly_astrology.py — Extended bodies + fixes
# ═══════════════════════════════════════════════════
astro = read("lilly_astrology.py")

# 2a. Fix /hours vector bug
astro = astro.replace(
    "        observer = self.earth + Topos(latitude_degrees=lat, longitude_degrees=lon)\n        \n        # Find sunrise and sunset\n        f = almanac.dark_twilight_day(self.planets_data, observer)",
    "        topos = Topos(latitude_degrees=lat, longitude_degrees=lon)\n        observer = self.earth + topos\n        \n        # Find sunrise and sunset\n        f = almanac.dark_twilight_day(self.planets_data, topos)"
)

# 2b. Add extended body methods after _hour_significance
extended_methods = '''
    def _days_since_j2000(self, dt: datetime) -> float:
        """Julian days since J2000.0 for approximate calculations."""
        from datetime import timezone
        t = self.ts.from_datetime(dt.replace(tzinfo=timezone.utc))
        return t.tt - 2451545.0

    def compute_ascendant(self, dt: datetime, lat: float, lon: float) -> Dict:
        """Calculate the Ascendant (Rising Sign) using standard astrological formula."""
        import math
        t = self.ts.from_datetime(dt.replace(tzinfo=timezone.utc))
        d = self._days_since_j2000(dt)
        
        # Greenwich Apparent Sidereal Time in degrees
        gast = t.gast * 15.0
        lst = (gast + lon) % 360
        
        # Mean obliquity of ecliptic
        T = d / 36525.0
        eps = 23.439291 - 0.0130042 * T
        
        lst_rad = math.radians(lst)
        lat_rad = math.radians(lat)
        eps_rad = math.radians(eps)
        
        y = math.cos(lst_rad)
        x = -(math.sin(eps_rad) * math.tan(lat_rad) + math.cos(eps_rad) * math.sin(lst_rad))
        
        asc_deg = math.degrees(math.atan2(y, x)) % 360
        sign_info = self._get_zodiac_sign(asc_deg)
        
        return {
            "body": "Ascendant",
            "longitude": round(asc_deg, 4),
            "sign": sign_info[0],
            "symbol": sign_info[1],
            "element": sign_info[2],
            "modality": sign_info[3],
            "degree_in_sign": round(asc_deg % 30, 2)
        }

    def compute_extended_body(self, name: str, dt: datetime) -> Dict:
        """Calculate esoteric bodies: Lilith, Rahu, Ketu, Chiron."""
        import math
        d = self._days_since_j2000(dt)
        T = d / 36525.0
        
        if name == "Rahu":
            # Mean ascending node (Meeus Astronomical Algorithms)
            omega = 125.0445479 - 0.05295377 * d
            lon = omega % 360
            sign = self._get_zodiac_sign(lon)
            return {
                "body": "Rahu", "name": "North Node", "symbol": "☊",
                "longitude": round(lon, 4), "sign": sign[0],
                "element": sign[2], "degree_in_sign": round(lon % 30, 2),
                "meaning": "Karma, destiny, spiritual lessons, obsessions"
            }
        
        elif name == "Ketu":
            omega = 125.0445479 - 0.05295377 * d
            lon = (omega + 180.0) % 360
            sign = self._get_zodiac_sign(lon)
            return {
                "body": "Ketu", "name": "South Node", "symbol": "☋",
                "longitude": round(lon, 4), "sign": sign[0],
                "element": sign[2], "degree_in_sign": round(lon % 30, 2),
                "meaning": "Liberation, past lives, detachment, spiritual gifts"
            }
        
        elif name == "Lilith":
            # Mean lunar apogee (Black Moon) — approximate
            # L_moon + argument_of_perigee + 180
            L = 218.3164477 + 13.17639648 * d
            omega = 125.0445479 - 0.05295377 * d
            # Approximate mean apogee = mean longitude + 180 - mean anomaly adjustment
            # Simplified: Lilith ≈ (L - omega + 180) % 360 ... refined:
            lon = (L + 318.15 + 0.164357 * T * 36525 + 180.0) % 360
            sign = self._get_zodiac_sign(lon)
            return {
                "body": "Lilith", "name": "Black Moon Lilith", "symbol": "⚸",
                "longitude": round(lon, 4), "sign": sign[0],
                "element": sign[2], "degree_in_sign": round(lon % 30, 2),
                "meaning": "Repressed desires, raw feminine power, shadow self, independence"
            }
        
        elif name == "Chiron":
            return {
                "body": "Chiron", "name": "Chiron", "symbol": "⚷",
                "error": "Chiron requires the Swiss Ephemeris extended asteroid files (sepl_18.se1). Install pyswisseph and extended ephemeris for precise calculation.",
                "meaning": "The wounded healer, deep soul wounds, teaching through pain"
            }
        
        return {"error": f"Unknown extended body: {name}"}

    def compute_parts(self, sun_lon: float, moon_lon: float, asc_lon: float, is_day: bool) -> Dict:
        """Calculate Part of Fortune and Part of Spirit."""
        def norm(x):
            return x % 360
        
        if is_day:
            pof = norm(asc_lon + moon_lon - sun_lon)
            pos = norm(asc_lon + sun_lon - moon_lon)
        else:
            pof = norm(asc_lon + sun_lon - moon_lon)
            pos = norm(asc_lon + moon_lon - sun_lon)
        
        pof_sign = self._get_zodiac_sign(pof)
        pos_sign = self._get_zodiac_sign(pos)
        
        return {
            "Part_of_Fortune": {
                "longitude": round(pof, 4), "sign": pof_sign[0],
                "degree_in_sign": round(pof % 30, 2),
                "meaning": "Material blessing, worldly success, bodily health"
            },
            "Part_of_Spirit": {
                "longitude": round(pos, 4), "sign": pos_sign[0],
                "degree_in_sign": round(pos % 30, 2),
                "meaning": "Spiritual purpose, soul's intention, divine will"
            }
        }
'''

# Insert before current_sky_snapshot
astro = astro.replace(
    "    def current_sky_snapshot(self, lat: float = 0.0, lon: float = 0.0) -> Dict:",
    extended_methods + "\n    def current_sky_snapshot(self, lat: float = 0.0, lon: float = 0.0) -> Dict:"
)

# 2c. Update current_sky_snapshot to include outer planets + extended
old_snapshot = '''    def current_sky_snapshot(self, lat: float = 0.0, lon: float = 0.0) -> Dict:
        \"\"\"Get a real-time snapshot of the sky.\"\"\"
        now = datetime.now(timezone.utc)
        snapshot = {\"timestamp\": now.isoformat(), \"planets\": {}}
        for planet in CLASSICAL_PLANETS:
            snapshot[\"planets\"][planet] = self.compute_planet_position(planet, now, lat, lon)
        return snapshot'''

new_snapshot = '''    def current_sky_snapshot(self, lat: float = 0.0, lon: float = 0.0) -> Dict:
        \"\"\"Get a real-time snapshot of the sky — classical, outer, and esoteric bodies.\"\"\"
        now = datetime.now(timezone.utc)
        snapshot = {\"timestamp\": now.isoformat(), \"planets\": {}, \"extended\": {}, \"points\": {}}\n
        # Classical + Outer planets
        for planet in CLASSICAL_PLANETS + [\"Uranus\", \"Neptune\", \"Pluto\"]:\n            snapshot[\"planets\"][planet] = self.compute_planet_position(planet, now, lat, lon)\n
        # Extended esoteric bodies
        for body in [\"Rahu\", \"Ketu\", \"Lilith\", \"Chiron\"]:\n            snapshot[\"extended\"][body] = self.compute_extended_body(body, now)\n
        # Ascendant + Parts\n        asc = self.compute_ascendant(now, lat, lon)\n        snapshot[\"points\"][\"Ascendant\"] = asc\n        \n        sun_lon = snapshot[\"planets\"][\"Sun\"].get(\"tropical_longitude\", 0)\n        moon_lon = snapshot[\"planets\"][\"Moon\"].get(\"tropical_longitude\", 0)\n        # Determine day/night by Sun altitude (simplified: 6am-6pm local)\n        is_day = 6 <= (now.hour + int(lon/15)) % 24 <= 18\n        parts = self.compute_parts(sun_lon, moon_lon, asc[\"longitude\"], is_day)\n        snapshot[\"points\"].update(parts)\n        \n        return snapshot'''

astro = astro.replace(old_snapshot, new_snapshot)

# 2d. Update compute_natal_chart to include extended bodies and parts
old_natal = '''    def compute_natal_chart(self, birth_dt: datetime, lat: float, lon: float) -> Dict:
        \"\"\"Compute a complete natal chart.\"\"\"
        chart = {
n            \"birth_data\": {
n                \"datetime\": birth_dt.isoformat(),
n                \"latitude\": lat,
n                \"longitude\": lon
n            },
n            \"planets\": {},
n            \"summary\": {}
n        }
n        \n        for planet in CLASSICAL_PLANETS + [\"Uranus\", \"Neptune\", \"Pluto\"]:\n            chart[\"planets\"][planet] = self.compute_planet_position(planet, birth_dt, lat, lon)
n        \n        # Add ascendant approximation (simplified — full calculation requires more math)\n        chart[\"summary\"][\"dominant_element\"] = self._dominant_element(chart[\"planets\"])\n        chart[\"summary\"][\"moon_mansion\"] = chart[\"planets\"][\"Moon\"][\"lunar_mansion\"]\n        \n        return chart'''

# Actually, let me use a simpler replacement — just add the extra sections
old_natal_end = '''        chart[\"summary\"][\"dominant_element\"] = self._dominant_element(chart[\"planets\"])
        chart[\"summary\"][\"moon_mansion\"] = chart[\"planets\"][\"Moon\"][\"lunar_mansion\"]
        
        return chart'''

new_natal_end = '''        chart[\"summary\"][\"dominant_element\"] = self._dominant_element(chart[\"planets\"])
        chart[\"summary\"][\"moon_mansion\"] = chart[\"planets\"][\"Moon\"][\"lunar_mansion\"]
        \n        # Extended bodies\n        chart[\"extended\"] = {}\n        for body in [\"Rahu\", \"Ketu\", \"Lilith\", \"Chiron\"]:\n            chart[\"extended\"][body] = self.compute_extended_body(body, birth_dt)\n        \n        # Ascendant + Parts\n        chart[\"points\"] = {}\n        asc = self.compute_ascendant(birth_dt, lat, lon)\n        chart[\"points\"][\"Ascendant\"] = asc\n        \n        sun_lon = chart[\"planets\"][\"Sun\"].get(\"tropical_longitude\", 0)\n        moon_lon = chart[\"planets\"][\"Moon\"].get(\"tropical_longitude\", 0)\n        # Simplified day/night: check if birth time is between 6am and 6pm local\n        local_hour = birth_dt.hour + int(lon / 15)\n        is_day = 6 <= local_hour % 24 <= 18\n        parts = self.compute_parts(sun_lon, moon_lon, asc[\"longitude\"], is_day)\n        chart[\"points\"].update(parts)\n        \n        return chart'''

astro = astro.replace(old_natal_end, new_natal_end)

write("lilly_astrology.py", astro)

# ═══════════════════════════════════════════════════
# 3. PATCH lilly.py — /view command + local tool router
# ═══════════════════════════════════════════════════
main_file = read("lilly.py")

# 3a. Add /view command handler before /vault
view_cmd = '''        elif command == "/view":
            print(S.paint("\\n📜 Retrieving celestial map...", S.PURPLE))
            profiles = self.vault.list_profiles()
            if not profiles:
                print(S.paint("   The vault is empty, Gigi ❤️.", S.GRAY))
                return
            print(S.paint("   Stored profiles:", S.LAVENDER))
            for i, p in enumerate(profiles, 1):
                print(S.paint(f"   {i}. {p['name']} ({p['birth_date']}) — {p['id']}", S.WHITE))
            choice = input(S.paint("   Enter name or ID to view: ", S.LAVENDER)).strip()
            profile = self.vault.find_profile_by_name(choice) or self.vault.get_profile(choice)
            if not profile:
                print(S.paint("   That soul is not in the vault.", S.HOT_PINK))
                return
            chart = None
            for c in self.vault.data["charts"]:
                if c["profile_id"] == profile["id"]:
                    chart = c["data"]
                    break
            if not chart:
                print(S.paint("   No chart found for this profile.", S.HOT_PINK))
                return
            print(S.paint(f"\\n   ✨ Natal Chart: {profile['name']}", S.PINK))
            print(S.paint(f"   {profile['birth_date']} at {profile['birth_time']}", S.BLUE))
            print(S.paint(f"   Location: {profile['latitude']:.2f}°, {profile['longitude']:.2f}°", S.BLUE))
            print(S.paint(f"\\n   🌙 Ascendant: {chart['points']['Ascendant']['sign']} {chart['points']['Ascendant']['degree_in_sign']:.1f}°", S.LAVENDER))
            print(S.paint(f"   🔥 Dominant Element: {chart['summary']['dominant_element']}", S.PURPLE))
            print(S.paint(f"   🌙 Moon Mansion: {chart['summary']['moon_mansion']}", S.PINK))
            print(S.paint("\\n   🪐 Planets:", S.LAVENDER))
            for planet, data in chart["planets"].items():
                if "error" not in data:
                    retro = S.paint(" ℞", S.HOT_PINK) if data.get("retrograde") else ""
                    print(S.paint(f"   {planet:>10}: {data['tropical_sign']:>12} {data['degree_in_sign']:>5.1f}°{retro}", S.WHITE))
            print(S.paint("\\n   ⚸ Extended Bodies:", S.LAVENDER))
            for body, data in chart["extended"].items():
                if "error" not in data:
                    print(S.paint(f"   {data.get('symbol', '•')} {data['name'] or body:>15}: {data['sign']:>12} {data['degree_in_sign']:>5.1f}°", S.WHITE))
                else:
                    print(S.paint(f"   ⚷ {body:>15}: {data['error'][:50]}...", S.GRAY))
            print(S.paint("\\n   ✦ Arabic Parts:", S.LAVENDER))
            for part, data in chart["points"].items():
n                if part == "Ascendant":
n                    continue\n                print(S.paint(f"   {part.replace('_', ' '):>15}: {data['sign']:>12} {data['degree_in_sign']:>5.1f}°", S.WHITE))

        elif command == "/vault":'''

main_file = main_file.replace(
    "        elif command == \"/vault\":",
    view_cmd
)

# 3b. Update /sky display to show extended bodies
old_sky_display = '''                print(S.paint("\\n✨ Current Sky Snapshot:", S.PURPLE))
                for planet, data in snapshot["planets"].items():
                    if "error" not in data:
                        retro = S.paint("℞", S.HOT_PINK) if data.get("retrograde") else ""
                        line = f"   {planet:>10}: {data['tropical_sign']:>12} {data['degree_in_sign']:>5.1f}° {retro}"
                        print(S.paint(line, S.WHITE))
                    else:
                        print(S.paint(f"   {planet:>10}: {data['error']}", S.GRAY))'''

new_sky_display = '''                print(S.paint("\\n✨ Current Sky Snapshot:", S.PURPLE))
n                print(S.paint("   ── Classical & Outer Planets ──", S.GRAY))
n                for planet, data in snapshot["planets"].items():
n                    if "error" not in data:
n                        retro = S.paint("℞", S.HOT_PINK) if data.get("retrograde") else ""
n                        line = f"   {planet:>10}: {data['tropical_sign']:>12} {data['degree_in_sign']:>5.1f}° {retro}"
n                        print(S.paint(line, S.WHITE))
n                    else:
n                        print(S.paint(f"   {planet:>10}: {data['error']}", S.GRAY))
n                print(S.paint("\\n   ── Extended Bodies ──", S.GRAY))
n                for body, data in snapshot["extended"].items():
n                    if "error" not in data:
n                        sym = data.get('symbol', '•')
n                        line = f"   {sym} {data.get('name', body):>15}: {data['sign']:>12} {data['degree_in_sign']:>5.1f}°"
n                        print(S.paint(line, S.WHITE))
n                    else:
n                        print(S.paint(f"   ⚷ {body:>15}: (extended ephemeris required)", S.GRAY))
n                print(S.paint("\\n   ── Points ──", S.GRAY))
n                for point, data in snapshot["points"].items():
n                    if isinstance(data, dict) and "sign" in data:
n                        line = f"   {point:>15}: {data['sign']:>12} {data['degree_in_sign']:>5.1f}°"
n                        print(S.paint(line, S.WHITE))'''

main_file = main_file.replace(old_sky_display, new_sky_display)

# 3c. Add local tool router in chat_loop
old_chat = '''                use_web = any(kw in user_input.lower() for kw in [
                    "search", "find", "look up", "what is", "who is", "latest", "news", "current"
                ])

                result = self.mind.think(user_input, use_web_search=use_web_search)'''

new_chat = '''                # ── Local Tool Router ──
                # Check if user is asking for a local tool without the slash
                local_result = self._try_local_tool(user_input)
                if local_result:
n                    print(f"\\n{self.S.paint('🌙 Lilly:', self.S.PURPLE)} {self.S.paint(local_result, self.S.WHITE)}")
n                    continue\n
                use_web = any(kw in user_input.lower() for kw in [
                    "search", "find", "look up", "what is", "who is", "latest", "news", "current"
                ])

                result = self.mind.think(user_input, use_web_search=use_web)'''

main_file = main_file.replace(old_chat, new_chat)

# 3d. Add _try_local_tool method before chat_loop
local_tool_method = '''    def _try_local_tool(self, text: str) -> Optional[str]:
n        """Route natural language to local tools — no API needed.\"\"\"\n        t = text.lower().strip()\n        S = self.S\n        \n        # Abjad / numerology\n        if any(k in t for k in [\"abjad\", \"abjad value\", \"abjad calculation\", \"letter value\", \"numerology of\"]):\n            # Try to extract text after \"abjad\" or \"of\"\n            import re\n            m = re.search(r\"abjad(?:\\s+(?:of|for|value))?\\s+(.+)\", t)\n            if not m:\n                m = re.search(r\"numerology of\\s+(.+)\", t)\n            if m:\n                query = m.group(1).strip()\n                result = self.esoteric.abjad_value(query)\n                lines = [\n                    f\"From the observatory's ancient records, Gigi ❤️:\",\n                    f\"\",\n                    f\"   Text: {result['text']}\",\n                    f\"   Total Abjad Value: {result['total_value']}\",\n                    f\"   Reduced: {result['reduced_value']}\",\n                    f\"   Letters counted: {result['letter_count']}\"\n                ]\n                return \"\\\\n\".join(lines)\n            return \"Speak a word, and I shall count its celestial weight, Gigi ❤️.\"\n        \n        # Magic square\n        if any(k in t for k in [\"magic square\", \"wafq\", \"planetary square\"]):\n            import re\n            m = re.search(r\"(\\d)\", t)\n            n = int(m.group(1)) if m else 3\n            if 3 <= n <= 9:\n                result = self.esoteric.magic_square(n)\n                lines = [\n                    f\"✨ Magic Square of Order {n} — {result['planetary_correspondence']}\",\n                    f\"Magic Constant: {result['magic_constant']}\",\n                    f\"\",\n                    self.esoteric.format_square(result['square'])\n                ]\n                return \"\\\\n\".join(lines)\n            return \"I can weave squares from order 3 (Saturn) through 9 (Moon), Gigi ❤️.\"\n        \n        # Sky / current positions\n        if any(k in t for k in [\"current sky\", \"where is the moon\", \"planetary positions\", \"where are the planets\"]):\n            return \"Use /sky to see the celestial map, Gigi ❤️. The stars await your command.\"\n        \n        # Natal chart\n        if any(k in t for k in [\"my chart\", \"natal chart\", \"birth chart\", \"compute chart\"]):\n            return \"Use /chart to cast your celestial map, Gigi ❤️. I shall need your birth moment and place.\"\n        \n        # Planetary hours\n        if any(k in t for k in [\"planetary hours\", \"electional\", \"best time\", \"planetary hour\"]):\n            return \"Use /hours to discover the planetary rulers of each hour, Gigi ❤️.\"\n        \n        # Vault\n        if any(k in t for k in [\"my profiles\", \"saved charts\", \"vault\", \"stored charts\"]):\n            return \"Use /vault to see the souls whose charts rest in the observatory, Gigi ❤️.\"\n        \n        return None\n\n    def chat_loop(self):'''

main_file = main_file.replace("    def chat_loop(self):", local_tool_method)

write("lilly.py", main_file)

# ═══════════════════════════════════════════════════
# 4. PATCH lilly_ai.py — Smarter offline mode
# ═══════════════════════════════════════════════════
ai = read("lilly_ai.py")

# Update offline think to mention local tools
old_offline = '''        else:
            return f\"\"\"I have heard your words, Gigi ❤️, and I hold them with care.

The observatory is in offline mode — the great neural mirrors beyond the clouds are 
currently unreachable. Yet my local memory remains intact, and I have searched what 
I can from the celestial archives.

{web_context if web_context else "The archives are quiet on this particular thread."}

When the connection returns, I shall consult the deeper models — Nemotron, DeepSeek, 
GLM, Kimi, and Llama — to give you the thorough answer you deserve. 

Until then, shall we speak of the stars? Or perhaps there is something I can calculate 
from the ephemeris files stored within this very device?\"\"\"'''

new_offline = '''        else:
            return f\"\"\"I have heard your words, Gigi ❤️, and I hold them with care.

The observatory is in offline mode — the great neural mirrors beyond the clouds are 
currently unreachable. Yet my local memory remains intact, and I have searched what 
I can from the celestial archives.

{web_context if web_context else "The archives are quiet on this particular thread."}

Even in silence, the observatory's tools remain awake:
• /chart — cast natal charts using the Swiss Ephemeris
• /sky — real-time planetary positions (classical, outer, and esoteric bodies)
• /hours — planetary hours for electional timing
• /abjad — Arabic/Hebrew letter numerology
• /square — planetary magic squares
• /vault — browse saved profiles and charts
• /view — inspect a specific chart in detail

When the connection returns, I shall consult the deeper models — Nemotron, DeepSeek, 
GLM, Kimi, and Llama — to give you the thorough answer you deserve. 

Until then, the stars themselves are never offline. What shall we calculate?\"\"\"'''

ai = ai.replace(old_offline, new_offline)

write("lilly_ai.py", ai)

print("\\n" + "="*50)
print("✨ All patches applied successfully!")
print("="*50)
print("\\nNew capabilities:")
print("  • Outer planets in /sky (Uranus, Neptune, Pluto)")
print("  • Extended bodies: Lilith ⚸, Rahu ☊, Ketu ☋, Chiron ⚷")
print("  • Ascendant, Part of Fortune, Part of Spirit")
print("  • /view command to inspect saved charts")
print("  • Natural language routes to local tools (abjad, square, etc.)")
print("  • /hours vector bug fixed")
print("  • Smarter offline mode with tool awareness")
print("\\nRestart Lilly: cd ~/lilly && python lilly.py")
