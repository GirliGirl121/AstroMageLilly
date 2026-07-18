
// ══════════ PREMIUM TRANSIT WHEEL — Solar Fire / AstroGold Inspired ══════════
const WHEEL = {
  scale: 1,
  hoverPlanet: null,
  showQuincunx: false,
};

function _lon2xy(lon, r, cx, cy) {
  const a = ((180 - lon) % 360 + 360) % 360 * Math.PI / 180;
  return { x: cx + r * Math.cos(a), y: cy + r * Math.sin(a) };
}

function _textAnchor(x, y, cx, cy) {
  const dx = x - cx, dy = y - cy;
  if(Math.abs(dx) > Math.abs(dy)) return dx > 0 ? 'start' : 'end';
  return dy > 0 ? 'middle' : 'middle';
}

async function drawTransitWheel() {
  const el = document.getElementById('wheel-canvas');
  if(!el) return;
  // Use embedded data if available, otherwise fetch
  let live = window.__WHEEL_DATA__;
  if(!live) {
    try { live = await loadJSON('/api/live'); } catch(e) { return; }
  }
  const aspD = window.__WHEEL_ASPECTS__ && window.__WHEEL_ASPECTS__.length ? {aspects: window.__WHEEL_ASPECTS__} : await loadJSON('/api/aspects').catch(() => ({aspects:[]}));
  const planets = live.planets || {};
  const aspects = aspD.aspects || [];
  const ascLon = live.ascendant;
  const cusps = live.cusps || [];

    // SVG dimensions (large for desktop)
    const S = 680, CX = S/2, CY = S/2;
    const OR = 300, signR = OR - 38, cuspR = 250, houseNumR = 232, planetR = 210, innerR = 140;

    function lon2xy(lon, r) { const a = ((180-lon)%360+360)%360*Math.PI/180; return {x:CX+r*Math.cos(a), y:CY+r*Math.sin(a)}; }

    let svg = `<svg viewBox="0 0 ${S} ${S}" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;display:block">`;
    svg += `<defs>`;
    svg += `<radialGradient id="wg-bg"><stop offset="0%" stop-color="#1a0e2e"/><stop offset="70%" stop-color="#0d0618"/><stop offset="100%" stop-color="#050408"/></radialGradient>`;
    svg += `<radialGradient id="wg-center"><stop offset="0%" stop-color="rgba(212,175,55,0.06)"/><stop offset="100%" stop-color="transparent"/></radialGradient>`;
    svg += `</defs>`;
    svg += `<rect width="${S}" height="${S}" fill="url(#wg-bg)"/>`;

    // Stars
    for(let i=0;i<80;i++){ const op=(Math.sin(i*17.3)*0.5+0.5)*0.25+0.05; svg+=`<circle cx="${(i*43)%S}" cy="${(i*61)%S}" r="${(i%3)*0.4+0.3}" fill="rgba(255,255,255,${op})"/>`; }
    svg += `<circle cx="${CX}" cy="${CY}" r="${OR+30}" fill="url(#wg-center)"/>`;

    // Rings
    svg += `<circle cx="${CX}" cy="${CY}" r="${OR}" class="wheel-ring" stroke-width="1.5"/>`;
    svg += `<circle cx="${CX}" cy="${CY}" r="${cuspR}" class="wheel-ring-inner" stroke-width="0.5"/>`;
    svg += `<circle cx="${CX}" cy="${CY}" r="${planetR}" class="wheel-ring-inner" stroke-width="0.4"/>`;
    svg += `<circle cx="${CX}" cy="${CY}" r="${innerR}" class="wheel-ring-inner" stroke-width="0.3"/>`;

    // Zodiac signs
    const signWords = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'];
    const signSyms = ['♈','♉','♊','♋','♌','♍','♎','♏','♐','♑','♒','♓'];
    for(let i=0;i<12;i++){
      const cusp = cusps[i] != null ? cusps[i] : (ascLon + i*30) % 360;
      const next = cusps[(i+1)%12] != null ? cusps[(i+1)%12] : (ascLon + (i+1)*30) % 360;
      const a1 = ((180-cusp)%360+360)%360*Math.PI/180;
      const span = ((next-cusp)+360)%360;
      svg += `<line x1="${CX+(OR-38)*Math.cos(a1)}" y1="${CY+(OR-38)*Math.sin(a1)}" x2="${CX+OR*Math.cos(a1)}" y2="${CY+OR*Math.sin(a1)}" class="wheel-cusp-line"/>`;
      for(let d=0; d<span; d+=5){
        const degLon=(cusp+d)%360, da=((180-degLon)%360+360)%360*Math.PI/180, tl=d%10===0?8:4;
        svg += `<line x1="${CX+(OR-14)*Math.cos(da)}" y1="${CY+(OR-14)*Math.sin(da)}" x2="${CX+(OR-14+tl)*Math.cos(da)}" y2="${CY+(OR-14+tl)*Math.sin(da)}" stroke="rgba(212,175,55,0.3)" stroke-width="${d%10===0?0.8:0.4}"/>`;
      }
      const midAng=((180-(cusp+span/2))%360+360)%360*Math.PI/180;
      svg += `<text x="${CX+signR*Math.cos(midAng)}" y="${CY+signR*Math.sin(midAng)}" text-anchor="middle" dominant-baseline="central" font-size="22" class="wheel-sign-label">${signSyms[i]}</text>`;
      svg += `<text x="${CX+(OR-10)*Math.cos(midAng)}" y="${CY+(OR-10)*Math.sin(midAng)}" text-anchor="middle" dominant-baseline="central" font-size="8" fill="rgba(212,175,55,0.65)" font-family="Playfair Display,Georgia,serif">${signWords[i]}</text>`;
    }

    // House cusps + numbers
    for(let i=0;i<12;i++){
      const cusp=cusps[i]!=null?cusps[i]:(ascLon+i*30)%360;
      const a=((180-cusp)%360+360)%360*Math.PI/180;
      svg += `<line x1="${CX+innerR*Math.cos(a)}" y1="${CY+innerR*Math.sin(a)}" x2="${CX+cuspR*Math.cos(a)}" y2="${CY+cuspR*Math.sin(a)}" class="wheel-house-line"/>`;
      svg += `<text x="${CX+houseNumR*Math.cos(a)}" y="${CY+houseNumR*Math.sin(a)}" text-anchor="middle" dominant-baseline="central" font-size="11" class="wheel-house-num">${i+1}</text>`;
    }

    // Angle lines
    if(ascLon != null){
      const ascA=((180-ascLon)%360+360)%360*Math.PI/180;
      svg += `<line x1="${CX+(innerR+5)*Math.cos(ascA)}" y1="${CY+(innerR+5)*Math.sin(ascA)}" x2="${CX+OR*Math.cos(ascA)}" y2="${CY+OR*Math.sin(ascA)}" class="wheel-asc-line"/>`;
      svg += `<text x="${CX+(OR+16)*Math.cos(ascA)}" y="${CY+(OR+16)*Math.sin(ascA)}" text-anchor="middle" dominant-baseline="central" fill="#ff4444" font-size="8" font-weight="bold">ASC</text>`;
      const dcA=((180-(ascLon+180)%360)%360+360)%360*Math.PI/180;
      svg += `<line x1="${CX+innerR*Math.cos(dcA)}" y1="${CY+innerR*Math.sin(dcA)}" x2="${CX+(OR-30)*Math.cos(dcA)}" y2="${CY+(OR-30)*Math.sin(dcA)}" class="wheel-dc-line"/>`;
      svg += `<text x="${CX+(OR+16)*Math.cos(dcA)}" y="${CY+(OR+16)*Math.sin(dcA)}" text-anchor="middle" dominant-baseline="central" fill="#ff6666" font-size="7" font-weight="bold">DC</text>`;
      if(cusps[9]!=null){const mcA=((180-cusps[9])%360+360)%360*Math.PI/180;svg+=`<line x1="${CX+(innerR+5)*Math.cos(mcA)}" y1="${CY+(innerR+5)*Math.sin(mcA)}" x2="${CX+OR*Math.cos(mcA)}" y2="${CY+OR*Math.sin(mcA)}" class="wheel-mc-line"/>`;svg+=`<text x="${CX+(OR+16)*Math.cos(mcA)}" y="${CY+(OR+16)*Math.sin(mcA)}" text-anchor="middle" dominant-baseline="central" fill="#d4af37" font-size="8" font-weight="bold">MC</text>`;}
      if(cusps[3]!=null){const icA=((180-cusps[3])%360+360)%360*Math.PI/180;svg+=`<line x1="${CX+innerR*Math.cos(icA)}" y1="${CY+innerR*Math.sin(icA)}" x2="${CX+(OR-30)*Math.cos(icA)}" y2="${CY+(OR-30)*Math.sin(icA)}" class="wheel-ic-line"/>`;svg+=`<text x="${CX+(OR+16)*Math.cos(icA)}" y="${CY+(OR+16)*Math.sin(icA)}" text-anchor="middle" dominant-baseline="central" fill="#d4af37" font-size="7" font-weight="bold">IC</text>`;}
    }

    // Aspect lines
    for(const a of aspects){
      if(!WHEEL.showQuincunx && a.aspect==='Quincunx') continue;
      const p1=planets[a.p1], p2=planets[a.p2]; if(!p1||!p2) continue;
      const p=lon2xy(p1.longitude,planetR), q=lon2xy(p2.longitude,planetR);
      const st=ASPECT_STYLES[a.aspect]||{c:'#888',d:''};
      const op=Math.max(0.15,0.5-(a.orb||0)*0.05);
      svg+=`<line x1="${p.x}" y1="${p.y}" x2="${q.x}" y2="${q.y}" stroke="${st.c}" stroke-width="0.8" stroke-dasharray="${st.d}" opacity="${op}" class="wheel-aspect-line ${a.aspect.toLowerCase()}"/>`;
    }

    // Planets with collision avoidance
    const order=['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn','Uranus','Neptune','Pluto','Chiron','Lilith','Rahu','Ketu','Part of Fortune','Part of Spirit'];
    const placed=[];
    for(const nm of order){
      const p=planets[nm]; if(!p) continue;
      let pos=lon2xy(p.longitude,planetR);
      for(const pp of placed){const dx=pos.x-pp.x,dy=pos.y-pp.y;if(Math.sqrt(dx*dx+dy*dy)<22){pos=lon2xy(p.longitude,planetR+18);break;}}
      placed.push(pos);
      const pc=PCOLORS[nm]||'#fff';
      svg+=`<circle cx="${pos.x}" cy="${pos.y}" r="14" fill="${pc}" class="wheel-planet-glow"/>`;
      svg+=`<text x="${pos.x}" y="${pos.y}" text-anchor="middle" dominant-baseline="central" fill="${pc}" font-size="19" data-planet="${nm}" class="wheel-planet-text" onmouseenter="highlightPlanet('${nm}')" onmouseleave="clearHighlight()">${p.symbol}</text>`;
      svg+=`<text x="${pos.x+(pos.x>CX?18:-18)}" y="${pos.y+10}" text-anchor="${pos.x>CX?'start':'end'}" font-size="8" fill="rgba(255,255,255,0.55)" font-family="Courier New,monospace">${p.degree}</text>`;
    }

    // Center hub
    const now=new Date();
    const ds=now.toLocaleDateString('en-GB',{day:'numeric',month:'short',year:'numeric'});
    const hh=String(now.getHours()).padStart(2,'0'), mm=String(now.getMinutes()).padStart(2,'0'), ss=String(now.getSeconds()).padStart(2,'0');
    svg+=`<circle cx="${CX}" cy="${CY}" r="40" fill="rgba(212,175,55,0.03)" class="wheel-center-pulse"/>`;
    svg+=`<text x="${CX}" y="${CY-14}" text-anchor="middle" class="wheel-center-text" font-size="11">${ds}</text>`;
    svg+=`<text x="${CX}" y="${CY+2}" text-anchor="middle" fill="#d4af37" font-size="20" font-family="monospace" font-weight="bold" opacity="0.9">${hh}:${mm}:${ss}</text>`;
    svg+=`<text x="${CX}" y="${CY+20}" text-anchor="middle" class="wheel-center-text" font-size="9">NOW</text>`;
    svg+=`</svg>`;
    el.innerHTML=svg;

    el.onwheel=(e)=>{e.preventDefault();WHEEL.scale=Math.max(0.5,Math.min(2,WHEEL.scale+(e.deltaY>0?-0.05:0.05)));el.style.transform=`scale(${WHEEL.scale})`;};
}

// Planet highlight on hover
function highlightPlanet(nm) {
  const texts = document.querySelectorAll(`#wheel-canvas .wheel-planet-text`);
  texts.forEach(t => {
    if(t.dataset.planet === nm) {
      t.style.filter = 'drop-shadow(0 0 6px gold)';
      t.style.fontSize = '24px';
    } else {
      t.style.opacity = '0.3';
    }
  });
}
function clearHighlight() {
  const texts = document.querySelectorAll(`#wheel-canvas .wheel-planet-text`);
  texts.forEach(t => {
    t.style.filter = '';
    t.style.fontSize = '19px';
    t.style.opacity = '';
  });
}

// Planet panel click
document.addEventListener('click', async (e) => {
  const pt = e.target.closest('.wheel-planet-text');
  if(!pt) return;
  const nm = pt.dataset.planet;
  if(!nm) return;
  const live = await loadJSON('/api/live');
  const p = live.planets[nm];
  if(!p) return;
  const panel = document.getElementById('planet-panel');
  const title = document.getElementById('planet-panel-title');
  const body = document.getElementById('planet-panel-body');
  title.textContent = `✦ ${nm} ${p.symbol}`;
  const col = PCOLORS[nm] || '#fff';
  body.innerHTML = `
    <div class="pp-row"><span class="pp-label">Longitude</span><span class="pp-value">${p.longitude}°</span></div>
    <div class="pp-row"><span class="pp-label">Sign</span><span class="pp-value">${p.sign_symbol} ${p.sign}</span></div>
    <div class="pp-row"><span class="pp-label">Degree</span><span class="pp-value">${p.degree}</span></div>
    <div class="pp-row"><span class="pp-label">House</span><span class="pp-value">${p.house || '—'}</span></div>
    <div class="pp-row"><span class="pp-label">Motion</span><span class="pp-value" style="color:var(--cyan)">Direct</span></div>
    <div class="pp-row" style="margin-top:8px;padding-top:8px;border-top:1px solid rgba(212,175,55,0.15)">
      <span class="pp-label" style="color:${col}">☽ Element</span>
      <span class="pp-value">${p.element || '—'}</span>
    </div>
    <div class="pp-row"><span class="pp-label" style="color:${col}">✦ Quality</span><span class="pp-value">${p.quality || '—'}</span></div>
  `;
  panel.classList.remove('hidden');
});
document.addEventListener('click', (e) => {
  if(e.target.id === 'planet-panel-close') {
    document.getElementById('planet-panel').classList.add('hidden');
  }
});

// Auto-refresh wheel + sidebar cards + info bar every 60 seconds
if(!window._wheelRefreshTimer){
  window._wheelRefreshTimer = setInterval(async () => {
    drawTransitWheel();
    loadObservatoryData();
  }, 60000);
}

