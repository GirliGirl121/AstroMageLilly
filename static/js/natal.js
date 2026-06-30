// Cosmic summary refresh button
document.addEventListener('click', (e) => {
 if (e.target.id === 'cs-refresh') {
 const body = document.getElementById('cosmic-summary-body');
 if (body) body.innerHTML = '<div class="obs-loading">Consulting the stars...</div>';
 fetch('/api/summary').then(r => r.json()).then(summ => {
 if (body) {
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
 }).catch(() => { if (body) body.innerHTML = '<div class="obs-loading">The stars are quiet...</div>'; });
 }
 });

// Initial load
loadObservatoryData();

// Embed wheel data directly in page
window.__WHEEL_DATA__ = null;
window.__WHEEL_ASPECTS__ = [];
fetch('/api/live').then(r => r.json()).then(d => { window.__WHEEL_DATA__ = d; drawTransitWheel(); });
fetch('/api/aspects').then(r => r.json()).then(d => { window.__WHEEL_ASPECTS__ = d.aspects || []; });

// ══════════ NATAL CHART LOADER ══════════
async function loadNatal(chartId) {
 const nc = document.getElementById('natal-worksheet');
 if (!nc) return;
 try {
 const body = chartId ? {chart_id: chartId} : {};
 const data = await loadJSON('/api/natal/chart', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)});

 currentNatalChartId = chartId || null;
 currentNatalData = data;

 // ── Birth Data ──
 document.getElementById('natal-name').textContent = data.name;
 document.getElementById('natal-date').textContent = data.birth_date;
 document.getElementById('natal-time').textContent = data.birth_time;
 document.getElementById('natal-location').textContent = data.location;
 document.getElementById('natal-asc').textContent = data.ascendant.sign+' '+data.ascendant.degree;
 document.getElementById('natal-mc').textContent = data.midheaven.sign+' '+data.midheaven.degree;

 // ── Planetary Positions Table ──
 const porder = ['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn',
 'Uranus','Neptune','Pluto','Chiron','Lilith','Rahu','Ketu','Part of Fortune'];

 // ── Use Placidus cusps from backend data ──
 const SIGN_NAMES = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'];
 const SIGN_SYM = ['♈','♉','♊','♋','♌','♍','♎','♏','♐','♑','♒','♓'];
 const SIGN_RULERS = {0:'Mars',1:'Venus',2:'Mercury',3:'Moon',4:'Sun',5:'Mercury',6:'Venus',7:'Mars',8:'Jupiter',9:'Saturn',10:'Saturn',11:'Jupiter'};

 // Extract Placidus cusps from backend data (houses object contains house_1 through house_12)
 const placidusCusps = [];
 for(let i = 1; i <= 12; i++) {
 const houseKey = `house_${i}`;
 const houseData = data.houses?.[houseKey];
 if(houseData) {
 placidusCusps.push({
 house: i,
 longitude: houseData.longitude,
 sign: houseData.sign,
 sign_symbol: houseData.symbol,
 degree: houseData.degree,
 ruler: SIGN_RULERS[Math.floor(houseData.longitude / 30) % 12]
 });
 } else {
 // Fallback to Equal House if Placidus data missing
 const cuspLon = (data.ascendant.longitude + (i-1) * 30) % 360;
 placidusCusps.push({
 house: i,
 longitude: cuspLon,
 sign: SIGN_NAMES[Math.floor(cuspLon / 30)],
 sign_symbol: SIGN_SYM[Math.floor(cuspLon / 30)],
 degree: (cuspLon % 30).toFixed(1).replace('.0','') + '°',
 ruler: SIGN_RULERS[Math.floor(cuspLon / 30)]
 });
 }
 }

 // Assign house via Placidus cusps
 function getHouse(lon) {
 for(let i = 0; i < 12; i++) {
 const c1 = placidusCusps[i].longitude;
 const c2 = placidusCusps[(i+1) % 12].longitude;
 const diff = (lon - c1 + 360) % 360;
 const span = (c2 - c1 + 360) % 360;
 if(diff < span) return i + 1;
 }
 return 1;
 }

 // ── Planetary Positions Table ──
 const ptbody = document.getElementById('natal-planet-tbody');
 ptbody.innerHTML = porder.map(n => {
 const p = data.planets[n];
 if(!p) return '';
 const sym = PLANET_SYMBOLS[n] || '&#9673;';
 const col = PLANET_COLORS[n] || '#fff';
 const houseNum = getHouse(p.longitude);
 return '<tr><td><span style="color:'+col+'">'+sym+'</span> '+n+'</td><td>'+p.sign_symbol+' '+p.sign+'</td><td>'+p.degree+'</td><td>'+houseNum+'</td></tr>';
 }).join('');

 // ── Aspect List ──
 const aspectDiv = document.getElementById('natal-aspect-list');
 const aspectSymbols = {'Conjunction':'&#x260C;','Opposition':'&#x260D;','Trine':'&#x25B3;','Square':'&#x25A1;','Sextile':'&#x2736;'};
 aspectDiv.innerHTML = data.aspects.map(function(a) {
 return '<div class="natal-aspect-row">'+
 '<span style="color:'+a.p1_color+'">'+a.p1_symbol+'</span> '+
 a.p1+' <span class="natal-aspect-sym">'+(aspectSymbols[a.aspect]||a.aspect)+'</span> '+
 a.p2+' <span style="color:'+a.p2_color+'">'+a.p2_symbol+'</span>'+
 ' <span class="natal-aspect-orb">('+a.orb+'&deg;)</span></div>';
 }).join('');

 // ── House Cusps Table (Placidus) ──
 const ctbody = document.getElementById('natal-cusp-tbody');
 ctbody.innerHTML = placidusCusps.map(function(c) {
 return '<tr><td>'+c.house+'</td><td>'+c.sign_symbol+' '+c.sign+'</td><td>'+c.degree+'</td><td>'+c.ruler+'</td></tr>';
 }).join('');

 // ── Elements & Modalities ──
 const etbody = document.getElementById('natal-elem-tbody');
 const elements = ['Fire','Earth','Air','Water'];
 const elemEmoji = {'Fire':'&#x1F525;','Earth':'&#x1F30D;','Air':'&#x1F32C;','Water':'&#x1F4A7;'};
 const elemModCounts = {};
 for(const n in data.planets) {
 const p = data.planets[n];
 if(!p.element) continue;
 const e = p.element.split(' ')[1] || p.element;
 const q = p.quality;
 if(!elemModCounts[e]) elemModCounts[e] = {'Cardinal':0,'Fixed':0,'Mutable':0};
 if(elemModCounts[e][q] !== undefined) elemModCounts[e][q]++;
 }
 etbody.innerHTML = elements.map(function(e) {
 return '<tr><td>'+(elemEmoji[e]||'&#x2726;')+' '+e.toUpperCase()+'</td>'+
 '<td>'+(elemModCounts[e]?.['Cardinal']||0)+'</td>'+
 '<td>'+(elemModCounts[e]?.['Fixed']||0)+'</td>'+
 '<td>'+(elemModCounts[e]?.['Mutable']||0)+'</td></tr>';
 }).join('');

 // ── NATAL WHEEL (SVG) ──
 drawNatalWheel(data);

 // Update the select to reflect the current chart
 const sel = document.getElementById('natal-chart-select');
 if(sel) {
 for(let o of sel.options) {
 o.selected = o.value === String(chartId || '');
 }
 }

 } catch(e) {
 nc.innerHTML = '<div class="natal-error">Failed to load natal chart: '+e.message+'</div>';
 }
}

function drawNatalWheel(data) {
 const container = document.getElementById('natal-wheel-canvas');
 if(!container) return;

 const size = 480, cx = size/2, cy = size/2;
 const rOuter = 220, rInner = 160, rPlanet = 185, rLabel = 145, rAspect = rInner - 10;

 // AstroChart coordinate system: SHIFT_IN_DEGREES = 180
 // angleInRad = (180 - angle) * PI/180
 // x = cx + r * cos(angleInRad), y = cy + r * sin(angleInRad)
 // 0° = 9o'clock(ASC), 90° = 6o'clock(IC), 180° = 3o'clock(DSC), 270° = 12o'clock(MC)
 const SHIFT = 180;
 function pos(angle, r) {
 const rad = (SHIFT - angle) * Math.PI / 180;
 return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
 }

 // ── Use Placidus cusps from backend data for wheel display ──
 const ascLon = data.ascendant.longitude;
 
 // Extract Placidus cusps from backend data (houses object contains house_1 through house_12)
 const SIGN_SYMBOLS = ['♈','♉','♊','♋','♌','♍','♎','♏','♐','♑','♒','♓'];
 const placidusCusps = [];
 for(let i = 1; i <= 12; i++) {
 const houseKey = `house_${i}`;
 const houseData = data.houses?.[houseKey];
 if(houseData && houseData.longitude !== undefined) {
 placidusCusps.push(houseData.longitude);
 } else {
 // Fallback to Equal House if Placidus data missing
 placidusCusps.push((ascLon + (i-1) * 30) % 360);
 }
 }

 // shift: rotate chart so ASC lands at 0° (9 o'clock)
 const shift = (360 - ascLon) % 360;
 function screenAngle(lon) { return ((lon + shift) % 360 + 360) % 360; }

 let svg = `<svg viewBox="0 0 ${size} ${size}" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;display:block">
 <rect width="${size}" height="${size}" fill="#0a0a14"/>
 <circle cx="${cx}" cy="${cy}" r="${rOuter+10}" fill="none" stroke="#d4af37" stroke-width="2"/>
 <circle cx="${cx}" cy="${cy}" r="${rOuter}" fill="none" stroke="#d4af37" stroke-width="0.5" opacity="0.3"/>
 <circle cx="${cx}" cy="${cy}" r="${rInner}" fill="none" stroke="#d4af37" stroke-width="0.5" opacity="0.2"/>
 <circle cx="${cx}" cy="${cy}" r="30" fill="none" stroke="#d4af37" stroke-width="0.5" opacity="0.2"/>`;

 // ── Aspect lines (inside the wheel, drawn first so planets sit on top) ──
 const ASPECT_COLORS = {'Conjunction':'#a855f7','Opposition':'#f97316','Trine':'#60a5fa','Square':'#f87171','Sextile':'#4ade80'};
 if(data.aspects) {
 for(const a of data.aspects) {
 if(a.orb > 6) continue;
 const p1lon = data.planets[a.p1]?.longitude;
 const p2lon = data.planets[a.p2]?.longitude;
 if(p1lon === undefined || p2lon === undefined) continue;
 const p1 = pos(screenAngle(p1lon), rAspect);
 const p2 = pos(screenAngle(p2lon), rAspect);
 const col = ASPECT_COLORS[a.aspect] || '#888';
 const sw = a.orb <= 2 ? 1.2 : a.orb <= 4 ? 0.8 : 0.5;
 const op = a.orb <= 2 ? 0.7 : a.orb <= 4 ? 0.5 : 0.3;
 svg += `<line x1="${p1.x.toFixed(1)}" y1="${p1.y.toFixed(1)}" x2="${p2.x.toFixed(1)}" y2="${p2.y.toFixed(1)}" stroke="${col}" stroke-width="${sw}" opacity="${op}"/>`;
 }
 }

 // ── 12 house sectors (Placidus) ──
 for(let i=0; i<12; i++) {
 const cusp = placidusCusps[i];
 const nextCusp = placidusCusps[(i+1)%12];
 const sa = screenAngle(cusp);
 const ea = screenAngle(nextCusp);
 const sRad = (SHIFT - sa) * Math.PI/180;
 const eRad = (SHIFT - ea) * Math.PI/180;
 const x1 = cx + rOuter * Math.cos(sRad), y1 = cy + rOuter * Math.sin(sRad);
 const x2 = cx + rOuter * Math.cos(eRad), y2 = cy + rOuter * Math.sin(eRad);
 const xi1 = cx + rInner * Math.cos(sRad), yi1 = cy + rInner * Math.sin(sRad);
 const xi2 = cx + rInner * Math.cos(eRad), yi2 = cy + rInner * Math.sin(eRad);
 const arcDiff = ((ea - sa) + 360) % 360;
 const largeArc = arcDiff > 180 ? 1 : 0;
 svg += `<path d="M ${xi1.toFixed(1)} ${yi1.toFixed(1)} L ${x1.toFixed(1)} ${y1.toFixed(1)} A ${rOuter} ${rOuter} 0 ${largeArc} 1 ${x2.toFixed(1)} ${y2.toFixed(1)} L ${xi2.toFixed(1)} ${yi2.toFixed(1)} A ${rInner} ${rInner} 0 ${largeArc} 0 ${xi1.toFixed(1)} ${yi1.toFixed(1)} Z" fill="none" stroke="#d4af37" stroke-width="0.5" opacity="0.25"/>`;

 // House number at midpoint
 const midMid = (sa + arcDiff/2) % 360;
 const midRad = (SHIFT - midMid) * Math.PI/180;
 const mr = (rOuter + rInner) / 2;
 const mx = cx + mr * Math.cos(midRad);
 const my = cy + mr * Math.sin(midRad);
 svg += `<text x="${mx.toFixed(1)}" y="${my.toFixed(1)}" text-anchor="middle" dominant-baseline="central" fill="#d4af37" font-size="10" opacity="0.5">${i+1}</text>`;

 // Sign glyph at label radius (15° into the sign from this cusp)
 const signAngle = sa + 15;
 const signRad = (SHIFT - signAngle) * Math.PI/180;
 const lx = cx + rLabel * Math.cos(signRad);
 const ly = cy + rLabel * Math.sin(signRad);
 const signIdx = Math.floor(cusp / 30) % 12;
 svg += `<text x="${lx.toFixed(1)}" y="${ly.toFixed(1)}" text-anchor="middle" dominant-baseline="central" fill="#a090b0" font-size="16" font-family="serif">${SIGN_SYMBOLS[signIdx]}</text>`;
 }

 // ── Angle lines ──
 // ASC/DSC: horizontal line through center (ASC left at 9o'clock, DSC right at 3o'clock)
 const ascPos = pos(0, rOuter + 5);
 const dscPos = pos(180, rOuter + 5);
 svg += `<line x1="${dscPos.x.toFixed(1)}" y1="${dscPos.y.toFixed(1)}" x2="${ascPos.x.toFixed(1)}" y2="${ascPos.y.toFixed(1)}" stroke="#ffffff" stroke-width="2" opacity="0.9"/>`;
 // ASC label
 const al = pos(0, rOuter + 18);
 svg += `<text x="${al.x.toFixed(1)}" y="${al.y.toFixed(1)}" text-anchor="middle" dominant-baseline="central" fill="#ffffff" font-size="10" font-weight="bold" transform="rotate(-90, ${al.x.toFixed(1)}, ${al.y.toFixed(1)})">${data.ascendant.degree} ${data.ascendant.sign_symbol} ${data.ascendant.sign}</text>`;
 // DSC label
 const dl = pos(180, rOuter + 18);
 svg += `<text x="${dl.x.toFixed(1)}" y="${dl.y.toFixed(1)}" text-anchor="middle" dominant-baseline="central" fill="#ffffff" font-size="8" opacity="0.7">DSC</text>`;

 // MC/IC: MC at 270° (12 o'clock), IC at 90° (6 o'clock)
 const mcPos = pos(270, rOuter + 5);
 const icPos = pos(90, rOuter + 5);
 svg += `<line x1="${icPos.x.toFixed(1)}" y1="${icPos.y.toFixed(1)}" x2="${mcPos.x.toFixed(1)}" y2="${mcPos.y.toFixed(1)}" stroke="#44aaff" stroke-width="1.2" opacity="0.5" stroke-dasharray="5,3"/>`;
 // MC label
 const ml = pos(270, rOuter + 18);
 svg += `<text x="${ml.x.toFixed(1)}" y="${ml.y.toFixed(1)}" text-anchor="middle" fill="#44aaff" font-size="8" font-weight="bold">MC ${data.midheaven.sign_symbol}</text>`;
 // IC label
 const il = pos(90, rOuter + 18);
 svg += `<text x="${il.x.toFixed(1)}" y="${il.y.toFixed(1)}" text-anchor="middle" fill="#44aaff" font-size="8" opacity="0.6">IC</text>`;

 // ── Planets on wheel ──
 const porder = ['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn',
 'Uranus','Neptune','Pluto','Chiron','Lilith','Rahu','Ketu','Part of Fortune'];
 for(const n of porder) {
 const p = data.planets[n];
 if(!p || p.longitude === undefined) continue;
 const pp = pos(screenAngle(p.longitude), rPlanet);
 const sym = PLANET_SYMBOLS[n] || '◉';
 const col = PLANET_COLORS[n] || '#fff';
 svg += `<text x="${pp.x.toFixed(1)}" y="${pp.y.toFixed(1)}" text-anchor="middle" dominant-baseline="central" fill="${col}" font-size="14">${sym}</text>`;
 // Label for outer points — name + degree
 if(['Uranus','Neptune','Pluto','Chiron','Lilith','Ketu','Part of Fortune'].includes(n)) {
 svg += `<text x="${pp.x.toFixed(1)}" y="${(pp.y+14).toFixed(1)}" text-anchor="middle" fill="${col}" font-size="6" opacity="0.8">${n} ${p.degree}</text>`;
 }
 }

 // Center text
 svg += `<text x="${cx}" y="${cy-5}" text-anchor="middle" fill="#d4af37" font-size="13" font-weight="bold">${data.name}</text>
 <text x="${cx}" y="${cy+12}" text-anchor="middle" fill="#a090b0" font-size="9">${data.birth_date}</text>
 </svg>`;

 container.innerHTML = svg;
}

// ══════════ SimplyAstrology Loader ══════════
async function loadSimply() {
 const sc = document.getElementById('simply-content');
 const nav = document.getElementById('simply-nav-list');
 try {
 const data = await loadJSON('/api/simply/all');
 // Build navigation
 let navHtml = '';
 data.forEach((sec, i) => {
 const icon = ['♈','♇','℞','∠','♔','📋','🔄','✨','📜','🕌'][i] || '✦';
 navHtml += `<div class="simply-nav-item" data-idx="${i}" onclick="simplySelect(${i})">
 <span class="simply-nav-icon">${icon}</span>
 <span class="simply-nav-name">${sec.section}</span>
 <span class="simply-nav-count">${sec.cards.length}</span>
 </div>`;
 });
 nav.innerHTML = navHtml;

 // Render all sections hidden initially
 let contentHtml = '';
 data.forEach((sec, i) => {
 contentHtml += `<div class="simply-section" id="simply-sec-${i}">`;
 contentHtml += `<div class="simply-section-title">${sec.section}</div>`;
 sec.cards.forEach((card, j) => {
 contentHtml += `<div class="simply-card" onclick="simplyToggleCard(this)">
 <div class="simply-card-header">
 <span class="simply-card-arrow">▶</span>
 <span class="simply-card-heading">${esc(card.heading)}</span>
 </div>
 <div class="simply-card-body">${card.body.replace(/\n/g, '<br>')}</div>
 </div>`;
 });
 contentHtml += `</div>`;
 });
 sc.innerHTML = contentHtml;

 // Auto-select first section
 simplySelect(0);
