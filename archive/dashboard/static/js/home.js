// ══════════ HOME PAGE — Load Everything ══════════
async function loadHome() {
  try {
    const data = await loadJSON('/api/home');
    const ia = data.islamic_astro || {};
    const en = data.energy || {};
    const tarot = data.tarot || {};
    const qh = data.quran_hadith || {};
    const hour = data.planetary_hour || {};

    // Update obs-quick-info with energy/moon data
    const mp = ia.moon_phase || {};
    const mn = ia.mansion || {};
    const nak = ia.nakshatra || {};
    const dasha = ia.dasha || {};
    const cd = dasha.current_dasha || {};
    const cb = dasha.current_bhukti || {};

    document.getElementById('obs-quick-info').innerHTML = `
      <div class="quick-info-row"><span class="quick-info-label">Moon Phase</span><span class="quick-info-value">${mp.emoji||'🌙'} ${mp.phase||'—'}</span></div>
      <div class="quick-info-row"><span class="quick-info-label">Lunar Mansion</span><span class="quick-info-value">${mn.picatrix_name||'—'}</span></div>
      <div class="quick-info-row"><span class="quick-info-label">Day Ruler</span><span class="quick-info-value">${ia.day_ruler||'—'}</span></div>
      <div class="quick-info-row"><span class="quick-info-label">Polarity</span><span class="quick-info-value">${en.polarity||'—'}</span></div>
      <div class="quick-info-row"><span class="quick-info-label">Dominant Elem</span><span class="quick-info-value">${en.dominant_element||'—'}</span></div>
      <div class="quick-info-row"><span class="quick-info-label">Planetary Hour</span><span class="quick-info-value">${hour.planet||'—'} (${hour.spirit_name||''})</span></div>
    `;

    // Bottom cards
    document.getElementById('obs-mansion').innerHTML = `
      <div style="font-size:11px;line-height:1.6">
        <strong>${mn.picatrix_name||'—'}</strong> ${mn.arabic_name||''}<br>
        <em>${mn.meaning||''}</em><br><br>
        Nature: ${mn.nature||'—'}<br>
        Ruler: ${mn.planetary_ruler||'—'}<br>
        Spirit: ${mn.spirit||'—'}<br>
        <br>
        <strong>Benefic:</strong> ${mn.benefic||'—'}<br>
        <strong>Malefic:</strong> ${mn.malefic||'—'}
      </div>`;

    document.getElementById('obs-nakshatra').innerHTML = `
      <div style="font-size:11px;line-height:1.6">
        <strong>${nak.name||'—'}</strong> ${nak.sanskrit||''}<br>
        Pada ${nak.pada||'—'} · Lord: ${nak.lord||'—'} · ${nak.gana||'—'} · ${nak.guna||'—'}<br>
        ${nak.meaning||''}
        <br><br>
        <strong>Mahadasha:</strong> ${cd.lord||'—'} (${cd.start?cd.start.slice(0,10):'—'} → ${cd.end?cd.end.slice(0,10):'—'})<br>
        <strong>Bhukti:</strong> ${cb.lord||'—'} (${cb.start?cb.start.slice(0,10):'—'} → ${cb.end?cb.end.slice(0,10):'—'})<br>
        Birth: ${dasha.birth_nakshatra||'—'} (lord ${dasha.birth_nakshatra_lord||'—'})
      </div>`;

    document.getElementById('obs-tarot').innerHTML = `
      <div style="font-size:11px;line-height:1.6">
        <strong>${tarot.name||'—'}</strong><br>
        ${(tarot.keywords||[]).join(' · ')}<br>
        <em>${tarot.daily_message||''}</em>
      </div>`;

    const quran = qh.quran || {};
    const hadith = qh.hadith || {};
    document.getElementById('obs-quran').innerHTML = `
      <div style="font-size:11px;line-height:1.6">
        <strong>${quran.surahNameEn||'—'}</strong><br>
        ${(quran.translation||'').substring(0,120)}<br>
        <em>— ${quran.surahNameEn||''} (${quran.surah||''}:${quran.ayah||''})</em>
        <br><br>
        <strong>Hadith:</strong> ${(hadith.english||hadith.text||'').replace(/\n/g,' ').replace(/\s+/g,' ').substring(0,100)}<br>
        <em>— ${hadith.bookName||''} (${hadith.idInBook||''})</em>
      </div>`;

    // Draw the wheel
    drawTransitWheel();

  } catch(e) {
    console.error('Home load error:', e);
  }
}

// ══════════ TRANSIT WHEEL ══════════
// Gold/brass MAPA ASTRAL-inspired SVG transit wheel
const ZODIAC = [
  {name:'Aries',sym:'♈',start:0},{name:'Taurus',sym:'♉',start:30},
  {name:'Gemini',sym:'♊',start:60},{name:'Cancer',sym:'♋',start:90},
  {name:'Leo',sym:'♌',start:120},{name:'Virgo',sym:'♍',start:150},
  {name:'Libra',sym:'♎',start:180},{name:'Scorpio',sym:'♏',start:210},
  {name:'Sagittarius',sym:'♐',start:240},{name:'Capricorn',sym:'♑',start:270},
  {name:'Aquarius',sym:'♒',start:300},{name:'Pisces',sym:'♓',start:330},
];
const PCOLORS = {Sun:'#ffd166',Moon:'#c0c0ff',Mercury:'#b0b0b0',Venus:'#ff9ec4',
  Mars:'#ff3b5c',Jupiter:'#ffa500',Saturn:'#d4b86a',Uranus:'#00cfff',Neptune:'#4b4bff',Pluto:'#a020f0',
  Chiron:'#77dd77',Lilith:'#cc44bb',Rahu:'#ff8844',Ketu:'#8844ff','Part of Fortune':'#88ddff','Part of Spirit':'#ffdd88'};
const ASPECT_STYLES = {Conjunction:{c:'#a855f7',d:''},Sextile:{c:'#4ade80',d:'5,3'},
  Square:{c:'#f87171',d:''},Trine:{c:'#60a5fa',d:''},Opposition:{c:'#f97316',d:'4,4'},
  Quincunx:{c:'#06b6d4',d:'3,2'}};
const PLANET_COLORS = { Sun:'#ffd166', Moon:'#c0c0ff', Mercury:'#b0b0b0', Venus:'#ff9ec4',
  Mars:'#ff3b5c', Jupiter:'#ffa500', Saturn:'#d4b86a', Uranus:'#00cfff', Neptune:'#4444ff', Pluto:'#a020f0' };
const PLANET_SYMBOLS = { Sun:'☉', Moon:'☽', Mercury:'☿', Venus:'♀', Mars:'♂',
  Jupiter:'♃', Saturn:'♄', Uranus:'♅', Neptune:'♆', Pluto:'♇' };
