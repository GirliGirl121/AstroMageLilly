// ══════════ OBSERVATORY DATA LOADER ══════════
async function loadObservatoryData() {
  try {
    const home = await loadJSON('/api/home');
    const live = await loadJSON('/api/live');

  // Top info bar
  const now = new Date();
  document.getElementById('obs-date').textContent = now.toLocaleDateString('en-GB',{weekday:'short',day:'numeric',month:'short',year:'numeric'});
  document.getElementById('obs-time').textContent = now.toLocaleTimeString('en-GB',{hour:'2-digit',minute:'2-digit',second:'2-digit'});
  document.getElementById('obs-tz').textContent = 'SAST (UTC+2)';
  document.getElementById('obs-location').textContent = 'Kariega, SA';
  document.getElementById('obs-jd').textContent = live.jd || '—';
  document.getElementById('obs-sidereal').textContent = live.sidereal || '—';

  // Transit planets list
  const planets = live.planets || {};
  const planetCount = Object.keys(planets).filter(n => n !== 'Sun' || true).length;
  document.getElementById('obs-planet-count').textContent = planetCount;
  const pList = document.getElementById('obs-planets-list');
  pList.innerHTML = '';
  const pOrder = ['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn','Uranus','Neptune','Pluto','Chiron','Lilith','Rahu','Ketu','Part of Fortune','Part of Spirit'];
  for(const nm of pOrder){
    const p = planets[nm]; if(!p) continue;
    const col = PCOLORS[nm] || '#fff';
    pList.innerHTML += `
      <div class="planet-row" onclick="showPlanetPanel('${nm}')">
        <span class="planet-glyph" style="color:${col}">${p.symbol}</span>
        <span class="planet-name">${nm}</span>
        <span class="planet-degree">${p.degree}</span>
        <span class="planet-motion direct">D</span>
      </div>`;
  }
  if(pList.innerHTML === '') pList.innerHTML = '<div class="obs-loading">No data</div>';

  // Aspects
  const aspD = await loadJSON('/api/aspects');
  const aspects = (aspD.aspects || []).filter(a => a.aspect !== 'Quincunx');
  document.getElementById('obs-aspect-count').textContent = aspects.length;
  const aList = document.getElementById('obs-aspects-list');
  aList.innerHTML = '';
  const aspSym = {Conjunction:'☌', Sextile:'✶', Square:'□', Trine:'△', Opposition:'☍', Quincunx:'⚹'};
  for(const a of aspects.slice(0, 12)){
    const cls = a.aspect === 'Applying' ? 'applying' : 'separating';
    const color = (ASPECT_STYLES[a.aspect]||{}).c || '#888';
    aList.innerHTML += `
      <div class="aspect-row">
        <span class="aspect-symbol" style="color:${color}">${aspSym[a.aspect]||'∠'}</span>
        <span class="aspect-planets">${a.p1} ${aspSym[a.aspect]} ${a.p2}</span>
        <span class="aspect-orb">${a.orb.toFixed(1)}°</span>
        <span class="${cls}">${a.applying ? 'app' : 'sep'}</span>
      </div>`;
  }
  if(aList.innerHTML === '') aList.innerHTML = '<div class="obs-loading">No major aspects</div>';

  // Elements
  const en = home.energy || {};
  const el = document.getElementById('obs-elements');
  const eb = en.elemental_balance || {};
  el.innerHTML = '';
  const elIcons = {Fire:'🔥', Earth:'🌍', Air:'🌬', Water:'💧'};
  for(const [name, count] of Object.entries(eb)){
    el.innerHTML += `<div class="element-item"><span class="element-icon">${elIcons[name]||'◉'}</span><span class="element-name">${name}</span><span class="element-count">${count}</span></div>`;
  }
  // Modalities
  const mods = en.modalities || {};
  if(Object.keys(mods).length > 0){
    el.innerHTML += '<div class="modalities-grid">';
    for(const [name, count] of Object.entries(mods)){
      el.innerHTML += `<div class="modality-item"><span class="modality-name">${name}</span><span class="modality-count">${count}</span></div>`;
    }
    el.innerHTML += '</div>';
  }

  // Quick info
  const ia = home.islamic_astro || {};
  const mp = ia.mansion || {};
  document.getElementById('obs-quick-info').innerHTML = `
    <div class="quick-info-row"><span class="quick-info-label">Moon Phase</span><span class="quick-info-value">${(ia.moon_phase||{}).emoji||'🌙'} ${(ia.moon_phase||{}).phase||'—'}</span></div>
    <div class="quick-info-row"><span class="quick-info-label">Lunar Mansion</span><span class="quick-info-value">${mp.picatrix_name||'—'}</span></div>
    <div class="quick-info-row"><span class="quick-info-label">Day Ruler</span><span class="quick-info-value">${ia.day_ruler||'—'}</span></div>
    <div class="quick-info-row"><span class="quick-info-label">Polarity</span><span class="quick-info-value">${(home.energy||{}).polarity||'—'}</span></div>
  `;

  // Bottom cards
  document.getElementById('obs-mansion').innerHTML = `<div style="font-size:11px;line-height:1.6"><strong>${mp.picatrix_name||'—'}</strong><br>${mp.arabic_name||''}<br><em>${mp.meaning||''}</em><br><br>Nature: ${mp.nature||'—'}<br>Ruler: ${mp.planetary_ruler||'—'}<br>Spirit: ${mp.spirit||'—'}</div>`;
  document.getElementById('obs-nakshatra').innerHTML = `<div style="font-size:11px;line-height:1.6">
        <strong>${(ia.nakshatra||{}).name||'—'}</strong> ${(ia.nakshatra||{}).sanskrit||''}<br>
        Pada ${(ia.nakshatra||{}).pada||'—'} · Lord: ${(ia.nakshatra||{}).lord||'—'} · ${(ia.nakshatra||{}).gana||'—'} · ${(ia.nakshatra||{}).guna||'—'}<br>
        ${(ia.nakshatra||{}).meaning||''}
        <br><br>
        ${(ia.dasha||{}).current_dasha? '<strong>Mahadasha:</strong> '+(ia.dasha||{}).current_dasha.lord||'—' : ''}
        ${(ia.dasha||{}).current_bhukti? ' · <strong>Bhukti:</strong> '+(ia.dasha||{}).current_bhukti.lord||'—' : ''}
      </div>`;
  document.getElementById('obs-tarot').innerHTML = `<div style="font-size:11px;line-height:1.6"><strong>${(home.tarot||{}).name||'—'}</strong><br>${(home.tarot||{}).keywords?.join(', ') || ''}<br><br><em>${(home.tarot||{}).daily_message||''}</em></div>`;
  document.getElementById('obs-quran').innerHTML = `<div style="font-size:11px;line-height:1.6"><strong>${(home.quran_hadith||{}).quran?.surahNameEn||'—'}</strong><br>${(home.quran_hadith||{}).quran?.translation?.substring(0,120)||''}...</div>`;

  // ── Lilly's Cosmic Weather Summary ──
  try {
    const summ = await loadJSON('/api/summary');
    const body = document.getElementById('cosmic-summary-body');
    if (body) {
      // Generate contextual summary from available data
      const mn = summ.moon_phase||'—';
      const ms = summ.moon_sign||'—';
      const me = summ.moon_emoji||'🌙';
      const nk = (summ.nakshatra||{}).name||'—';
      const dr = summ.day_ruler||'—';
      const md = summ.mahadasha||'—';
      const bh = summ.bhukti||'—';
      const ph = (summ.planetary_hour||{}).planet||'—';
      const sunS = summ.sun_sign||'—';
      const aspCount = (summ.aspects||[]).length;
      const retros = (summ.retrograde_planets||[]).join(', ');
      const summary = `The **${mn}** ${me} shines through **${ms}** as the Moon journeys through **${nk}** nakshatra. The Sun radiates from **${sunS}**, while today is ruled by **${dr}**. ${aspCount} aspects shape the sky — ${retros ? retros + ' retrograde' : 'offering clarity and momentum'}. Mahadasha: **${md}** · Bhukti: **${bh}** · Planetary Hour: **${ph}**`;
      body.innerHTML = summary.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>');
    }
  } catch(e) { console.error('Summary fetch error:', e); }

  } catch(e) { console.error('Observatory data error:', e); }
}

// Cosmic summary refresh button
document.addEventListener('click', (e) => {
