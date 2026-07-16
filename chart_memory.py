"""Natal Chart Memory System for AstroMageLilly"""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

CHARTS_FILE = Path(__file__).parent / "charts" / "natal_charts.json"

def load_charts() -> dict:
    if CHARTS_FILE.exists():
        try:
            with open(CHARTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_charts(charts: dict):
    CHARTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CHARTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(charts, f, indent=2, ensure_ascii=False)

def add_chart(name: str, chart_data: dict) -> bool:
    charts = load_charts()
    chart_data['saved_at'] = datetime.now().isoformat()
    charts[name] = chart_data
    save_charts(charts)
    return True

def get_chart(name: str) -> dict | None:
    charts = load_charts()
    return charts.get(name)

def delete_chart(name: str) -> bool:
    charts = load_charts()
    if name in charts:
        del charts[name]
        save_charts(charts)
        return True
    return False

def list_charts() -> list:
    charts = load_charts()
    return list(charts.keys())

def format_chart_for_ai(chart: dict) -> str:
    """Format a chart as text for Lilly's AI context."""
    if not chart:
        return ""
    
    lines = [
        f"NATAL CHART: {chart.get('name', 'Unknown')}",
        f"Date: {chart.get('birth_date', '?')} | Time: {chart.get('birth_time', '?')}",
        f"Location: Lat {chart.get('latitude', '?')}°, Lon {chart.get('longitude', '?')}°",
        f"House System: {chart.get('house_system', '?')}",
        f"ASC: {chart.get('ascendant', {}).get('sign', '?')} {chart.get('ascendant', {}).get('degree', 0):.2f}°",
        f"MC: {chart.get('midheaven', {}).get('sign', '?')} {chart.get('midheaven', {}).get('degree', 0):.2f}°",
        "",
        "PLANETARY POSITIONS:",
    ]
    
    for name, info in chart.get('planets', {}).items():
        sign = info.get('sign', '?')
        degree = info.get('degree', 0)
        house = info.get('house', '?')
        retro = " ℞" if info.get('retrograde') else ""
        lines.append(f"  {name}: {sign} {degree:.2f}° H{house}{retro}")
    
    return "\n".join(lines)

