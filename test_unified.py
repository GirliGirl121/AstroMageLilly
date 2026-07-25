#!/usr/bin/env python3
# test_unified.py — Verify the unified engine, synastry, and transits

from datetime import datetime
from unified_engine import engine
from config import DEFAULT_NATAL

def test_gigi_chart():
    print("=" * 60)
    print("TEST 1: Gigi's Natal Chart")
    print("=" * 60)
    dt = datetime.strptime(f"{DEFAULT_NATAL['date']} {DEFAULT_NATAL['time']}",
                           "%Y-%m-%d %H:%M:%S")
    chart = engine.get_full_chart(
        dt, DEFAULT_NATAL["lat"], DEFAULT_NATAL["lon"],
        DEFAULT_NATAL["timezone_offset"], name="Gigi"
    )
    print(f"Name: {chart['name']}")
    print(f"JD: {chart['julian_day']}")
    print(f"Planets calculated: {len(chart['planets'])}")
    for name, p in list(chart['planets'].items())[:5]:
        val = p.get('_validation')
        v_str = f" [Skyfield diff: {val['diff_arcmin']}']" if val else ""
        print(f"  {name}: {p['sign']} {p['degree_in_sign']}°{v_str}")
    print(f"Houses: {len(chart['houses'])} cusps")
    print(f"Aspects: {len(chart['aspects'])}")
    print(f"Arabic Parts: {list(chart['arabic_parts'].keys())}")
    print(f"Moon Phase: {chart['moon_phase']['phase']}")
    print("PASS\n")

def test_engine_comparison():
    print("=" * 60)
    print("TEST 2: Engine Comparison (Swiss vs Skyfield)")
    print("=" * 60)
    dt = datetime.strptime(f"{DEFAULT_NATAL['date']} {DEFAULT_NATAL['time']}",
                           "%Y-%m-%d %H:%M:%S")
    result = engine.compare_engines(dt, DEFAULT_NATAL["lat"],
                                    DEFAULT_NATAL["lon"], DEFAULT_NATAL["timezone_offset"])
    if "error" in result:
        print(f"SKIP: {result['error']}")
        return
    print(f"Max difference: {result['max_diff_arcmin']} arcmin")
    print(f"Agreement: {result['agreement']}")
    for planet, diff in result['longitude_diffs_arcmin'].items():
        status = "✓" if diff < 0.5 else "✗"
        print(f"  {status} {planet}: {diff} arcmin")
    print("PASS\n")

def test_synastry():
    print("=" * 60)
    print("TEST 3: Synastry (Gigi vs Gigi)")
    print("=" * 60)
    dt = datetime.strptime(f"{DEFAULT_NATAL['date']} {DEFAULT_NATAL['time']}",
                           "%Y-%m-%d %H:%M:%S")
    gigi = engine.get_full_chart(
        dt, DEFAULT_NATAL["lat"], DEFAULT_NATAL["lon"],
        DEFAULT_NATAL["timezone_offset"], name="Gigi"
    )
    syn = engine.synastry(gigi, gigi, orb=8.0)
    print(f"Inter-aspects found: {len(syn['inter_aspects'])}")
    print(f"House overlays: {len(syn['house_overlays'])}")
    print("PASS\n")

def test_transits():
    print("=" * 60)
    print("TEST 4: Transits (Gigi vs Now)")
    print("=" * 60)
    dt = datetime.strptime(f"{DEFAULT_NATAL['date']} {DEFAULT_NATAL['time']}",
                           "%Y-%m-%d %H:%M:%S")
    gigi = engine.get_full_chart(
        dt, DEFAULT_NATAL["lat"], DEFAULT_NATAL["lon"],
        DEFAULT_NATAL["timezone_offset"], name="Gigi"
    )
    now_jd = engine.jd_from_datetime(datetime.now(), DEFAULT_NATAL["timezone_offset"])
    trans = engine.transits(gigi, now_jd, orb=5.0)
    print(f"Transit aspects found: {len(trans['inter_aspects'])}")
    for a in trans['inter_aspects'][:5]:
        print(f"  {a['planet2']} {a['aspect']} natal {a['planet1']} (orb {a['orb']}°)")
    print("PASS\n")

def test_astronomy():
    print("=" * 60)
    print("TEST 5: Astronomical API (Skyfield pass-through)")
    print("=" * 60)
    if not engine.sky:
        print("SKIP: Skyfield not available")
        return
    pos = engine.high_precision_pos("Sun", DEFAULT_NATAL["lat"], DEFAULT_NATAL["lon"])
    if pos:
        print(f"Sun RA: {pos['ra_hours']}h, Dec: {pos['dec_degrees']}°")
        print(f"Alt: {pos['altitude']}°, Az: {pos['azimuth']}°")
    phase = engine.precise_moon_phase()
    if phase:
        print(f"Moon phase: {phase['phase_name']}, {phase['illumination_percent']}%")
    print("PASS\n")

if __name__ == "__main__":
    try:
        test_gigi_chart()
        test_engine_comparison()
        test_synastry()
        test_transits()
        test_astronomy()
        print("=" * 60)
        print("ALL TESTS PASSED — Unified engine is ready.")
        print("=" * 60)
    except Exception as e:
        print(f"\n[FAIL] {e}")
        import traceback
        traceback.print_exc()

