#!/usr/bin/env python3
"""Merge full Quran (Uthmani + Sahih Intl) and 3 Hadith books into complete JSON."""
import json, sys, os

OUTPUT = os.path.join(os.path.dirname(__file__), 'quran_hadith_data.json')

# ─── LOAD QURAN ───
print("Loading Quran data...")
with open('/tmp/quran_uthmani.json') as f:
    uthmani = json.load(f)
with open('/tmp/quran_en_sahih.json') as f:
    sahih = json.load(f)

# Surah name map (English)
SURAH_NAMES = [
    "","Al-Fatiha","Al-Baqarah","Aal-e-Imran","An-Nisa","Al-Maidah","Al-An'am","Al-A'raf",
    "Al-Anfal","At-Tawbah","Yunus","Hud","Yusuf","Ar-Ra'd","Ibrahim","Al-Hijr","An-Nahl",
    "Al-Isra","Al-Kahf","Maryam","Ta-Ha","Al-Anbiya","Al-Hajj","Al-Mu'minun","An-Nur",
    "Al-Furqan","Ash-Shu'ara","An-Naml","Al-Qasas","Al-Ankabut","Ar-Rum","Luqman","As-Sajda",
    "Al-Ahzab","Saba","Fatir","Ya-Sin","As-Saffat","Sad","Az-Zumar","Ghafir","Fussilat",
    "Ash-Shura","Az-Zukhruf","Ad-Dukhan","Al-Jathiya","Al-Ahqaf","Muhammad","Al-Fath",
    "Al-Hujurat","Qaf","Adh-Dhariyat","At-Tur","An-Najm","Al-Qamar","Ar-Rahman","Al-Waqia",
    "Al-Hadid","Al-Mujadila","Al-Hashr","Al-Mumtahina","As-Saff","Al-Jumua","Al-Munafiqun",
    "At-Taghabun","At-Talaq","At-Tahrim","Al-Mulk","Al-Qalam","Al-Haaqqa","Al-Maarij","Nuh",
    "Al-Jinn","Al-Muzzammil","Al-Muddaththir","Al-Qiyama","Al-Insan","Al-Mursalat","An-Naba",
    "An-Naziat","Abasa","At-Takwir","Al-Infitar","Al-Mutaffifin","Al-Inshiqaq","Al-Buruj",
    "At-Tariq","Al-A'la","Al-Ghashiya","Al-Fajr","Al-Balad","Ash-Shams","Al-Lail","Ad-Duha",
    "Ash-Sharh","At-Tin","Al-Alaq","Al-Qadr","Al-Bayyina","Az-Zalzala","Al-Adiyat",
    "Al-Qaria","At-Takathur","Al-Asr","Al-Humaza","Al-Fil","Quraish","Al-Ma'un","Al-Kawthar",
    "Al-Kafirun","An-Nasr","Al-Masad","Al-Ikhlas","Al-Falaq","An-Nas"
]

# Build merged Quran
quran = []
u_surahs = uthmani['data']['surahs']
s_surahs = sahih['data']['surahs']

surah_themes = {
    1:"Faith",2:"Law",3:"Faith",4:"Law",5:"Law",6:"Faith",7:"History",8:"War",
    9:"Law",10:"History",11:"History",12:"History",13:"Faith",14:"Faith",15:"History",
    16:"Mercy",17:"Spiritual",18:"Spiritual",19:"History",20:"History",21:"History",
    22:"Faith",23:"Faith",24:"Law",25:"Faith",26:"History",27:"History",28:"History",
    29:"Faith",30:"Faith",31:"Wisdom",32:"Faith",33:"Law",34:"History",35:"Faith",
    36:"Faith",37:"Faith",38:"Faith",39:"Faith",40:"Faith",41:"Faith",42:"Faith",
    43:"History",44:"Faith",45:"Faith",46:"History",47:"War",48:"War",49:"Law",
    50:"Faith",51:"Faith",52:"Faith",53:"Faith",54:"Faith",55:"Mercy",56:"Faith",
    57:"Faith",58:"Law",59:"Faith",60:"Law",61:"Faith",62:"Faith",63:"Faith",
    64:"Wisdom",65:"Law",66:"Law",67:"Faith",68:"Faith",69:"Faith",70:"Faith",
    71:"History",72:"Faith",73:"Spiritual",74:"Spiritual",75:"Faith",76:"Faith",
    77:"Faith",78:"Faith",79:"Faith",80:"Wisdom",81:"Faith",82:"Faith",83:"Faith",
    84:"Faith",85:"Faith",86:"Faith",87:"Faith",88:"Faith",89:"History",90:"Wisdom",
    91:"Faith",92:"Faith",93:"Mercy",94:"Mercy",95:"Faith",96:"Spiritual",97:"Spiritual",
    98:"Faith",99:"Faith",100:"Faith",101:"Faith",102:"Wisdom",103:"Wisdom",
    104:"Wisdom",105:"History",106:"Mercy",107:"Mercy",108:"Mercy",109:"Faith",
    110:"Faith",111:"Wisdom",112:"Faith",113:"Faith",114:"Faith"
}

for su_idx in range(114):
    u_sura = u_surahs[su_idx]
    s_sura = s_surahs[su_idx]
    surah_num = u_sura['number']
    surah_name_ar = u_sura['name']
    # Get english name
    surah_name_en = SURAH_NAMES[surah_num] if surah_num < len(SURAH_NAMES) else f"Surah {surah_num}"
    # Get revelation type
    revelation_type = u_sura.get('revelationType', s_sura.get('revelationType', 'Meccan'))
    theme = surah_themes.get(surah_num, "Faith")
    
    for ay_idx in range(len(u_sura['ayahs'])):
        u_ayah = u_sura['ayahs'][ay_idx]
        s_ayah = s_sura['ayahs'][ay_idx]
        ayah_num = u_ayah['numberInSurah']
        global_num = u_ayah['number']
        juz = u_ayah.get('juz', 0)
        hizb = u_ayah.get('hizbQuarter', 0)
        
        quran.append({
            "surah": surah_num,
            "surahName": surah_name_ar,
            "surahNameEn": surah_name_en,
            "ayah": ayah_num,
            "number": global_num,
            "juz": juz,
            "hizbQuarter": hizb,
            "revelationType": revelation_type,
            "theme": theme,
            "arabic": u_ayah['text'].strip(),
            "translation": s_ayah['text'].strip()
        })

print(f"Quran merged: {len(quran)} verses")

# ─── LOAD HADITH ───
print("Loading hadith books...")
hadith_all = []

for book_file, en_name, ar_name, en_author, ar_author, abbr in [
    ('/tmp/bukhari.json', 'Sahih al-Bukhari', 'صحيح البخاري',
     'Imam Muhammad ibn Ismail al-Bukhari', 'الإمام محمد بن إسماعيل البخاري', 'bukhari'),
    ('/tmp/muslim.json', 'Sahih Muslim', 'صحيح مسلم',
     'Imam Muslim ibn al-Hajjaj al-Naysaburi', 'الإمام مسلم بن الحجاج القشيري النيسابوري', 'muslim'),
    ('/tmp/abudawud.json', 'Sunan Abi Dawud', 'سنن أبي داود',
     'Imam Sulayman ibn al-Ash\'ath Abu Dawud al-Sijistani',
     'الإمام سليمان بن الأشعث أبو داود السجستاني', 'abudawud')
]:
    with open(book_file) as f:
        book = json.load(f)
    
    hadith_count = len(book['hadiths'])
    print(f"  {en_name}: {hadith_count} hadiths")
    
    for h in book['hadiths']:
        hadith_all.append({
            "id": h['id'],
            "idInBook": h['idInBook'],
            "chapterId": h['chapterId'],
            "book": abbr,
            "bookName": en_name,
            "bookNameAr": ar_name,
            "bookAuthor": en_author,
            "bookAuthorAr": ar_author,
            "narrator": "",  # Will extract from english/narrator
            "arabic": h['arabic'].strip(),
            "english": h['english']['text'].strip() if isinstance(h.get('english'), dict) and 'text' in h['english'] else (h.get('english','') or ''),
            "narratorEn": h['english']['narrator'] if isinstance(h.get('english'), dict) and 'narrator' in h['english'] else ''
        })

print(f"Hadith total: {len(hadith_all)}")

# ─── SAVE ───
output = {
    "quran": quran,
    "hadith": hadith_all,
    "metadata": {
        "quran": {
            "totalVerses": len(quran),
            "totalSurahs": 114,
            "script": "Uthmani (Mushaf al-Madinah)",
            "translation": "Sahih International",
            "source": "Al Quran Cloud API (alquran.cloud)"
        },
        "hadith": {
            "total": len(hadith_all),
            "books": [
                {"id": "bukhari", "name": "Sahih al-Bukhari", "hadithCount": sum(1 for h in hadith_all if h['book']=='bukhari')},
                {"id": "muslim", "name": "Sahih Muslim", "hadithCount": sum(1 for h in hadith_all if h['book']=='muslim')},
                {"id": "abudawud", "name": "Sunan Abi Dawud", "hadithCount": sum(1 for h in hadith_all if h['book']=='abudawud')}
            ],
            "source": "AhmedBaset/hadith-json v1.2.0 (Sunnah.com)"
        }
    },
    "themes": sorted(set(v['theme'] for v in quran))
}

print(f"\nWriting to {OUTPUT}...")
with open(OUTPUT, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

file_size = os.path.getsize(OUTPUT)
print(f"Done! File: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
print(f"  Quran: {len(quran):,} verses")
print(f"  Hadith: {len(hadith_all):,} narrations")
print(f"  Themes: {sorted(set(v['theme'] for v in quran))}")
