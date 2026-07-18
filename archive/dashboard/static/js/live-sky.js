async function loadLive() {
  const lc = document.getElementById('live-content');
  lc.innerHTML = '<div class="loading">Loading live planetary data...</div>';
  try {
    const data = await loadJSON('/api/live');
    let html = '<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px"><div><h3 class="section-title">Planets Now</h3>';
    for(const [name, info] of Object.entries(data.planets||{})) {
      const col = PLANET_COLORS[name]||'#ffd166';
      const sym = PLANET_SYMBOLS[name]||'◉';
      html += `<div class="planet-row"><span class="sym" style="color:${col}">${sym}</span>
        <span class="name">${name}</span>
        <span class="pos">${info.sign||info.longitude||'—'}</span>
        <span style="font-size:11px;color:var(--text-muted)">${info.degree||''}</span>
      </div>`;
    }
    html += '</div><div><h3 class="section-title">Current Aspects</h3>';
    try {
      const aspects = await loadJSON('/api/aspects');
      for(const a of (aspects.aspects||[])) {
        html += `<div class="planet-row" style="gap:4px">
          <span style="color:${a.p1_color};font-size:16px">${a.p1_symbol}</span>
          <span>${a.aspect}</span>
          <span style="color:${a.p2_color};font-size:16px">${a.p2_symbol}</span>
          <span class="pos">orb ${a.orb}°</span>
        </div>`;
      }
    } catch(e) { html += '<div class="loading">No aspect data</div>'; }
    html += '</div></div>';
    lc.innerHTML = html;
  } catch(e) { lc.innerHTML = `<div class="loading">${e.message}</div>`; }
}


