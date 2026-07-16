#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path
from flask import Flask, jsonify, request
import swisseph as swe

# Constants
ROOT = Path(__file__).resolve().parent
PROFILES_FILE = ROOT / 'data' / 'profiles.json'

app = Flask(__name__)

def load_profiles():
    if not PROFILES_FILE.exists():
        return []
    with open(PROFILES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_profiles(profiles):
    with open(PROFILES_FILE, 'w', encoding='utf-8') as f:
        json.dump(profiles, f, indent=2)

@app.route("/api/profiles", methods=["GET"])
def get_profiles():
    return jsonify(load_profiles())

@app.route("/api/profiles", methods=["POST"])
def add_profile():
    data = request.json
    profiles = load_profiles()
    data['id'] = max([p['id'] for p in profiles] + [0]) + 1
    profiles.append(data)
    save_profiles(profiles)
    return jsonify(data)

@app.route("/api/profiles/<int:id>", methods=["DELETE"])
def delete_profile(id):
    profiles = [p for p in load_profiles() if p['id'] != id]
    save_profiles(profiles)
    return jsonify({'ok': True})

@app.route("/api/natal/<int:id>", methods=["GET"])
def calculate_natal(id):
    profiles = load_profiles()
    profile = next((p for p in profiles if p['id'] == id), None)
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404
    
    # Calculate chart (simplified implementation for hookup)
    # Using Swiss Ephemeris here...
    return jsonify({
        'name': profile['name'],
        'planets': {'Sun': {'sign': 'Aries', 'deg': '10°'}, 'Moon': {'sign': 'Taurus', 'deg': '5°'}},
        'houses': 'Placeholder'
    })

if __name__ == "__main__":
    app.run(port=5488, debug=True)
