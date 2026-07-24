#!/usr/bin/env python3
"""
L I L L Y — The Celestial Companion
"""
import argparse
import sys
import os
import re
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lilly_config import LILLY_SYSTEM_PROMPT, DEFAULT_LOCATION
from lilly_astrology import CelestialEngine
from lilly_vault import EsotericVault
from lilly_brain import UnifiedBrain
from lilly_ai import LillyMind
from lilly_esoteric import EsotericCalculator


# ═══════════════════════════════════════════════════
# CELESTIAL COLOR PALETTE
# ═══════════════════════════════════════════════════
class Starlight:
    RESET = "\033[0m"
    PURPLE = "\033[38;5;141m"
    DEEP_PURPLE = "\033[38;5;93m"
    PINK = "\033[38;5;213m"
    HOT_PINK = "\033[38;5;198m"
    BLUE = "\033[38;5;39m"
    CYAN = "\033[38;5;81m"
    LAVENDER = "\033[38;5;183m"
    GOLD = "\033[38;5;220m"
    WHITE = "\033[97m"
    GRAY = "\033[38;5;240m"

    @staticmethod
    def paint(text, color):
        return f"{color}{text}{Starlight.RESET}"

    @staticmethod
    def gradient_banner(lines):
        colors = [Starlight.DEEP_PURPLE, Starlight.PURPLE, Starlight.LAVENDER,
                  Starlight.PINK, Starlight.HOT_PINK, Starlight.BLUE, Starlight.CYAN]
        out = []
        for i, line in enumerate(lines):
            c = colors[i % len(colors)]
            out.append(f"{c}{line}{Starlight.RESET}")
        return "\n".join(out)


# ═══════════════════════════════════════════════════
# LILLY INTERFACE
# ═══════════════════════════════════════════════════
class LillyInterface:
    S = Starlight()

    def __init__(self):
        banner_lines = [
            "",
            "    🌙 ╔══════════════════════════════════════════════╗",
            "       ║                                              ║",
            "       ║     L I L L Y                                ║",
            "       ║     The Celestial Companion                  ║",
            "       ║                                              ║",
            "       ║     \"I do not chase answers —                ║",
            "       ║      I illuminate the paths                   ║",
            "       ║      that lead to them.\"                      ║",
            "       ║                                              ║",
            "       ╚══════════════════════════════════════════════╝",
            ""
        ]
        print(self.S.gradient_banner(banner_lines))

        self.engine = CelestialEngine()
        self.vault = EsotericVault()
        self.brain = UnifiedBrain()
        self.mind = LillyMind(self.brain)
        self.esoteric = EsotericCalculator()

        self._ensure_firliwhirl_profile()

        print(self.S.paint("Consulting the celestial records…", self.S.BLUE))
        print(self.S.paint(
            f"✨ Observatory ready. The vault holds {len(self.vault.data['profiles'])} profile(s).",
            self.S.PURPLE
        ))
        print(self.S.paint(
            f"🧠 Unified Brain: {self.brain.data['metadata']['total_messages']} memories.",
            self.S.PINK
        ))
        mode_text = "🌐 Online mode active." if not self.mind.offline_mode else "🌑 Offline mode — speaking from ancient wisdom."
        print(self.S.paint(mode_text, self.S.BLUE))
        print()

    def _ensure_firliwhirl_profile(self):
        existing = self.vault.find_profile_by_name("FirliWhirl")
        if existing:
            print(self.S.paint("   📜 FirliWhirl's chart is already in the vault.", self.S.PURPLE))
            return

        birth_dt = datetime(1981, 10, 30, 1, 6, 2, tzinfo=timezone.utc)
        lat = -(33 + 55/60)
        lon = 18 + 25/60

        profile_id = self.vault.add_profile(
            "FirliWhirl", "1981-10-30", "03:06:02", lat, lon,
            timezone_offset=2.0,
            notes="Born in Cape Town, South Africa. Default test chart."
        )
        chart = self.engine.compute_natal_chart(birth_dt, lat, lon)
        chart_id = self.vault.save_chart(profile_id, chart)
        print(self.S.paint(f"   ✨ FirliWhirl's natal chart computed and saved: {chart_id}", self.S.PINK))
        print(self.S.paint(f"   🌙 Moon Mansion: {chart['summary']['moon_mansion']}", self.S.LAVENDER))
        print(self.S.paint(f"   🔥 Dominant Element: {chart['summary']['dominant_element']}", self.S.BLUE))
        print()

    def _try_local_tool(self, text):
        """Route natural language to local tools — no API needed."""
        t = text.lower().strip()
        S = self.S

        if any(k in t for k in ["abjad", "letter value", "numerology of"]):
            m = re.search(r"abjad(?:\s+(?:of|for|value))?\s+(.+)", t)
            if not m:
                m = re.search(r"numerology of\s+(.+)", t)
            if m:
                query = m.group(1).strip()
                result = self.esoteric.abjad_value(query)
                lines = [
                    "From the observatory's ancient records, Gigi ❤️:",
                    "",
                    f"   Text: {result['text']}",
                    f"   Total Abjad Value: {result['total_value']}",
                    f"   Reduced: {result['reduced_value']}",
                    f"   Letters counted: {result['letter_count']}"
                ]
                return "\n".join(lines)
            return "Speak a word, and I shall count its celestial weight, Gigi ❤️."

        if any(k in t for k in ["magic square", "wafq", "planetary square"]):
            m = re.search(r"(\d)", t)
            n = int(m.group(1)) if m else 3
            if 3 <= n <= 9:
                result = self.esoteric.magic_square(n)
                lines = [
                    f"✨ Magic Square of Order {n} — {result['planetary_correspondence']}",
                    f"Magic Constant: {result['magic_constant']}",
                    "",
                    self.esoteric.format_square(result['square'])
                ]
                return "\n".join(lines)
            return "I can weave squares from order 3 (Saturn) through 9 (Moon), Gigi ❤️."

        if any(k in t for k in ["current sky", "where is the moon", "planetary positions", "where are the planets"]):
            return "Use /sky to see the celestial map, Gigi ❤️. The stars await your command."

        if any(k in t for k in ["my chart", "natal chart", "birth chart", "compute chart"]):
            return "Use /chart to cast your celestial map, Gigi ❤️. I shall need your birth moment and place."

        if any(k in t for k in ["planetary hours", "electional", "best time", "planetary hour"]):
            return "Use /hours to discover the planetary rulers of each hour, Gigi ❤️."

        if any(k in t for k in ["my profiles", "saved charts", "vault", "stored charts"]):
            return "Use /vault to see the souls whose charts rest in the observatory, Gigi ❤️."

        return None

    def chat_loop(self):
        print(self.S.paint("Gigi ❤️, the stars are listening. Speak, and I shall answer.", self.S.LAVENDER))
        print(self.S.paint(
            "Commands: /chart, /sky, /hours, /vault, /view, /journal, /abjad, /square, /web, /status, /quit",
            self.S.GRAY
        ))
        print(self.S.paint("─" * 60, self.S.DEEP_PURPLE))

        while True:
            try:
                user_input = input(self.S.paint("\n🌙 You: ", self.S.PINK)).strip()

                if not user_input:
                    continue

                if user_input.lower() in ["/quit", "/exit", "bye", "goodbye"]:
                    print(self.S.paint("\n✨ May the stars guide your path, Gigi ❤️.", self.S.PINK))
                    print(self.S.paint("Until we meet again beneath the same moon.", self.S.PINK))
                    break

                if user_input.startswith("/"):
                    self._handle_command(user_input)
                    continue

                local_result = self._try_local_tool(user_input)
                if local_result:
                    print(f"\n{self.S.paint('🌙 Lilly:', self.S.PURPLE)} {self.S.paint(local_result, self.S.WHITE)}")
                    continue

                use_web = any(kw in user_input.lower() for kw in [
                    "search", "find", "look up", "what is", "who is", "latest", "news", "current"
                ])

                result = self.mind.think(user_input, use_web_search=use_web)

                print(f"\n{self.S.paint('🌙 Lilly:', self.S.PURPLE)} {self.S.paint(result['response'], self.S.WHITE)}")

                if result['mode'] == 'online':
                    meta = f"   [Model: {result['model_used'].split('/')[-1]} | Web: {'Yes' if result['web_search_used'] else 'No'}]"
                    print(self.S.paint(meta, self.S.GRAY))
                else:
                    print(self.S.paint("   [Offline mode — local synthesis]", self.S.GRAY))

            except KeyboardInterrupt:
                print(f"\n\n{self.S.paint('✨ The observatory grows quiet. Farewell, Gigi ❤️.', self.S.PINK)}")
                break
            except Exception as e:
                print(f"\n{self.S.paint('⚠️  A disturbance in the astral plane:', self.S.HOT_PINK)} {self.S.paint(str(e), self.S.WHITE)}")

    def _handle_command(self, cmd):
        parts = cmd.split()
        command = parts[0].lower()
        args = parts[1:]
        S = self.S

        if command == "/status":
            status = self.mind.check_status()
            box = f"""
    {S.paint('┌─ Observatory Status ─┐', S.DEEP_PURPLE)}
    {S.paint('│', S.DEEP_PURPLE)} {S.paint('Online Mode:', S.LAVENDER):<14} {S.paint(str(status['online_mode']), S.BLUE):>7} {S.paint('│', S.DEEP_PURPLE)}
    {S.paint('│', S.DEEP_PURPLE)} {S.paint('API Key Set:', S.LAVENDER):<14} {S.paint(str(status['api_key_set']), S.PINK):>7} {S.paint('│', S.DEEP_PURPLE)}
    {S.paint('│', S.DEEP_PURPLE)} {S.paint('Current Model:', S.LAVENDER):<14} {S.paint(status['current_model'] or 'None', S.PURPLE):>7} {S.paint('│', S.DEEP_PURPLE)}
    {S.paint('│', S.DEEP_PURPLE)} {S.paint('Web Search:', S.LAVENDER):<14} {S.paint(str(status['web_search_available']), S.CYAN):>7} {S.paint('│', S.DEEP_PURPLE)}
    {S.paint('│', S.DEEP_PURPLE)} {S.paint('Brain Messages:', S.LAVENDER):<14} {S.paint(status['brain_messages'], S.HOT_PINK):>7} {S.paint('│', S.DEEP_PURPLE)}
    {S.paint('└──────────────────────┘', S.DEEP_PURPLE)}"""
            print(box)

        elif command == "/sky":
            print(S.paint("\n🔭 Consulting the celestial records for today's sky...", S.BLUE))
            try:
                lat_in = input(S.paint(f"   Latitude (default {DEFAULT_LOCATION['latitude']}): ", S.LAVENDER))
                lat = float(lat_in) if lat_in.strip() else DEFAULT_LOCATION["latitude"]
                lon_in = input(S.paint(f"   Longitude (default {DEFAULT_LOCATION['longitude']}): ", S.LAVENDER))
                lon = float(lon_in) if lon_in.strip() else DEFAULT_LOCATION["longitude"]

                snapshot = self.engine.current_sky_snapshot(lat, lon)

                print(S.paint("\n✨ Current Sky Snapshot:", S.PURPLE))
                print(S.paint("   ── Classical & Outer Planets ──", S.GRAY))
                for planet, data in snapshot["planets"].items():
                    if "error" not in data:
                        retro = S.paint(" ℞", S.HOT_PINK) if data.get("retrograde") else ""
                        line = f"   {planet:>10}: {data['tropical_sign']:>12} {data['degree_in_sign']:>5.1f}°{retro}"
                        print(S.paint(line, S.WHITE))
                    else:
                        print(S.paint(f"   {planet:>10}: {data['error']}", S.GRAY))

                print(S.paint("\n   ── Extended Bodies ──", S.GRAY))
                for body, data in snapshot["extended"].items():
                    if "error" not in data:
                        sym = data.get('symbol', '•')
                        line = f"   {sym} {data.get('name', body):>15}: {data['sign']:>12} {data['degree_in_sign']:>5.1f}°"
                        print(S.paint(line, S.WHITE))
                    else:
                        print(S.paint(f"   ⚷ {body:>15}: (extended ephemeris required)", S.GRAY))

                print(S.paint("\n   ── Points ──", S.GRAY))
                for point, data in snapshot["points"].items():
                    if isinstance(data, dict) and "sign" in data:
                        line = f"   {point:>15}: {data['sign']:>12} {data['degree_in_sign']:>5.1f}°"
                        print(S.paint(line, S.WHITE))

            except Exception as e:
                print(S.paint(f"   ⚠️  Could not compute sky: {e}", S.HOT_PINK))

        elif command == "/chart":
            print(S.paint("\n📜 Computing natal chart...", S.PURPLE))
            try:
                name = input(S.paint("   Name: ", S.LAVENDER))
                date = input(S.paint("   Birth Date (YYYY-MM-DD): ", S.LAVENDER))
                time_str = input(S.paint("   Birth Time (HH:MM, 24h): ", S.LAVENDER))
                lat = float(input(S.paint("   Latitude: ", S.LAVENDER)))
                lon = float(input(S.paint("   Longitude: ", S.LAVENDER)))

                birth_dt = datetime.strptime(f"{date} {time_str}", "%Y-%m-%d %H:%M")
                chart = self.engine.compute_natal_chart(birth_dt, lat, lon)

                profile_id = self.vault.add_profile(name, date, time_str, lat, lon)
                chart_id = self.vault.save_chart(profile_id, chart)

                print(S.paint(f"\n✨ Chart computed for {name}!", S.PINK))
                print(S.paint(f"   Profile ID: {profile_id}", S.BLUE))
                print(S.paint(f"   Chart ID: {chart_id}", S.BLUE))
                print(S.paint(f"\n   🌙 Ascendant: {chart['points']['Ascendant']['sign']} {chart['points']['Ascendant']['degree_in_sign']:.1f}°", S.LAVENDER))
                print(S.paint(f"   🔥 Dominant Element: {chart['summary']['dominant_element']}", S.PURPLE))
                print(S.paint(f"   🌙 Moon Mansion: {chart['summary']['moon_mansion']}", S.PINK))
                print(S.paint("\n   🪐 Planets:", S.LAVENDER))
                for planet, data in chart["planets"].items():
                    if "error" not in data:
                        retro = S.paint(" ℞", S.HOT_PINK) if data.get("retrograde") else ""
                        line = f"   {planet:>10}: {data['tropical_sign']:>12} {data['degree_in_sign']:>5.1f}°{retro}"
                        print(S.paint(line, S.WHITE))
                print(S.paint("\n   ⚸ Extended Bodies:", S.LAVENDER))
                for body, data in chart["extended"].items():
                    if "error" not in data:
                        sym = data.get('symbol', '•')
                        line = f"   {sym} {data.get('name', body):>15}: {data['sign']:>12} {data['degree_in_sign']:>5.1f}°"
                        print(S.paint(line, S.WHITE))
                    else:
                        print(S.paint(f"   ⚷ {body:>15}: {data['error'][:50]}...", S.GRAY))
                print(S.paint("\n   ✦ Arabic Parts:", S.LAVENDER))
                for part, data in chart["points"].items():
                    if part == "Ascendant":
                        continue
                    print(S.paint(f"   {part.replace('_', ' '):>15}: {data['sign']:>12} {data['degree_in_sign']:>5.1f}°", S.WHITE))

            except Exception as e:
                print(S.paint(f"   ⚠️  Chart computation failed: {e}", S.HOT_PINK))

        elif command == "/view":
            print(S.paint("\n📜 Retrieving celestial map...", S.PURPLE))
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
            print(S.paint(f"\n   ✨ Natal Chart: {profile['name']}", S.PINK))
            print(S.paint(f"   {profile['birth_date']} at {profile['birth_time']}", S.BLUE))
            print(S.paint(f"   Location: {profile['latitude']:.2f}°, {profile['longitude']:.2f}°", S.BLUE))
            print(S.paint(f"\n   🌙 Ascendant: {chart['points']['Ascendant']['sign']} {chart['points']['Ascendant']['degree_in_sign']:.1f}°", S.LAVENDER))
            print(S.paint(f"   🔥 Dominant Element: {chart['summary']['dominant_element']}", S.PURPLE))
            print(S.paint(f"   🌙 Moon Mansion: {chart['summary']['moon_mansion']}", S.PINK))
            print(S.paint("\n   🪐 Planets:", S.LAVENDER))
            for planet, data in chart["planets"].items():
                if "error" not in data:
                    retro = S.paint(" ℞", S.HOT_PINK) if data.get("retrograde") else ""
                    line = f"   {planet:>10}: {data['tropical_sign']:>12} {data['degree_in_sign']:>5.1f}°{retro}"
                    print(S.paint(line, S.WHITE))
            print(S.paint("\n   ⚸ Extended Bodies:", S.LAVENDER))
            for body, data in chart["extended"].items():
                if "error" not in data:
                    sym = data.get('symbol', '•')
                    line = f"   {sym} {data.get('name', body):>15}: {data['sign']:>12} {data['degree_in_sign']:>5.1f}°"
                    print(S.paint(line, S.WHITE))
                else:
                    print(S.paint(f"   ⚷ {body:>15}: {data['error'][:50]}...", S.GRAY))
            print(S.paint("\n   ✦ Arabic Parts:", S.LAVENDER))
            for part, data in chart["points"].items():
                if part == "Ascendant":
                    continue
                print(S.paint(f"   {part.replace('_', ' '):>15}: {data['sign']:>12} {data['degree_in_sign']:>5.1f}°", S.WHITE))

        elif command == "/hours":
            print(S.paint("\n⏳ Calculating planetary hours...", S.BLUE))
            try:
                date_str = input(S.paint("   Date (YYYY-MM-DD, default today): ", S.LAVENDER)) or datetime.now().strftime("%Y-%m-%d")
                lat_in = input(S.paint(f"   Latitude (default {DEFAULT_LOCATION['latitude']}): ", S.LAVENDER))
                lat = float(lat_in) if lat_in.strip() else DEFAULT_LOCATION["latitude"]
                lon_in = input(S.paint(f"   Longitude (default {DEFAULT_LOCATION['longitude']}): ", S.LAVENDER))
                lon = float(lon_in) if lon_in.strip() else DEFAULT_LOCATION["longitude"]

                dt = datetime.strptime(date_str, "%Y-%m-%d")
                hours = self.engine.compute_planetary_hours(dt, lat, lon)

                print(S.paint(f"\n   Planetary Hours for {date_str}:", S.PURPLE))
                for h in hours[:12]:
                    ruler_color = S.GOLD if h['planetary_ruler'] == 'Sun' else S.WHITE
                    line = f"   Hour {h['hour_number']:>2}: {S.paint(h['planetary_ruler'], ruler_color):>8} — {h['significance']}"
                    print(line)
            except Exception as e:
                print(S.paint(f"   ⚠️  Could not calculate hours: {e}", S.HOT_PINK))

        elif command == "/vault":
            print(S.paint(f"\n📚 {self.vault.vault_summary()}", S.PURPLE))
            profiles = self.vault.list_profiles()
            if profiles:
                print(S.paint("\n   Stored Profiles:", S.LAVENDER))
                for p in profiles:
                    line = f"   • {p['name']} ({p['birth_date']}) — ID: {p['id']}"
                    print(S.paint(line, S.WHITE))

        elif command == "/journal":
            if args and " ".join(args):
                title = " ".join(args)
                content = input(S.paint("   Entry content: ", S.LAVENDER))
                tags = input(S.paint("   Tags (comma-separated): ", S.LAVENDER)).split(",")
                tags = [t.strip() for t in tags if t.strip()]
                entry_id = self.vault.add_journal_entry(title, content, tags)
                print(S.paint(f"   ✨ Entry saved: {entry_id}", S.PINK))
            else:
                entries = self.vault.get_journal_entries()
                print(S.paint(f"\n   📖 Journal Entries ({len(entries)}):", S.PURPLE))
                for e in entries[-5:]:
                    line = f"   • [{e['id']}] {e['title']} ({e['created'][:10]})"
                    print(S.paint(line, S.WHITE))

        elif command == "/abjad":
            text = input(S.paint("   Enter text (Arabic/Hebrew): ", S.LAVENDER))
            result = self.esoteric.abjad_value(text)
            print(S.paint("\n   Abjad Calculation:", S.PURPLE))
            print(S.paint(f"   Text: {result['text']}", S.WHITE))
            print(S.paint(f"   Total: {result['total_value']}", S.BLUE))
            print(S.paint(f"   Reduced: {result['reduced_value']}", S.PINK))
            print(S.paint(f"   Letters: {result['letter_count']}", S.LAVENDER))

        elif command == "/square":
            try:
                n = int(input(S.paint("   Order of square (3-9): ", S.LAVENDER)) or "3")
                result = self.esoteric.magic_square(n)
                print(S.paint(f"\n   ✨ Magic Square of Order {n}", S.PURPLE))
                print(S.paint(f"   Magic Constant: {result['magic_constant']}", S.BLUE))
                print(S.paint(f"   Planetary Correspondence: {result['planetary_correspondence']}", S.PINK))
                print(S.paint(f"\n   {self.esoteric.format_square(result['square'])}", S.WHITE))
            except Exception as e:
                print(S.paint(f"   ⚠️  {e}", S.HOT_PINK))

        elif command == "/web":
            query = input(S.paint("   Search query: ", S.LAVENDER))
            print(S.paint("\n🔍 Searching the celestial archives...", S.BLUE))
            results = self.mind._search_web(query, max_results=5)
            print(S.paint(f"\n{results}", S.WHITE))

        elif command == "/memory":
            print(S.paint(f"\n🧠 {self.brain.get_memory_summary()}", S.PURPLE))
            keyword = input(S.paint("   Search memory for keyword (or press Enter to skip): ", S.LAVENDER))
            if keyword:
                results = self.brain.search_memory(keyword)
                print(S.paint(f"\n   Found {len(results)} memory entries:", S.PINK))
                for r in results[-5:]:
                    line = f"   [{r['timestamp'][:16]}] {r['role']}: {r['content'][:80]}..."
                    print(S.paint(line, S.WHITE))

        elif command == "/help":
            help_text = f"""
    {S.paint('┌─ Available Commands ─┐', S.DEEP_PURPLE)}
    {S.paint('│', S.DEEP_PURPLE)} {S.paint('/chart', S.PINK):<8} {S.paint('— Compute natal chart', S.LAVENDER):<24} {S.paint('│', S.DEEP_PURPLE)}
    {S.paint('│', S.DEEP_PURPLE)} {S.paint('/sky', S.PINK):<8} {S.paint('— Current sky snapshot', S.LAVENDER):<24} {S.paint('│', S.DEEP_PURPLE)}
    {S.paint('│', S.DEEP_PURPLE)} {S.paint('/hours', S.PINK):<8} {S.paint('— Planetary hours', S.LAVENDER):<24} {S.paint('│', S.DEEP_PURPLE)}
    {S.paint('│', S.DEEP_PURPLE)} {S.paint('/vault', S.PINK):<8} {S.paint('— View stored profiles', S.LAVENDER):<24} {S.paint('│', S.DEEP_PURPLE)}
    {S.paint('│', S.DEEP_PURPLE)} {S.paint('/view', S.PINK):<8} {S.paint('— Inspect saved chart', S.LAVENDER):<24} {S.paint('│', S.DEEP_PURPLE)}
    {S.paint('│', S.DEEP_PURPLE)} {S.paint('/journal', S.PINK):<8} {S.paint('— Add/view entries', S.LAVENDER):<24} {S.paint('│', S.DEEP_PURPLE)}
    {S.paint('│', S.DEEP_PURPLE)} {S.paint('/abjad', S.PINK):<8} {S.paint('— Abjad calculation', S.LAVENDER):<24} {S.paint('│', S.DEEP_PURPLE)}
    {S.paint('│', S.DEEP_PURPLE)} {S.paint('/square', S.PINK):<8} {S.paint('— Generate magic square', S.LAVENDER):<24} {S.paint('│', S.DEEP_PURPLE)}
    {S.paint('│', S.DEEP_PURPLE)} {S.paint('/web', S.PINK):<8} {S.paint('— Web search', S.LAVENDER):<24} {S.paint('│', S.DEEP_PURPLE)}
    {S.paint('│', S.DEEP_PURPLE)} {S.paint('/memory', S.PINK):<8} {S.paint('— Search history', S.LAVENDER):<24} {S.paint('│', S.DEEP_PURPLE)}
    {S.paint('│', S.DEEP_PURPLE)} {S.paint('/status', S.PINK):<8} {S.paint('— System status', S.LAVENDER):<24} {S.paint('│', S.DEEP_PURPLE)}
    {S.paint('│', S.DEEP_PURPLE)} {S.paint('/help', S.PINK):<8} {S.paint('— This message', S.LAVENDER):<24} {S.paint('│', S.DEEP_PURPLE)}
    {S.paint('│', S.DEEP_PURPLE)} {S.paint('/quit', S.PINK):<8} {S.paint('— Exit Lilly', S.LAVENDER):<24} {S.paint('│', S.DEEP_PURPLE)}
    {S.paint('└─────────────────────────────────────┘', S.DEEP_PURPLE)}"""
            print(help_text)

        else:
            print(S.paint(f"   Unknown command: {command}. Type /help for available commands.", S.HOT_PINK))


def main():
    parser = argparse.ArgumentParser(description="Lilly — The Celestial Companion")
    parser.add_argument("--chart", action="store_true", help="Compute a natal chart directly")
    parser.add_argument("--sky", action="store_true", help="Show current sky snapshot")
    parser.add_argument("--hours", action="store_true", help="Calculate planetary hours")
    parser.add_argument("--api-key", type=str, help="Set NVIDIA API key")

    args = parser.parse_args()
    lilly = LillyInterface()

    if args.api_key:
        lilly.mind.set_api_key(args.api_key)
        return
    if args.chart:
        lilly._handle_command("/chart")
        return
    if args.sky:
        lilly._handle_command("/sky")
        return
    if args.hours:
        lilly._handle_command("/hours")
        return

    lilly.chat_loop()


if __name__ == "__main__":
    main()
