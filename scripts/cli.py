#!/usr/bin/env python3
"""
AstroMage CLI
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core_engine import Engine


def format_planet(name: str, info: Dict) -> str:
    sign = info.get('sign', '?')
    degree = info.get('degree', '?')
    house = info.get('house', '')
    suffix = f"  [{house}]" if house != '' else ""
    return f"{name}: {sign} {degree}{suffix}"


def cmd_live(_: list[str]) -> int:
    engine = Engine()
    data = engine.live()
    print(f"AstroMage Live — {data.get('timestamp', 'now')}")
    print(f"Ephemeris: {data.get('ephemeris', '?')}")
    print(f"Location : {data.get('location', '?')}")
    print()
    for name, info in data.get("planets", {}).items():
        print(format_planet(name, info))
    print()
    mansion = data.get("lunar_mansion", {})
    print(f"Lunar Mansion: {mansion.get('name')}")
    hour = data.get("planetary_hour", {})
    print(f"Planetary Hour: {hour.get('planet')}  {hour.get('time')}")
    return 0


def cmd_aspects(_: list[str]) -> int:
    engine = Engine()
    data = engine.aspects()
    print("Aspects:")
    for a in data.get("aspects", []):
        print(f"  {a['planet1']} {a['symbol']} {a['planet2']}  orb {a['orb']}  — {a['meaning']}")
    return 0


def cmd_transit(args: list[str]) -> int:
    days = int(args[0]) if args else 30
    engine = Engine()
    # transit_calendar() ignores natal unless supplied; build a tiny dummy
    # natal from current positions so transit-to-natal aspects are produced.
    natal = {
        "Sun": engine.planet("Sun"),
        "Moon": engine.planet("Moon"),
        "Mercury": engine.planet("Mercury"),
        "Venus": engine.planet("Venus"),
        "Mars": engine.planet("Mars"),
        "Jupiter": engine.planet("Jupiter"),
        "Saturn": engine.planet("Saturn"),
    }
    # transit_calendar returns a list of transit-event dicts.
    data = engine.transit_calendar(days=days, natal_planets=natal)
    out_path = Path("outputs") / f"transits_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Transits written to {out_path}")
    print(f"Total events: {len(data)}")
    return 0


def cmd_hour(_: list[str]) -> int:
    engine = Engine()
    # The Engine exposes the current planetary hour through live().
    data = engine.live().get("planetary_hour", {})
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return 0


def cmd_mansion(_: list[str]) -> int:
    engine = Engine()
    # The Engine tracks the lunar station as a nakshatra (27-station Vedic
    # system). Use it for the mansion command.
    data = engine.nakshatra()
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return 0


def usage() -> int:
    print(
        "AstroMage — Lilly-backed astrology\n"
        "\n"
        "Usage:\n"
        "  python cli.py live\n"
        "  python cli.py aspects\n"
        "  python cli.py transit [days]\n"
        "  python cli.py hour\n"
        "  python cli.py mansion\n"
    )
    return 1


def main(argv=None) -> int:
    argv = argv or sys.argv[1:]
    if not argv:
        return usage()

    cmds = {
        "live": cmd_live,
        "aspects": cmd_aspects,
        "transit": cmd_transit,
        "hour": cmd_hour,
        "mansion": cmd_mansion,
    }

    name = argv[0].lower()
    if name not in cmds:
        return usage()
    return cmds[name](argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
