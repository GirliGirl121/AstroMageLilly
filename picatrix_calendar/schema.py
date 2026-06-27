#!/usr/bin/env python3
"""
Picatrix Astrological Calendar — Database Schema and Generator
Based on the Ghayat al-Hakim (Picatrix) tradition.

Author: Lilly for Gigi ❤️
Date: 2026-06-24
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta

DB_PATH = '/home/ladylefey/AstroMage/picatrix_calendar/picatrix_calendar.db'

SCHEMA_SQL = """
-- Picatrix Astrological Calendar Database
-- Generated from Ghayat al-Hakim (Picatrix) and related sources

CREATE TABLE IF NOT EXISTS calendar_dates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL UNIQUE,           -- YYYY-MM-DD
    julian_day REAL NOT NULL,            -- Julian Day Number
    day_of_week TEXT NOT NULL,           -- Sunday, Monday, etc.
    day_ruler TEXT NOT NULL,             -- Ruling planet of the day
    day_ruler_ar TEXT,                   -- Arabic name
    day_ruler_vedic TEXT,                -- Vedic name
    sunrise TEXT,                        -- HH:MM (local)
    sunset TEXT,                         -- HH:MM (local)
    day_length_sec REAL,                 -- Day length in seconds
    night_length_sec REAL,               -- Night length in seconds
    location TEXT DEFAULT 'Kariega, ZA',
    timezone TEXT DEFAULT 'Africa/Johannesburg',
    source TEXT DEFAULT 'Picatrix',
    confidence TEXT DEFAULT 'high',
    notes TEXT
);

CREATE TABLE IF NOT EXISTS planetary_hours (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    hour_number INTEGER NOT NULL,        -- 0-23 (0 = first hour from sunrise)
    period TEXT NOT NULL,                -- 'day' or 'night'
    planet TEXT NOT NULL,                -- Ruling planet
    planet_ar TEXT,                      -- Arabic name
    planet_vedic TEXT,                   -- Vedic name
    malikah_spirit TEXT,                 -- Picatrix ruling spirit
    malikah_arabic TEXT,                 -- Arabic spirit name
    malikah_angel TEXT,                  -- Picatrix angel
    hour_start TEXT NOT NULL,            -- HH:MM (local)
    hour_end TEXT NOT NULL,              -- HH:MM (local)
    duration_min REAL,                   -- Hour duration in minutes
    significance TEXT,                   -- One-line meaning
    recommended_ops TEXT,                -- JSON array of recommended operations
    source TEXT DEFAULT 'Picatrix BIII Ch9',
    confidence TEXT DEFAULT 'high',
    FOREIGN KEY (date) REFERENCES calendar_dates(date)
);

CREATE TABLE IF NOT EXISTS moon_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    moon_longitude REAL NOT NULL,        -- Tropical longitude in degrees
    moon_sign TEXT NOT NULL,             -- Zodiac sign
    moon_sign_degree REAL NOT NULL,      -- Degree within sign
    mansion_index INTEGER NOT NULL,      -- 0-26 (27 mansions)
    mansion_name TEXT NOT NULL,
    mansion_arabic TEXT,
    mansion_ruler_sign TEXT,
    mansion_element TEXT,
    mansion_degree_in REAL,             -- Degree within mansion
    mansion_meaning TEXT,
    recommended_works TEXT,              -- JSON array
    forbidden_works TEXT,                -- JSON array
    source TEXT DEFAULT 'Picatrix BII',
    confidence TEXT DEFAULT 'high',
    FOREIGN KEY (date) REFERENCES calendar_dates(date)
);

CREATE TABLE IF NOT EXISTS planetary_aspects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    planet1 TEXT NOT NULL,
    planet2 TEXT NOT NULL,
    aspect_type TEXT NOT NULL,           -- Conjunction, Sextile, Square, Trine, Opposition
    orb REAL NOT NULL,                   -- Orb in degrees
    applying TEXT,                       -- 'applying' or 'separating'
    significance TEXT,
    source TEXT DEFAULT 'Picatrix',
    confidence TEXT DEFAULT 'high',
    FOREIGN KEY (date) REFERENCES calendar_dates(date)
);

CREATE TABLE IF NOT EXISTS elections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    category TEXT NOT NULL,              -- love, business, travel, health, war, agriculture, ritual, etc.
    operation TEXT NOT NULL,             -- Specific operation
    rating TEXT NOT NULL,                -- 'excellent', 'good', 'neutral', 'bad', 'forbidden'
    planet TEXT,                         -- Associated planet
    sign TEXT,                           -- Associated sign
    mansion TEXT,                        -- Associated mansion
    day_ruler TEXT,
    hour_ruler TEXT,
    description TEXT,
    picatrix_reference TEXT,             -- Book, Chapter, section
    source TEXT DEFAULT 'Picatrix',
    confidence TEXT DEFAULT 'high',
    notes TEXT,
    FOREIGN KEY (date) REFERENCES calendar_dates(date)
);

CREATE TABLE IF NOT EXISTS lunar_mansions_reference (
    id INTEGER PRIMARY KEY,
    mansion_index INTEGER NOT NULL UNIQUE, -- 0-26 (27 mansions)
    name TEXT NOT NULL,
    arabic_name TEXT,
    picatrix_name TEXT,                  -- Name as given in Picatrix
    start_sign TEXT NOT NULL,
    start_degree REAL NOT NULL,          -- Degree in zodiac (0-360)
    end_degree REAL NOT NULL,
    ruler_sign TEXT,
    element TEXT,
    meaning TEXT,
    recommended_works TEXT,              -- JSON array
    forbidden_works TEXT,                -- JSON array
    picatrix_reference TEXT,
    picatrix_images TEXT,                -- Description of associated images
    source TEXT DEFAULT 'Picatrix BII',
    confidence TEXT DEFAULT 'high',
    notes TEXT
);

CREATE TABLE IF NOT EXISTS planetary_correspondences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    planet TEXT NOT NULL,
    category TEXT NOT NULL,              -- color, metal, stone, incense, plant, animal, body_part, profession, food, clothing_color
    item TEXT NOT NULL,
    picatrix_reference TEXT,
    source TEXT DEFAULT 'Picatrix BIII',
    confidence TEXT DEFAULT 'high',
    notes TEXT
);

CREATE TABLE IF NOT EXISTS fixed_stars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    arabic_name TEXT,
    constellation TEXT,
    longitude REAL,                      -- Approximate tropical longitude
    magnitude REAL,
    nature TEXT,                         -- Planetary nature (e.g., "Mars+Saturn")
    description TEXT,
    picatrix_reference TEXT,
    source TEXT DEFAULT 'Picatrix BII',
    confidence TEXT DEFAULT 'high'
);

CREATE TABLE IF NOT EXISTS seasonal_correspondences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    season TEXT NOT NULL,                -- spring, summer, autumn, winter
    sign TEXT NOT NULL,                  -- Associated zodiac sign
    planet TEXT,                         -- Ruling planet
    element TEXT,
    description TEXT,
    operations TEXT,                     -- JSON array
    picatrix_reference TEXT,
    source TEXT DEFAULT 'Picatrix BIII',
    confidence TEXT DEFAULT 'high'
);

CREATE TABLE IF NOT EXISTS talismanic_timings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    planet TEXT NOT NULL,
    operation TEXT NOT NULL,             -- Type of talisman/image
    required_day TEXT,
    required_hour TEXT,
    required_sign TEXT,
    required_mansion TEXT,
    required_aspect TEXT,
    description TEXT,
    picatrix_reference TEXT,
    source TEXT DEFAULT 'Picatrix BII-BIII',
    confidence TEXT DEFAULT 'high'
);

"""
INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_planetary_hours_date ON planetary_hours(date);
CREATE INDEX IF NOT EXISTS idx_moon_data_date ON moon_data(date);
CREATE INDEX IF NOT EXISTS idx_aspects_date ON planetary_aspects(date);
CREATE INDEX IF NOT EXISTS idx_elections_date ON elections(date);
CREATE INDEX IF NOT EXISTS idx_mansion_index ON lunar_mansions_reference(mansion_index);
CREATE INDEX IF NOT EXISTS idx_correspondences_planet ON planetary_correspondences(planet);
"""

def create_database():
    """Create the Picatrix Calendar database."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA_SQL)
    conn.executescript(INDEX_SQL)
    conn.commit()
    return conn

def load_reference_data(conn):
    """Load static reference data (mansions, correspondences, etc.)."""
    
    # Lunar Mansions (27 mansions, starting from 0° Aries)
    # Based on Picatrix Book II and Arabic tradition
    mansions = [
        {"index": 0, "name": "Al-Sharatain", "arabic_name": "الشَرَطَيْن", "picatrix_name": "Alnath", "start_sign": "Aries", "start_degree": 0.0, "end_degree": 12.857, "ruler_sign": "Aries", "element": "Fire", "meaning": "The Two Signals. Favorable for business, beginnings, planting seeds. Associated with whirlwinds and conflicts.", "recommended_works": json.dumps(["starting new projects", "business ventures", "planting", "travel"]), "forbidden_works": json.dumps(["marriage (some sources)", "passive activities"]), "picatrix_reference": "Picatrix BII, Ch. Mansions; Picatrix BIII Ch. Operations", "picatrix_images": "Image of a man with two horns, or two figures. Associated with the head."},
        {"index": 1, "name": "Al-Butain", "arabic_name": "البُطَيْن", "picatrix_name": "Albotain", "start_sign": "Aries", "start_degree": 12.857, "end_degree": 25.714, "ruler_sign": "Taurus", "element": "Earth", "meaning": "The Little Belly. Recklessness, risk-taking. Favorable for sciences, outdoor work. Unfavorable for marriage and sea travel.", "recommended_works": json.dumps(["scientific work", "outdoor labor", "study", "risk-taking ventures"]), "forbidden_works": json.dumps(["marriage (some sources)", "sea travel"]), "picatrix_reference": "Picatrix BII; Volguine via Picatrix", "picatrix_images": "Image of a figure with a small belly."},
        {"index": 2, "name": "Al-Thurayya", "arabic_name": "الثُّرَيَّا", "picatrix_name": "Azoraya", "start_sign": "Taurus", "start_degree": 25.714, "end_degree": 38.571, "ruler_sign": "Gemini", "element": "Air", "meaning": "The Abundance. Hard work, reward, nourishment. Favorable for earning, rewards, abundance.", "recommended_works": json.dumps(["seeking reward", "financial gain", "nurturing", "building"]), "forbidden_works": json.dumps(["idleness", "destruction"]), "picatrix_reference": "Picatrix BII", "picatrix_images": "Image of a woman with flowing hair, or a group of stars (Pleiades)."},
        {"index": 3, "name": "Al-Dabaran", "arabic_name": "الدَّبَرَان", "picatrix_name": "Al Debaran", "start_sign": "Taurus", "start_degree": 38.571, "end_degree": 51.429, "ruler_sign": "Cancer", "element": "Water", "meaning": "The Follower. Irresistible passion, determination. Good for love, passion, conflict resolution. Unfavorable for committed partnerships.", "recommended_works": json.dumps(["passionate pursuits", "conflict resolution", "determination", "love magic"]), "forbidden_works": json.dumps(["marriage (some sources)", "long-term commitments"]), "picatrix_reference": "Picatrix BII; Volguine", "picatrix_images": "Image of a figure following another, or a dog (Aldebaran)."},
        {"index": 4, "name": "Al-Haq'ah", "arabic_name": "الحَقْعَة", "picatrix_name": "Al Hakah", "start_sign": "Gemini", "start_degree": 51.429, "end_degree": 64.286, "ruler_sign": "Leo", "element": "Fire", "meaning": "The White Spot. Wisdom, education, arts, friendships, marriage. Shy of public life but enjoys private study.", "recommended_works": json.dumps(["education", "artistic pursuits", "friendship", "marriage", "private study"]), "forbidden_works": json.dumps(["public appearances (some sources)"]), "picatrix_reference": "Picatrix BII; Volguine", "picatrix_images": "Image of a white spot or mark."},
        {"index": 5, "name": "Al-Hana", "arabic_name": "الحَنَاء", "picatrix_name": "Al Hanach", "start_sign": "Cancer", "start_degree": 64.286, "end_degree": 77.143, "ruler_sign": "Virgo", "element": "Earth", "meaning": "The Mark. Social life, friendship. Unfavorable for health and hard labor. Possible financial loss.", "recommended_works": json.dumps(["social gatherings", "friendship", "light work"]), "forbidden_works": json.dumps(["hard labor", "strenuous activity", "financial speculation"]), "picatrix_reference": "Picatrix BII; Volguine", "picatrix_images": "Image of a figure with a mark or brand."},
        {"index": 6, "name": "Al-Dhira", "arabic_name": "الذِّرَاع", "picatrix_name": "Aldirah", "start_sign": "Cancer", "start_degree": 77.143, "end_degree": 90.0, "ruler_sign": "Libra", "element": "Air", "meaning": "The Arm. Love of home, family, friends. Amiable, understanding, content with little. Can indicate isolation.", "recommended_works": json.dumps(["domestic matters", "family", "friendship", "retirement", "contentment"]), "forbidden_works": json.dumps(["ambition", "public life"]), "picatrix_reference": "Picatrix BII; Volguine", "picatrix_images": "Image of an arm or foreleg."},
        {"index": 7, "name": "Al-Nathrah", "arabic_name": "النَّثْرَة", "picatrix_name": "Annathra", "start_sign": "Leo", "start_degree": 90.0, "end_degree": 102.857, "ruler_sign": "Scorpio", "element": "Water", "meaning": "The Crown. Profound attachment to family and children. Love and friendship through travel.", "recommended_works": json.dumps(["family matters", "childcare", "friendship", "short travels"]), "forbidden_works": json.dumps(["isolation"]), "picatrix_reference": "Picatrix BII; Volguine", "picatrix_images": "Image of a crown or garland."},
        {"index": 8, "name": "Al-Tarf", "arabic_name": "الطَّرْف", "picatrix_name": "Al Tarf", "start_sign": "Leo", "start_degree": 102.857, "end_degree": 115.714, "ruler_sign": "Sagittarius", "element": "Fire", "meaning": "The Eye. Benevolence, power. Can indicate strong personality or discouragement depending on chart.", "recommended_works": json.dumps(["leadership", "observation", "vigilance"]), "forbidden_works": json.dumps(["passivity"]), "picatrix_reference": "Picatrix BII; Volguine", "picatrix_images": "Image of an eye or watching figure."},
        {"index": 9, "name": "Al-Jabhah", "arabic_name": "الجَبْهَة", "picatrix_name": "Algebha", "start_sign": "Virgo", "start_degree": 115.714, "end_degree": 128.571, "ruler_sign": "Capricorn", "element": "Earth", "meaning": "The Forehead. Favorable for studies, earnings, professional success, love. Sensitive to others' feelings. Risk of pride and substance abuse.", "recommended_works": json.dumps(["studies", "professional work", "social life", "earning"]), "forbidden_works": json.dumps(["substance abuse", "pride", "arrogance"]), "picatrix_reference": "Picatrix BII; Volguine/Koparkar", "picatrix_images": "Image of a forehead or broad face."},
        {"index": 10, "name": "Al-Zubrah", "arabic_name": "الزُّبْرَة", "picatrix_name": "Azobra", "start_sign": "Libra", "start_degree": 128.571, "end_degree": 141.429, "ruler_sign": "Aquarius", "element": "Air", "meaning": "The Mane. Wealth through others, trade, marriage, travel. Women may suffer ill-health.", "recommended_works": json.dumps(["trade", "marriage", "travel", "wealth building"]), "forbidden_works": json.dumps(["solitary work"]), "picatrix_reference": "Picatrix BII; Volguine", "picatrix_images": "Image of a mane or flowing hair."},
        {"index": 11, "name": "Al-Sarfah", "arabic_name": "الصَّرْفَة", "picatrix_name": "Acarfa", "start_sign": "Libra", "start_degree": 141.429, "end_degree": 154.286, "ruler_sign": "Pisces", "element": "Water", "meaning": "The Changer. Success through service to others, agriculture, employee work. Requires dedication.", "recommended_works": json.dumps(["service", "agriculture", "employee work", "dedication"]), "forbidden_works": json.dumps(["self-employment (some sources)", "leadership"]), "picatrix_reference": "Picatrix BII; Volguine", "picatrix_images": "Image of a figure turning or changing."},
        {"index": 12, "name": "Al-Awwa", "arabic_name": "الأَوَّا", "picatrix_name": "Alahue", "start_sign": "Scorpio", "start_degree": 154.286, "end_degree": 167.143, "ruler_sign": "Aries", "element": "Fire", "meaning": "The Swordsmith. Travel, discernment, writing, analysis. Unhappy first marriage. Good for detective work.", "recommended_works": json.dumps(["travel", "writing", "analysis", "detective work", "discernment"]), "forbidden_works": json.dumps(["first marriage (some sources)", "impulsive decisions"]), "picatrix_reference": "Picatrix BII; Volguine", "picatrix_images": "Image of a swordsmith or figure with weapons."},
        {"index": 13, "name": "Al-Simak", "arabic_name": "السِّمَاك", "picatrix_name": "Azimech", "start_sign": "Sagittarius", "start_degree": 167.143, "end_degree": 180.0, "ruler_sign": "Taurus", "element": "Earth", "meaning": "The Unarmed. Prudent, analytical, interested in divination and experiments. Problems in early marriage that resolve later.", "recommended_works": json.dumps(["divination", "experiments", "analysis", "study", "prudent decisions"]), "forbidden_works": json.dumps(["impulsive marriage", "recklessness"]), "picatrix_reference": "Picatrix BII; Volguine", "picatrix_images": "Image of an unarmed figure."},
        {"index": 14, "name": "Al-Ghafr", "arabic_name": "الغَفْر", "picatrix_name": "Argafra", "start_sign": "Capricorn", "start_degree": 180.0, "end_degree": 192.857, "ruler_sign": "Gemini", "element": "Air", "meaning": "The Covering. Reputation damage through jealous people. Unfavorable for relationships and travel. Only good for discovering hostile schemes or treasure hunting.", "recommended_works": json.dumps(["treasure hunting", "discovering secrets", "protecting reputation"]), "forbidden_works": json.dumps(["marriage", "travel", "public life", "trusting others"]), "picatrix_reference": "Picatrix BII; Volguine", "picatrix_images": "Image of a covered or hidden figure."},
        {"index": 15, "name": "Al-Zubana", "arabic_name": "الزُّبَانَا", "picatrix_name": "Azubene", "start_sign": "Capricorn", "start_degree": 192.857, "end_degree": 205.714, "ruler_sign": "Cancer", "element": "Water", "meaning": "The Claws. Stockbreeding, buying/selling cattle, speculation. Protection through observation and clear judgment.", "recommended_works": json.dumps(["cattle trading", "speculation", "observation", "protection"]), "forbidden_works": json.dumps(["blind trust", "reckless investment"]), "picatrix_reference": "Picatrix BII; Volguine", "picatrix_images": "Image of claws or grasping hands."},
        {"index": 16, "name": "Al-Iklil", "arabic_name": "الإِكْلِيل", "picatrix_name": "Alichil", "start_sign": "Aquarius", "start_degree": 205.714, "end_degree": 218.571, "ruler_sign": "Leo", "element": "Fire", "meaning": "The Crown. Honor, achievement, completion, leadership. Unfavorable for marriage and travel.", "recommended_works": json.dumps(["leadership", "achievement", "honor", "completion"]), "forbidden_works": json.dumps(["marriage (some sources)", "travel (some sources)"]), "picatrix_reference": "Picatrix BII; Volguine", "picatrix_images": "Image of a crown or diadem."},
        {"index": 17, "name": "Al-Qalb", "arabic_name": "القَلْب", "picatrix_name": "Al Kalb", "start_sign": "Aquarius", "start_degree": 218.571, "end_degree": 231.429, "ruler_sign": "Virgo", "element": "Earth", "meaning": "The Heart. Conflict, exposing enemies, war. Unfavorable for family. Threatens premature death of mother.", "recommended_works": json.dumps(["conflict", "exposing enemies", "war", "defense"]), "forbidden_works": json.dumps(["family matters", "peaceful pursuits", "marriage"]), "picatrix_reference": "Picatrix BII; Volguine", "picatrix_images": "Image of a heart or the heart of a scorpion (Antares)."},
        {"index": 18, "name": "Al-Shaulah", "arabic_name": "الشَّوْلَة", "picatrix_name": "Exaula", "start_sign": "Pisces", "start_degree": 231.429, "end_degree": 244.286, "ruler_sign": "Libra", "element": "Air", "meaning": "The Sting. Hunting, personal ideas. Unfavorable for commerce and fixed residence. Good for travel and movement.", "recommended_works": json.dumps(["hunting", "travel", "movement", "personal projects"]), "forbidden_works": json.dumps(["commerce", "settling down", "fixed residence"]), "picatrix_reference": "Picatrix BII; Volguine", "picatrix_images": "Image of a sting or spear."},
        {"index": 19, "name": "Al-Baldah", "arabic_name": "البَلْدَة", "picatrix_name": "Nahaym", "start_sign": "Aries", "start_degree": 244.286, "end_degree": 257.143, "ruler_sign": "Scorpio", "element": "Water", "meaning": "The Town. Love and success through women. Better off with free liaison than marriage. Involuntary changes of residence. Hastens healing.", "recommended_works": json.dumps(["love", "healing", "travel", "women's affairs"]), "forbidden_works": json.dumps(["marriage (some sources)", "staying in one place"]), "picatrix_reference": "Picatrix BII; Volguine", "picatrix_images": "Image of a town or dwelling."},
        {"index": 20, "name": "Al-Sa'd al-Dhabih", "arabic_name": "السَّعْد الذَّابِح", "picatrix_name": "Caadaldeba", "start_sign": "Taurus", "start_degree": 257.143, "end_degree": 270.0, "ruler_sign": "Sagittarius", "element": "Fire", "meaning": "The Fortune of the Slaughterer. Personal power. Escapes consequences of actions. Unfavorable for marriage.", "recommended_works": json.dumps(["personal power", "influence", "authority"]), "forbidden_works": json.dumps(["marriage", "contracts"]), "picatrix_reference": "Picatrix BII; Volguine", "picatrix_images": "Image of a figure with a slaughtered animal."},
        {"index": 21, "name": "Al-Sa'd Bula", "arabic_name": "السَّعْد بُلَع", "picatrix_name": "Caaddebolach", "start_sign": "Gemini", "start_degree": 270.0, "end_degree": 282.857, "ruler_sign": "Capricorn", "element": "Earth", "meaning": "The Fortune of the Swallowing. Doctors, soldiers, politicians. Unfavorable for marriage, children, contracts.", "recommended_works": json.dumps(["medicine", "military", "politics", "leadership"]), "forbidden_works": json.dumps(["marriage", "children", "contracts"]), "picatrix_reference": "Picatrix BII; Volguine", "picatrix_images": "Image of a figure swallowing or a bird."},
        {"index": 22, "name": "Al-Sa'd al-Su'ud", "arabic_name": "السَّعْد السُّعُود", "picatrix_name": "Caadacohot", "start_sign": "Cancer", "start_degree": 282.857, "end_degree": 295.714, "ruler_sign": "Aquarius", "element": "Air", "meaning": "The Fortune of Fortunes. Eventful but ultimately unhappy career. Unfavorable for administration of countries or cities.", "recommended_works": json.dumps(["creative pursuits", "art", "non-administrative work"]), "forbidden_works": json.dumps(["government administration", "high office", "leadership of organizations"]), "picatrix_reference": "Picatrix BII; Volguine", "picatrix_images": "Image of a fortunate figure or rising sun."},
        {"index": 23, "name": "Al-Sa'd al-Akhbiyah", "arabic_name": "السَّعْد الأَخْبِيَة", "picatrix_name": "Caadalhacbia", "start_sign": "Leo", "start_degree": 295.714, "end_degree": 308.571, "ruler_sign": "Pisces", "element": "Water", "meaning": "The Fortune of the Tents. Negative affect on business. Humble, modest, wise, god-fearing. Difficulties with family/parents. Success when traveling abroad.", "recommended_works": json.dumps(["travel abroad", "spiritual pursuits", "humility", "wisdom"]), "forbidden_works": json.dumps(["business affairs", "family dealings", "local ventures"]), "picatrix_reference": "Picatrix BII; Volguine", "picatrix_images": "Image of a tent or hidden figure."},
        {"index": 24, "name": "Al-Fargh al-Muqaddam", "arabic_name": "الفَرْق المُقَدَّم", "picatrix_name": "Almiquedam", "start_sign": "Virgo", "start_degree": 308.571, "end_degree": 321.429, "ruler_sign": "Aries", "element": "Fire", "meaning": "The Fore-pourer. Favorable for marriage, agriculture, buying/selling. Unfavorable for ocean voyages. Covetous, problems with brothers.", "recommended_works": json.dumps(["marriage", "agriculture", "trade", "buying/selling"]), "forbidden_works": json.dumps(["ocean voyages", "brotherhood disputes"]), "picatrix_reference": "Picatrix BII; Volguine", "picatrix_images": "Image of a figure pouring from a vessel."},
        {"index": 25, "name": "Al-Fargh al-Mu'akhkhar", "arabic_name": "الفَرْق المُؤَخَّر", "picatrix_name": "Algarf almuehar", "start_sign": "Libra", "start_degree": 321.429, "end_degree": 334.286, "ruler_sign": "Taurus", "element": "Earth", "meaning": "The After-pourer. Favorable for marriage, achieving responsible position. Strong temper but honored by men. Love of horses and revelry.", "recommended_works": json.dumps(["marriage", "responsible positions", "honor", "equestrian pursuits"]), "forbidden_works": json.dumps(["idleness", "dishonor"]), "picatrix_reference": "Picatrix BII; Volguine", "picatrix_images": "Image of a figure pouring from behind."},
        {"index": 26, "name": "Al-Risha", "arabic_name": "الرِّيشَا", "picatrix_name": "Arrexhe", "start_sign": "Scorpio", "start_degree": 334.286, "end_degree": 347.143, "ruler_sign": "Gemini", "element": "Air", "meaning": "The Rope. Marriage and business success. May suffer ill health. Sign of poverty. Can help in moments of danger.", "recommended_works": json.dumps(["marriage", "business", "danger protection"]), "forbidden_works": json.dumps(["sea voyages", "excessive spending"]), "picatrix_reference": "Picatrix BII; Volguine", "picatrix_images": "Image of a rope or belly."},
    ]
    
    cursor = conn.cursor()
    for m in mansions:
        cursor.execute("""
            INSERT OR REPLACE INTO lunar_mansions_reference 
            (mansion_index, name, arabic_name, picatrix_name, start_sign, start_degree, end_degree,
             ruler_sign, element, meaning, recommended_works, forbidden_works,
             picatrix_reference, source, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            m['index'], m['name'], m['arabic_name'], m['picatrix_name'],
            m['start_sign'], m['start_degree'], m['end_degree'],
            m['ruler_sign'], m['element'], m['meaning'],
            m['recommended_works'], m['forbidden_works'],
            m['picatrix_reference'], 'Picatrix + Arabic Lunar Mansions (Johnson)', 'high'
        ))
    
    conn.commit()
    print(f"Loaded {len(mansions)} lunar mansions")


def load_planetary_correspondences(conn):
    """Load planetary correspondence tables from Picatrix Book III."""
    
    correspondences = []
    
    # Saturn
    for item in ['black', 'dark blue', 'brown-black']:
        correspondences.append(('Saturn', 'color', item, 'Picatrix BIII Ch. Images'))
    for item in ['lead', 'antimony', 'tin']:
        correspondences.append(('Saturn', 'metal', item, 'Picatrix BIII'))
    for item in ['onyx', 'jet', 'obsidian', 'black tourmaline']:
        correspondences.append(('Saturn', 'stone', item, 'Picatrix BIII'))
    for item in ['henbane', 'mandrake', 'nightshade', 'poppy', 'myrrh', 'frankincense']:
        correspondences.append(('Saturn', 'incense', item, 'Picatrix BIII Ch. Suffumigations'))
    for item in ['crows', 'dogs', 'bats', 'owls', 'snakes']:
        correspondences.append(('Saturn', 'animal', item, 'Picatrix BIII'))
    for item in ['feet', 'bones', 'spleen', 'joints']:
        correspondences.append(('Saturn', 'body_part', item, 'Picatrix BIII'))
    for item in ['grave diggers', 'executioners', 'miners', 'potters', 'farmers']:
        correspondences.append(('Saturn', 'profession', item, 'Picatrix BIII'))
    
    # Jupiter
    for item in ['royal blue', 'purple', 'violet']:
        correspondences.append(('Jupiter', 'color', item, 'Picatrix BIII'))
    for item in ['tin', 'bronze', 'electrum']:
        correspondences.append(('Jupiter', 'metal', item, 'Picatrix BIII'))
    for item in ['sapphire', 'amethyst', 'lapis lazuli', 'turquoise', 'jacinth']:
        correspondences.append(('Jupiter', 'stone', item, 'Picatrix BIII'))
    for item in ['frankincense', 'saffron', 'cinnamon', 'balsam', 'myrtle']:
        correspondences.append(('Jupiter', 'incense', item, 'Picatrix BIII Ch. Suffumigations'))
    for item in ['eagles', 'stags', 'oxen', 'elephants', 'peacocks']:
        correspondences.append(('Jupiter', 'animal', item, 'Picatrix BIII'))
    for item in ['liver', 'thighs', 'digestion']:
        correspondences.append(('Jupiter', 'body_part', item, 'Picatrix BIII'))
    for item in ['kings', 'judges', 'scholars', 'clergy', 'bankers']:
        correspondences.append(('Jupiter', 'profession', item, 'Picatrix BIII'))
    
    # Mars
    for item in ['red', 'scarlet', 'crimson', 'blood red']:
        correspondences.append(('Mars', 'color', item, 'Picatrix BIII'))
    for item in ['iron', 'steel', 'copper-red']:
        correspondences.append(('Mars', 'metal', item, 'Picatrix BIII'))
    for item in ['ruby', 'garnet', 'bloodstone', 'carnelian', 'jasper', 'diamond']:
        correspondences.append(('Mars', 'stone', item, 'Picatrix BIII'))
    for item in ['sulfur', 'pepper', 'garlic', 'mustard', 'nettle', 'onion']:
        correspondences.append(('Mars', 'incense', item, 'Picatrix BIII Ch. Suffumigations'))
    for item in ['lions', 'wolves', 'tigers', 'hawks', 'falcons', 'scorpions']:
        correspondences.append(('Mars', 'animal', item, 'Picatrix BIII'))
    for item in ['genitals', 'muscles', 'blood', 'head', 'gallbladder']:
        correspondences.append(('Mars', 'body_part', item, 'Picatrix BIII'))
    for item in ['soldiers', 'surgeons', 'blacksmiths', 'butchers', 'barbers']:
        correspondences.append(('Mars', 'profession', item, 'Picatrix BIII'))
    
    # Sun
    for item in ['gold', 'yellow', 'orange', 'amber']:
        correspondences.append(('Sun', 'color', item, 'Picatrix BIII'))
    for item in ['gold', 'brass', 'bronze-yellow']:
        correspondences.append(('Sun', 'metal', item, 'Picatrix BIII'))
    for item in ['diamond', 'topaz', 'citrine', 'amber', 'heliotrope', 'sunstone']:
        correspondences.append(('Sun', 'stone', item, 'Picatrix BIII'))
    for item in ['frankincense', 'saffron', 'bay laurel', 'rosemary', 'mastic']:
        correspondences.append(('Sun', 'incense', item, 'Picatrix BIII Ch. Suffumigations'))
    for item in ['lions', 'roosters', 'peacocks', 'swans', 'cranes']:
        correspondences.append(('Sun', 'animal', item, 'Picatrix BIII'))
    for item in ['heart', 'spine', 'eyes', 'vital spirit']:
        correspondences.append(('Sun', 'body_part', item, 'Picatrix BIII'))
    for item in ['kings', 'princes', 'artists', 'performers', 'jewelers']:
        correspondences.append(('Sun', 'profession', item, 'Picatrix BIII'))
    
    # Venus
    for item in ['white', 'rose', 'pink', 'light green', 'cream']:
        correspondences.append(('Venus', 'color', item, 'Picatrix BIII'))
    for item in ['silver', 'copper', 'electrum']:
        correspondences.append(('Venus', 'metal', item, 'Picatrix BIII'))
    for item in ['emerald', 'jade', 'rose quartz', 'pearl', 'coral', 'lapis-green']:
        correspondences.append(('Venus', 'stone', item, 'Picatrix BIII'))
    for item in ['rose', 'violet', 'sandalwood', 'myrrh', 'camphor', 'musk', 'ambergris']:
        correspondences.append(('Venus', 'incense', item, 'Picatrix BIII Ch. Suffumigations'))
    for item in ['doves', 'swans', 'rabbits', 'cats', 'gazelles', 'bees']:
        correspondences.append(('Venus', 'animal', item, 'Picatrix BIII'))
    for item in ['kidneys', 'reproductive system', 'throat', 'skin', 'fat']:
        correspondences.append(('Venus', 'body_part', item, 'Picatrix BIII'))
    for item in ['musicians', 'artists', 'perfumers', 'courtesans', 'jewelers', 'gardeners']:
        correspondences.append(('Venus', 'profession', item, 'Picatrix BIII'))
    
    # Mercury
    for item in ['mixed colors', 'variegated', 'silver-green', 'gray-blue']:
        correspondences.append(('Mercury', 'color', item, 'Picatrix BIII'))
    for item in ['mercury (quicksilver)', 'tin-silver', 'mixed alloys']:
        correspondences.append(('Mercury', 'metal', item, 'Picatrix BIII'))
    for item in ['emerald', 'agate', 'beryl', 'chrysoprase', 'carnelian']:
        correspondences.append(('Mercury', 'stone', item, 'Picatrix BIII'))
    for item in ['cinnamon', 'cassia', 'clove', 'mastic', 'anise', 'fennel']:
        correspondences.append(('Mercury', 'incense', item, 'Picatrix BIII Ch. Suffumigations'))
    for item in ['monkeys', 'foxes', 'weasels', 'swallows', 'parrots', 'spiders']:
        correspondences.append(('Mercury', 'animal', item, 'Picatrix BIII'))
    for item in ['nervous system', 'tongue', 'lungs', 'arms', 'hands']:
        correspondences.append(('Mercury', 'body_part', item, 'Picatrix BIII'))
    for item in ['merchants', 'scribes', 'astrologers', 'philosophers', 'teachers', 'orators']:
        correspondences.append(('Mercury', 'profession', item, 'Picatrix BIII'))
    
    # Moon
    for item in ['white', 'silver', 'pearl', 'pale blue', 'iridescent']:
        correspondences.append(('Moon', 'color', item, 'Picatrix BIII'))
    for item in ['silver', 'pewter', 'tin']:
        correspondences.append(('Moon', 'metal', item, 'Picatrix BIII'))
    for item in ['moonstone', 'pearl', 'crystal', 'selenite', 'opal', 'aquamarine']:
        correspondences.append(('Moon', 'stone', item, 'Picatrix BIII'))
    for item in ['camphor', 'white sandalwood', 'jasmine', 'rose-water', 'myrrh']:
        correspondences.append(('Moon', 'incense', item, 'Picatrix BIII Ch. Suffumigations'))
    for item in ['owls', 'cats', 'hares', 'frogs', 'cranes', 'geese', 'dolphins']:
        correspondences.append(('Moon', 'animal', item, 'Picatrix BIII'))
    for item in ['brain', 'breasts', 'stomach', 'lymph', 'body fluids', 'left eye']:
        correspondences.append(('Moon', 'body_part', item, 'Picatrix BIII'))
    for item in ['sailors', 'midwives', 'nurses', 'dreamers', 'psychics', 'agriculturalists']:
        correspondences.append(('Moon', 'profession', item, 'Picatrix BIII'))
    
    cursor = conn.cursor()
    for planet, category, item, ref in correspondences:
        cursor.execute("""
            INSERT INTO planetary_correspondences (planet, category, item, picatrix_reference, source, confidence)
            VALUES (?, ?, ?, ?, 'Picatrix BIII', 'high')
        """, (planet, category, item, ref))
    
    conn.commit()
    print(f"Loaded {len(correspondences)} planetary correspondences")


def load_fixed_stars(conn):
    """Load fixed stars mentioned in Picatrix."""
    
    stars = [
        ("Algol", "الغول", "Perseus", 26.3, 2.14, "Saturn+Mars", "The Ghoul. Violence, decapitation, revenge. Unfavorable for most operations.", "Picatrix BII Ch. Fixed Stars"),
        ("Pleiades", "الثريا", "Taurus", 28.5, 2.87, "Moon+Mars", "The Cluster. Love, friendship, wounds from iron. Favorable for education.", "Picatrix BII; Al-Thurayya mansion"),
        ("Aldebaran", "الدبران", "Taurus", 51.5, 0.87, "Mars+Venus", "The Follower. Passion, determination, wealth. Favorable for love and passion.", "Picatrix BII; Al-Dabaran mansion"),
        ("Antares", "قلب العقرب", "Scorpio", 218.0, 1.06, "Mars+Jupiter", "The Heart of the Scorpion. Conflict, courage, war. Favorable for war, unfavorable for family.", "Picatrix BII; Al-Qalb mansion"),
        ("Fomalhaut", "فم الحوت", "Aquarius", 320.0, 1.16, "Venus+Mercury", "The Fish's Mouth. Magic, occult knowledge, fame. Favorable for magical operations.", "Picatrix BII"),
        ("Regulus", "قلب الأسد", "Leo", 129.5, 1.36, "Jupiter+Mars", "The Heart of the Lion. Leadership, victory, royal favor. Favorable for authority.", "Picatrix BII"),
        ("Spica", "السنبلة", "Virgo", 203.5, 0.98, "Venus+Mars", "The Ear of Corn. Harvest, abundance, wisdom. Favorable for agriculture and education.", "Picatrix BII"),
        ("Vega", "النسر الواقع", "Aquarius", 284.5, 0.03, "Venus+Mercury", "The Falling Eagle. Artistic talent, ambition, political power. Favorable for arts and politics.", "Picatrix BII"),
        ("Sirius", "الشعرى", "Gemini", 104.0, -1.46, "Jupiter+Mars", "The Scorching. Fame, wealth, fire. Favorable for wealth, unfavorable for health in excess.", "Picatrix BII"),
        ("Canopus", "سهيل", "Carina", 95.5, -0.74, "Saturn+Jupiter", "The Southern Star. Navigation, wisdom, guidance. Favorable for travel and teaching.", "Picatrix BII"),
        ("Capriceornus", "الجدي", "Capricorn", 297.5, 0.28, "Jupiter+Mars", "The Goat. Abundance, fertility, protection. Favorable for agriculture.", "Picatrix BII"),
        ("Alphecca", "الفكة", "Libra", 226.0, 2.21, "Venus+Mars", "The Broken. Union, marriage, justice. Favorable for legal matters and marriage.", "Picatrix BII"),
        ("Deneb", "ذنب الدجاجة", "Aquarius", 310.5, 1.25, "Venus+Jupiter", "The Tail of the Hen. Writing, art, hidden knowledge. Favorable for creative work.", "Picatrix BII"),
        ("Betelgeuse", "يد الجوزاء", "Gemini", 88.5, 0.50, "Mars+Jupiter", "The Hand of the Central One. War, courage, destruction. Favorable for military operations.", "Picatrix BII"),
        ("Rigel", "رجل الجوزاء", "Gemini", 77.5, 0.13, "Jupiter+Saturn", "The Foot of the Central One. Teaching, law, structure. Favorable for education and law.", "Picatrix BII"),
    ]
    
    cursor = conn.cursor()
    for name, arabic, constellation, lon, mag, nature, desc, ref in stars:
        cursor.execute("""
            INSERT INTO fixed_stars (name, arabic_name, constellation, longitude, magnitude, nature, description, picatrix_reference, source, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Picatrix BII', 'high')
        """, (name, arabic, constellation, lon, mag, nature, desc, ref))
    
    conn.commit()
    print(f"Loaded {len(stars)} fixed stars")


def load_seasonal_correspondences(conn):
    """Load seasonal correspondences from Picatrix."""
    
    seasons = [
        ("Spring", "Aries", "Mars", "Fire", "Time of beginning, growth, planting. Favorable for new ventures, travel, starting battles.", json.dumps(["planting", "new ventures", "travel", "starting battles", "building"]), "Picatrix BIII Ch. Seasons"),
        ("Spring", "Taurus", "Venus", "Earth", "Time of growth, consolidation, love. Favorable for marriage, agriculture, building.", json.dumps(["marriage", "agriculture", "building", "love", "financial matters"]), "Picatrix BIII Ch. Seasons"),
        ("Spring", "Gemini", "Mercury", "Air", "Time of communication, commerce. Favorable for trade, writing, learning.", json.dumps(["trade", "writing", "learning", "communication", "negotiations"]), "Picatrix BIII Ch. Seasons"),
        ("Summer", "Cancer", "Moon", "Water", "Time of nurturing, home. Favorable for domestic matters, family, agriculture.", json.dumps(["domestic matters", "family", "agriculture", "nurturing", "building"]), "Picatrix BIII Ch. Seasons"),
        ("Summer", "Leo", "Sun", "Fire", "Time of power, authority. Favorable for leadership, recognition, royal favor.", json.dumps(["leadership", "recognition", "royal favor", "authority", "public life"]), "Picatrix BIII Ch. Seasons"),
        ("Summer", "Virgo", "Mercury", "Earth", "Time of harvest, health. Favorable for medicine, agriculture, crafts.", json.dumps(["harvest", "medicine", "crafts", "agriculture", "health"]), "Picatrix BIII Ch. Seasons"),
        ("Autumn", "Libra", "Venus", "Air", "Time of balance, justice. Favorable for legal matters, partnerships, art.", json.dumps(["legal matters", "partnerships", "art", "balance", "justice"]), "Picatrix BIII Ch. Seasons"),
        ("Autumn", "Scorpio", "Mars", "Water", "Time of transformation, secrets. Favorable for magic, war, destruction.", json.dumps(["magic", "war", "destruction", "secrets", "transformation"]), "Picatrix BIII Ch. Seasons"),
        ("Autumn", "Sagittarius", "Jupiter", "Fire", "Time of wisdom, travel. Favorable for philosophy, long journeys, teaching.", json.dumps(["philosophy", "travel", "teaching", "wisdom", "religion"]), "Picatrix BIII Ch. Seasons"),
        ("Winter", "Capricorn", "Saturn", "Earth", "Time of structure, discipline. Favorable for building, boundaries, protection.", json.dumps(["building", "boundaries", "protection", "discipline", "long-term planning"]), "Picatrix BIII Ch. Seasons"),
        ("Winter", "Aquarius", "Saturn", "Air", "Time of innovation, community. Favorable for science, friendship, reform.", json.dumps(["science", "friendship", "reform", "innovation", "community"]), "Picatrix BIII Ch. Seasons"),
        ("Winter", "Pisces", "Jupiter", "Water", "Time of dreams, spirituality. Favorable for religion, dreams, healing.", json.dumps(["religion", "dreams", "healing", "spirituality", "art"]), "Picatrix BIII Ch. Seasons"),
    ]
    
    cursor = conn.cursor()
    for season, sign, planet, element, desc, ops, ref in seasons:
        cursor.execute("""
            INSERT INTO seasonal_correspondences (season, sign, planet, element, description, operations, picatrix_reference, source, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'Picatrix BIII', 'high')
        """, (season, sign, planet, element, desc, ops, ref))
    
    conn.commit()
    print(f"Loaded {len(seasons)} seasonal correspondences")


def load_talismanic_timings(conn):
    """Load talismanic timing rules from Picatrix."""
    
    timings = [
        ("Sun", "Royal authority, favor", "Sunday", "Sun hour", "Leo", None, "Sun in Leo", "Make images of authority on Sunday in Sun hour with Leo rising", "Picatrix BII Ch. Images"),
        ("Sun", "Recognition, fame", "Sunday", "Sun hour", "Aries", None, "Sun conjunct ASC", "Make images of recognition on Sunday in Sun hour", "Picatrix BII Ch. Images"),
        ("Moon", "Travel, navigation, dreams", "Monday", "Moon hour", "Cancer", None, "Moon in Cancer", "Make images of travel on Monday in Moon hour", "Picatrix BII Ch. Images"),
        ("Moon", "Love, reconciliation", "Monday", "Moon hour", "Taurus", None, "Moon trine Venus", "Make images of love on Monday in Moon hour", "Picatrix BII Ch. Images"),
        ("Mars", "Courage, war, victory", "Tuesday", "Mars hour", "Aries", "Al-Sharatain", "Mars in Aries", "Make images of war on Tuesday in Mars hour with Mars in Aries", "Picatrix BII Ch. Images"),
        ("Mars", "Protection from enemies", "Tuesday", "Mars hour", "Scorpio", None, "Mars in Scorpio", "Make images of protection on Tuesday in Mars hour", "Picatrix BII Ch. Images"),
        ("Mercury", "Intellect, commerce, eloquence", "Wednesday", "Mercury hour", "Gemini", None, "Mercury in Gemini", "Make images of commerce on Wednesday in Mercury hour", "Picatrix BII Ch. Images"),
        ("Mercury", "Writing, science, divination", "Wednesday", "Mercury hour", "Virgo", None, "Mercury in Virgo", "Make images of writing on Wednesday in Mercury hour", "Picatrix BII Ch. Images"),
        ("Jupiter", "Wealth, fortune, wisdom", "Thursday", "Jupiter hour", "Sagittarius", None, "Jupiter in Sagittarius", "Make images of wealth on Thursday in Jupiter hour", "Picatrix BII Ch. Images"),
        ("Jupiter", "Honor, learning, friendship", "Thursday", "Jupiter hour", "Pisces", None, "Jupiter in Pisces", "Make images of honor on Thursday in Jupiter hour", "Picatrix BII Ch. Images"),
        ("Venus", "Love, beauty, pleasure", "Friday", "Venus hour", "Taurus", None, "Venus in Taurus", "Make images of love on Friday in Venus hour", "Picatrix BII Ch. Images"),
        ("Venus", "Art, music, joy", "Friday", "Venus hour", "Libra", None, "Venus in Libra", "Make images of art on Friday in Venus hour", "Picatrix BII Ch. Images"),
        ("Saturn", "Protection, boundaries, discipline", "Saturday", "Saturn hour", "Capricorn", None, "Saturn in Capricorn", "Make images of protection on Saturday in Saturn hour", "Picatrix BII Ch. Images"),
        ("Saturn", "Banishing, long-term works", "Saturday", "Saturn hour", "Aquarius", None, "Saturn in Aquarius", "Make images of banishing on Saturday in Saturn hour", "Picatrix BII Ch. Images"),
    ]
    
    cursor = conn.cursor()
    for planet, operation, day, hour, sign, mansion, aspect, desc, ref in timings:
        cursor.execute("""
            INSERT INTO talismanic_timings (planet, operation, required_day, required_hour, required_sign, required_mansion, required_aspect, description, picatrix_reference, source, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Picatrix BII-BIII', 'high')
        """, (planet, operation, day, hour, sign, mansion, aspect, desc, ref))
    
    conn.commit()
    print(f"Loaded {len(timings)} talismanic timing rules")


def load_elections(conn):
    """Load electional rules from Picatrix."""
    
    elections = [
        # Love and relationships
        ("love", "Attracting love", "good", "Venus", "Taurus", None, "Friday", "Venus hour", "Make images of love when Venus is strong. Dress in white, use rose incense.", "Picatrix BIII Ch. 12"),
        ("love", "Reconciliation", "good", "Venus", "Libra", None, "Friday", "Venus hour", "Make images of reconciliation when Venus is well-placed.", "Picatrix BIII Ch. 12"),
        ("love", "Destroying love", "bad", "Mars", "Scorpio", None, "Tuesday", "Mars hour", "Make images of separation when Mars is strong.", "Picatrix BIII Ch. 12"),
        
        # Business and wealth
        ("business", "Starting a business", "good", "Jupiter", "Sagittarius", None, "Thursday", "Jupiter hour", "Begin new business when Jupiter is in a fortunate position.", "Picatrix BIII Ch. Operations"),
        ("business", "Financial gain", "good", "Jupiter", "Pisces", None, "Thursday", "Jupiter hour", "Make images of wealth when Jupiter is strong.", "Picatrix BIII Ch. Operations"),
        ("business", "Commerce", "good", "Mercury", "Gemini", None, "Wednesday", "Mercury hour", "Begin commercial activities when Mercury is well-aspected.", "Picatrix BIII Ch. Operations"),
        
        # Travel
        ("travel", "Safe journey", "good", "Moon", "Cancer", None, "Monday", "Moon hour", "Begin travel when Moon is well-aspected and in fortunate mansion.", "Picatrix BIII Ch. Operations"),
        ("travel", "Sea voyage", "neutral", "Moon", "Cancer", None, "Monday", "Moon hour", "Sea voyages favored when Moon is in water signs. Avoid when Moon is afflicted.", "Picatrix BIII Ch. Operations"),
        ("travel", "Avoid travel", "bad", "Saturn", "Capricorn", None, "Saturday", "Saturn hour", "Avoid travel when Saturn is afflicting the Moon or ASC.", "Picatrix BIII Ch. Operations"),
        
        # Health
        ("health", "Healing", "good", "Sun", "Leo", None, "Sunday", "Sun hour", "Make images of healing when Sun is strong. Favorable for recovery.", "Picatrix BIII Ch. Operations"),
        ("health", "Medicine preparation", "good", "Mercury", "Virgo", None, "Wednesday", "Mercury hour", "Prepare medicines when Mercury is well-aspected.", "Picatrix BIII Ch. Operations"),
        ("health", "Avoid treatment", "bad", "Mars", "Aries", None, "Tuesday", "Mars hour", "Avoid surgery or aggressive treatment when Mars is afflicting.", "Picatrix BIII Ch. Operations"),
        
        # War and conflict
        ("war", "Victory in battle", "good", "Mars", "Aries", "Al-Sharatain", "Tuesday", "Mars hour", "Make images of war when Mars is in Aries or Scorpio.", "Picatrix BIII Ch. Operations"),
        ("war", "Protection from enemies", "good", "Mars", "Scorpio", None, "Tuesday", "Mars hour", "Make images of protection when Mars is strong.", "Picatrix BIII Ch. Operations"),
        ("war", "Destroying enemies", "good", "Mars", "Leo", None, "Tuesday", "Mars hour", "Make images of destruction when Mars is in fire signs.", "Picatrix BIII Ch. Operations"),
        
        # Agriculture
        ("agriculture", "Planting", "good", "Moon", "Cancer", None, "Monday", "Moon hour", "Plant when Moon is in water or earth signs and in fortunate mansion.", "Picatrix BIII Ch. Operations"),
        ("agriculture", "Harvesting", "good", "Sun", "Virgo", None, "Sunday", "Sun hour", "Harvest when Sun or Moon is in earth signs.", "Picatrix BIII Ch. Operations"),
        
        # Ritual and magic
        ("ritual", "Invocation of spirits", "good", "Mercury", "Gemini", None, "Wednesday", "Mercury hour", "Invoke planetary spirits on their days in their hours.", "Picatrix BIII Ch. 9"),
        ("ritual", "Making talismans", "good", None, None, None, None, None, "Make talismans on the day and hour of the ruling planet, with the planet strong.", "Picatrix BII Ch. Images"),
        ("ritual", "Banishing", "good", "Saturn", "Capricorn", None, "Saturday", "Saturn hour", "Make images of banishing when Saturn is strong.", "Picatrix BIII Ch. Operations"),
        
        # Forbidden times
        ("general", "Avoid new ventures", "forbidden", "Saturn", None, None, "Saturday", "Saturn hour", "Saturday in Saturn hour is unfavorable for most new undertakings.", "Picatrix BIII"),
        ("general", "Avoid marriage", "forbidden", "Saturn", None, None, "Saturday", "Saturn hour", "Avoid marriage in Saturn hour on Saturday.", "Picatrix BIII"),
        ("general", "Avoid travel", "forbidden", "Mars", None, None, "Tuesday", "Mars hour", "Avoid long travel in Mars hour when Mars is afflicted.", "Picatrix BIII"),
    ]
    
    cursor = conn.cursor()
    for category, operation, rating, planet, sign, mansion, day, hour, desc, ref in elections:
        cursor.execute("""
            INSERT INTO elections (date, category, operation, rating, planet, sign, mansion, day_ruler, hour_ruler, description, picatrix_reference, source, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Picatrix', 'high')
        """, ('recurring', category, operation, rating, planet, sign, mansion, day, hour, desc, ref))
    
    conn.commit()
    print(f"Loaded {len(elections)} electional rules")


def initialize():
    """Initialize the complete database."""
    conn = create_database()
    load_reference_data(conn)
    load_planetary_correspondences(conn)
    load_fixed_stars(conn)
    load_seasonal_correspondences(conn)
    load_talismanic_timings(conn)
    load_elections(conn)
    conn.close()
    print(f"\n✅ Picatrix Calendar database created at: {DB_PATH}")


if __name__ == '__main__':
    initialize()
