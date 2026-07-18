async function loadDashasFull() {
  const dc = document.getElementById('dashas-content');
  try {
    const d = await loadJSON('/api/dasha');
    let html = `<div class="section-desc">Vimshottari Dasha is a 120-year planetary cycle based on the Moon's nakshatra at birth. Each planet rules a specific period.</div>
    <div class="dasha-current-box">
      <div class="current-maha"><span class="label">Current Mahadasha:</span> <strong>${d.current_dasha?.lord||'—'}</strong></div>
      <div class="current-bhukti"><span class="label">Current Bhukti:</span> <strong>${d.current_bhukti?.lord||'—'}</strong></div>
      <div class="birth-nak">Birth Nakshatra: ${d.birth_nakshatra||'—'} — lord ${d.birth_nakshatra_lord||'—'}</div>
    </div>
    <h3 class="section-title">Full Dasha Timeline</h3>`;
    for(const dash of (d.dashas||[])) {
      const active = dash.lord === d.current_dasha?.lord ? 'dasha-active' : '';
      html += `<div class="dasha-item ${active}">
        <span class="dasha-lord">${dash.lord}</span>
        <span class="dasha-years">${dash.years} yrs</span>
        <span class="dasha-dates">${dash.start.slice(0,10)} → ${dash.end.slice(0,10)}</span>
        <span class="dasha-type">${dash.type}</span>
      </div>`;
    }
    if(d.current_dasha?.bhuktis) {
      html += `<h3 class="section-title" style="margin-top:16px">Current Mahadasha: ${d.current_dasha.lord} — Bhuktis</h3>`;
      for(const b of (d.current_dasha.bhuktis||[])) {
        html += `<div class="dasha-item ${b.active?'dasha-active':''}">
          <span class="dasha-lord">${b.lord}</span>
          <span class="dasha-years">${b.years.toFixed(2)} yrs</span>
          <span class="dasha-dates">${b.start.slice(0,10)} → ${b.end.slice(0,10)}</span>
        </div>`;
      }
    }
    dc.innerHTML = html;
  } catch(e) { dc.innerHTML = `<div class="loading">${e.message}</div>`; }
}

async function loadNakshatrasFull() {
  const nc = document.getElementById('nakshatras-full-content');
  try {
    const d = await loadJSON('/api/nakshatra-now');
    const nd = await loadJSON('/static/nakshatra_data.json');
    let html = `<div class="section-desc">The 27 Nakshatras (lunar mansions) of Vedic astrology. Each spans 13°20' and is ruled by a planet.</div>
    <div class="current-nak-box">
      <strong>Current: ${d.name}</strong> (Pada ${d.pada}) — Lord ${d.lord} · ${d.gana||''} · ${d.guna||''}
      <div>${d.description||''}</div>
    </div>
    <h3 class="section-title">All 27 Nakshatras</h3><div class="nak-grid">`;
    for(const n of (nd.nakshatras||[])) {
      html += `<div class="nak-card ${n.name===d.name?'nak-active':''}">
        <div class="nak-card-name">${n.name}</div>
        <div class="nak-card-sans">${n.sanskrit||''}</div>
        <div class="nak-card-lord">${n.lord} (${n.dasha_years}yr)</div>
        <div class="nak-card-meaning">${n.meaning||''}</div>
      </div>`;
    }
    html += '</div>';
    nc.innerHTML = html;
  } catch(e) { nc.innerHTML = `<div class="loading">${e.message}</div>`; }
}

