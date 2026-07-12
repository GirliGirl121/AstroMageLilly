/* ═══════════════════════════════════════════════════════════════════════════
   LILLY · CORE — homepage live loop, hero tiles, recent-conversation rendering.
   openTab, lillyAsk, sendChat, LILLY_AVATAR, lillyLoadRecent/SaveRecent, esc,
   loadJSON are defined in the inline script (templates/index.html).
   ═══════════════════════════════════════════════════════════════════════════ */

// ─── Utilities ───────────────────────────────────────────────────────────────
function setHTML(id, html){ const el=document.getElementById(id); if(el) el.innerHTML=html; }
function setTxt(id, txt){ const el=document.getElementById(id); if(el) el.textContent=txt; }

// Planet detail panel (opened from chart rows / wheel)
let _liveCacheForPanel = null;
async function showPlanetPanel(name){
  const panel = document.getElementById('planet-panel');
  const title = document.getElementById('planet-panel-title');
  const body  = document.getElementById('planet-panel-body');
  if(!panel || !body) return;
  if(!_liveCacheForPanel){
    try { _liveCacheForPanel = await loadJSON('/api/live'); } catch(e){ _liveCacheForPanel = {}; }
  }
  const p = (_liveCacheForPanel.planets||{})[name] || {};
  if(title) title.textContent = `${p.symbol||''} ${name}`;
  const s = _sgn(p.longitude);
  body.innerHTML = `
    <div class="pp-line"><span>Sign</span><b>${s.sym} ${esc(p.sign||'—')}</b></div>
    <div class="pp-line"><span>Degree</span><b>${esc(p.degree||'—')}</b></div>
    <div class="pp-line"><span>House</span><b>${p.house!=null?p.house:'—'}</b></div>
    <div class="pp-line"><span>Element</span><b>${esc((p.element||'').replace(/^[^\s]+\s/,'')||'—')}</b></div>
    <div class="pp-line"><span>Quality</span><b>${esc(p.quality||'—')}</b></div>
    <div class="pp-line"><span>Motion</span><b>${p.retrograde?'Retrograde':'Direct'}</b></div>`;
  panel.classList.remove('hidden');
}
function closePlanetPanel(){
  const panel = document.getElementById('planet-panel');
  if(panel) panel.classList.add('hidden');
}

function degToDMS(lon) {
  const deg = ((lon % 360) + 360) % 360;
  const d = Math.floor(deg);
  const mFloat = (deg - d) * 60;
  const m = Math.floor(mFloat);
  const s = Math.round((mFloat - m) * 60);
  return `${d}°${String(m).padStart(2,'0')}′${String(s).padStart(2,'0')}″`;
}
function signOf(lon) {
  const SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'];
  const SYM = ['♈','♉','♊','♋','♌','♍','♎','♏','♐','♑','♒','♓'];
  const i = Math.floor(((lon%360)+360)%360 / 30);
  return { name: SIGNS[i], sym: SYM[i] };
}

// ─── Recent conversation (persisted in localStorage by the inline script) ─────
function lillyRenderRecent() {
  const box = document.getElementById('lilly-recent-list');
  if (!box) return;
  const list = lillyLoadRecent();
  if (!list.length) {
    box.innerHTML = '<div class="lilly-recent-empty">Lilly is waiting… Ask her anything about the stars. ✨</div>';
    return;
  }
  box.innerHTML = list.map(m => {
    if (m.role === 'user') {
      return `<div class="lilly-msg user"><div class="lm-bubble">${esc(m.text)}</div></div>`;
    }
    return `<div class="lilly-msg"><div class="lm-avatar"><img src="${LILLY_AVATAR}" alt="Lilly"></div><div class="lm-bubble">${m.text}</div></div>`;
  }).join('');
  box.scrollTop = box.scrollHeight;
}

// ─── LIVE astronomy: per-second dashboard update ─────────────────────────────
let _lillyLiveTimer = null;
let _lillyWheelTimer = null;

async function lillyTick() {
  // Clock
  const now = new Date();
  const hh = String(now.getHours()).padStart(2,'0');
  const mm = String(now.getMinutes()).padStart(2,'0');
  const ss = String(now.getSeconds()).padStart(2,'0');
  const clock = document.getElementById('tile-clock-val');
  if (clock) clock.textContent = `${hh}:${mm}:${ss}`;

  // Fetch live sky (cheap, cached by browser)
  let live;
  try { live = await loadJSON('/api/live'); } catch (e) { return; }
  const planets = live.planets || {};

  // Moon tile
  const moon = planets['Moon'];
  const mp = live.moon_phase || {};
  const moonVal = document.getElementById('tile-moon-val');
  const moonSub = document.getElementById('tile-moon-sub');
  if (moonVal && moon) {
    const s = signOf(moon.longitude);
    moonVal.textContent = `${s.sym} ${s.name}`;
    moonSub.textContent = `${mp.emoji||'🌙'} ${mp.phase||''} · ${moon.degree||degToDMS(moon.longitude)}`;
  }

  // Planetary hour tile
  const ph = live.planetary_hour || {};
  const hourVal = document.getElementById('tile-hour-val');
  const hourSub = document.getElementById('tile-hour-sub');
  if (hourVal) {
    hourVal.textContent = ph.planet ? `${ph.planet}` : '—';
    hourSub.textContent = ph.spirit_name ? `Spirit: ${ph.spirit_name}` : `Hour ${ph.hour_number||''} · ${ph.period||''}`;
  }

  // ASC / MC tile
  const asc = live.ascendant, mc = live.midheaven;
  const ascVal = document.getElementById('tile-asc-val');
  const ascSub = document.getElementById('tile-asc-sub');
  if (ascVal && asc != null) {
    const s = signOf(asc);
    ascVal.textContent = `${s.sym} ${s.name}`;
    ascSub.textContent = mc != null ? `MC ${signOf(mc).sym} ${signOf(mc).name}` : 'MC —';
  }

  // Current transit tile (strongest major aspect right now)
  const aspects = live.aspects || [];
  const trVal = document.getElementById('tile-transit-val');
  const trSub = document.getElementById('tile-transit-sub');
  if (trVal) {
    if (aspects.length) {
      const a = aspects[0];
      trVal.textContent = `${a.p1} ${a.symbol} ${a.p2}`;
      trSub.textContent = `${a.aspect} · orb ${a.orb}°`;
    } else {
      trVal.textContent = 'No major aspect';
      trSub.textContent = 'Planets at ease';
    }
  }

  // Today's energy (from /api/energy if available, else derive)
  const enVal = document.getElementById('tile-energy-val');
  const enSub = document.getElementById('tile-energy-sub');
  if (enVal) {
    if (aspects.length) {
      enVal.textContent = aspects[0].aspect;
      enSub.textContent = `${aspects.length} active aspects`;
    } else {
      enVal.textContent = 'Flowing';
      enSub.textContent = 'Calm sky';
    }
  }
}

// Redraw the live wheel from /api/live (uses the existing renderer)
async function lillyDrawWheel() {
  if (typeof drawTransitWheel === 'function') {
    try { await drawTransitWheel(); } catch (e) {}
  }
}

function startLillyLive() {
  if (_lillyLiveTimer) return;            // guard against double-start
  lillyTick();
  lillyDrawWheel();
  lillyRenderRecent();
  _lillyLiveTimer = setInterval(lillyTick, 1000);     // clock + tiles every second
  _lillyWheelTimer = setInterval(lillyDrawWheel, 5000); // wheel + planets every 5s
}

// Pause when leaving home (battery saver)
function lillyPauseLive() {
  if (_lillyLiveTimer) { clearInterval(_lillyLiveTimer); _lillyLiveTimer = null; }
  if (_lillyWheelTimer) { clearInterval(_lillyWheelTimer); _lillyWheelTimer = null; }
}

// ═══════════ HOME CHAMBER RENDERER ═══════════
const HOME_PLANET_ORDER = ['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn','Uranus','Neptune','Pluto','Chiron','Lilith','Rahu','Ketu','Part of Fortune','Part of Spirit'];
const HOME_PLANET_COLORS = {Sun:'#ffd166',Moon:'#cfd8ff',Mercury:'#b0b0b0',Venus:'#f5b8d0',Mars:'#ff6b5e',Jupiter:'#e0a96d',Saturn:'#c9b27e',Uranus:'#7fe3e3',Neptune:'#9b8cff',Pluto:'#a06bd0',Chiron:'#9bd1a0',Lilith:'#caa0ff',Rahu:'#ff7fa0',Ketu:'#ff7fa0','Part of Fortune':'#ffe08a','Part of Spirit':'#bfe3ff'};
const HOME_PLANET_KAMEA_ORDER = {Saturn:3,Jupiter:4,Mars:5,Sun:6,Venus:7,Mercury:8,Moon:9};

function _sgn(lon){ try { return signOf(lon); } catch(e){ return {name:'',sym:''}; } }

// ── Planetary magic square (awfaq) generator ──
function _siamese(n){ const m=Array.from({length:n},()=>Array(n).fill(0)); let r=0,c=(n-1)/2|0; for(let k=1;k<=n*n;k++){ m[r][c]=k; let nr=(r-1+n)%n,nc=(c+1)%n; if(m[nr][nc]){ nr=(r+1)%n; nc=c; } r=nr;c=nc; } return m; }
function _doublyEven(n){ const m=Array.from({length:n},(_,i)=>Array.from({length:n},(_,j)=>i*n+j+1)); for(let i=0;i<n;i++)for(let j=0;j<n;j++){ if((i%4===j%4)||((i%4)+(j%4)===3)) m[i][j]=n*n+1-m[i][j]; } return m; }
function _singlyEven(n){ const h=n/2; const q=_siamese(h); const off=k=>q.map(r=>r.map(v=>v+k*h*h)); const A=off(0),B=off(1),C=off(2),D=off(3); const M=Array.from({length:n},()=>Array(n).fill(0)); for(let i=0;i<h;i++)for(let j=0;j<h;j++){M[i][j]=A[i][j];M[i][j+h]=B[i][j];M[i+h][j]=C[i][j];M[i+h][j+h]=D[i][j];} const t=Math.floor(h/2); for(let i=0;i<h;i++){ for(let j=0;j<t;j++){ if(i===Math.floor(h/2)&&j===t-1) continue; const x=M[i][j];M[i][j]=M[i+h][j];M[i+h][j]=x; } for(let j=n-t;j<n;j++){ const x=M[i][j];M[i][j]=M[i+h][j];M[i+h][j]=x; } } return M; }
function buildKamea(n){ if(n%2===1) return _siamese(n); if(n%4===0) return _doublyEven(n); return _singlyEven(n); }
function kameaHTML(planet){ const order=HOME_PLANET_KAMEA_ORDER[planet]; if(!order) return ''; const m=buildKamea(order); const sum=order*(order*order+1)/2; const rows=m.map(r=>`<tr>${r.map(v=>`<td>${v}</td>`).join('')}</tr>`).join(''); return `<div class="kamea-wrap"><table class="kamea"><tbody>${rows}</tbody></table><div class="kamea-cap">Square of ${esc(planet)} · order ${order} · each row, column &amp; diagonal sums to ${sum}</div></div>`; }

async function renderHomeChamber(){
  let home=null, live=null, pic=null;
  try { home = await loadJSON('/api/home'); } catch(e){}
  try { live = await loadJSON('/api/live'); } catch(e){}
  try { pic = await loadJSON('/api/picatrix/correspondences'); } catch(e){}
  if(!home && !live) return;

  // ── THE LIVE CHART GRID (signs, planets, fixed symbol icons) ──
  const planets = (live&&live.planets)||{};
  const grid = document.getElementById('home-chart-grid');
  if(grid){
    const ordered = HOME_PLANET_ORDER.filter(n=>planets[n]);
    grid.innerHTML = ordered.map(n=>{
      const p=planets[n]; const col=HOME_PLANET_COLORS[n]||'#fff';
      const ret = (p.retrograde)?' <span class="retro">R</span>':'';
      const s = _sgn(p.longitude);
      return `<div class="chart-row" onclick="showPlanetPanel('${esc(n)}')">
        <span class="cr-sym" style="color:${col}">${p.symbol||''}</span>
        <span class="cr-name">${esc(n)}</span>
        <span class="cr-sign" style="color:${col}">${s.sym}</span>
        <span class="cr-signname">${esc(p.sign||'')}</span>
        <span class="cr-deg">${esc(p.degree||'')}</span>
        <span class="cr-house">H${p.house!=null?p.house:'–'}</span>${ret}
      </div>`;
    }).join('');
  }

  // ── QURAN & HADITH ──
  const qh = (home&&home.quran_hadith)||{};
  const q = qh.quran||{};
  const qtrans = q.translation||'';
  setHTML('home-quran', `
    <div class="qmeta">Surah ${esc(q.surahNameEn||'—')} · ${q.surah!=null?q.surah:'—'}:${q.ayah!=null?q.ayah:'—'}</div>
    <div class="qarabic" dir="rtl" lang="ar">${esc(q.arabic||'')}</div>
    <div class="qtrans">${esc(qtrans.slice(0,280))}${qtrans.length>280?'…':''}</div>`);
  const h = qh.hadith||{};
  const htxt = h.english||'';
  setHTML('home-hadith', `
    <div class="qmeta">${esc(h.bookName||'—')}</div>
    <div class="qtrans">${esc(htxt.slice(0,340))}${htxt.length>340?'…':''}</div>
    <div class="qmeta">— ${esc(h.narratorEn||'')}</div>`);

  // ── TAROT OF THE DAY ──
  const t = (home&&home.tarot)||{};
  setTxt('home-tarot-name', t.name ? `${esc(t.name)}${t.reversed?' (reversed)':''} · ${esc(t.suit||'')}` : '—');
  setHTML('home-tarot', `
    <div class="tarot-keywords">${(t.keywords||[]).map(k=>`<span class="kw">${esc(k)}</span>`).join('')}</div>
    <div class="tarot-block"><strong>Meaning:</strong> ${esc(t.upright||'')}</div>
    <div class="tarot-block"><strong>Lilly's daily message:</strong> ${esc(t.daily_message||'')}</div>`);

  // ── MAGICAL WEATHER ──
  const ia = (home&&home.islamic_astro)||{};
  const mp = ia.mansion||{};
  const ph = (live&&live.planetary_hour)||{};
  const moonPh = (live&&live.moon_phase)||{};
  const ruler = ia.day_ruler || (ph&&ph.planet) || 'Sun';
  const aspectsAll = (live&&live.aspects)||[];
  const majors = aspectsAll.filter(a=>a.aspect!=='Quincunx').slice(0,8);
  const mjHTML = majors.length ? majors.map(a=>`<span class="asp-chip">${a.p1_symbol||''} ${esc(a.aspect)} ${a.p2_symbol||''} <em>${a.orb}°</em></span>`).join('') : '<span class="asp-chip">No major aspects</span>';
  // Truthful fallbacks: Element from the Moon; Colour from the ruler's traditional hue
  const moonEl = (live&&live.planets&&live.planets.Moon&&live.planets.Moon.element)?live.planets.Moon.element.replace(/^[^\s]+\s/,''):'';
  const elementVal = mp.element || moonEl || (mp.quality||'—');
  const PLANET_COLOR_WORD = {Sun:'Gold',Moon:'Silver-White',Mercury:'Orange & mixed',Venus:'Green',Mars:'Red',Jupiter:'Blue-Violet',Saturn:'Black',Uranus:'Variegated',Neptune:'Sea-Green',Pluto:'Deep Crimson',Rahu:'Smoky',Ketu:'Smoky'};
  const colourVal = mp.colour || mp.color || PLANET_COLOR_WORD[ruler] || '—';
  setHTML('home-magic', `
    <div class="magic-cell"><div class="mc-label">🌙 Lunar Mansion</div><div class="mc-val">${esc(mp.picatrix_name||'—')}</div><div class="mc-sub">${esc(mp.arabic_name||'')} · ${esc(mp.nature||'')}</div></div>
    <div class="magic-cell"><div class="mc-label">🜔 Element</div><div class="mc-val">${esc(elementVal)}</div></div>
    <div class="magic-cell"><div class="mc-label">⏳ Ruling Hour</div><div class="mc-val">${esc(ph.planet||'—')}</div><div class="mc-sub">${esc(ph.spirit_name?('Spirit: '+ph.spirit_name):'')}</div></div>
    <div class="magic-cell"><div class="mc-label">🪐 Ruling Planet (day)</div><div class="mc-val">${esc(ia.day_ruler||'—')}</div></div>
    <div class="magic-cell"><div class="mc-label">🎨 Colour</div><div class="mc-val">${esc(colourVal)}</div></div>
    <div class="magic-cell"><div class="mc-label">🌗 Moon</div><div class="mc-val">${moonPh.emoji||'🌙'} ${esc(moonPh.phase||'—')}</div></div>
    <div class="magic-cell magic-wide"><div class="mc-label">✶ Major Aspects</div><div class="asp-row">${mjHTML}</div></div>`);

  // ── REMEDY: Picatrix + Red Magick + Magic Square ──
  const pcPlanets = (pic&&pic.planets)||{};
  const corr = pcPlanets[ruler]||{};
  const notes = corr.additional_notes||'';
  const animals = (corr.animals||[]).slice(0,6).join(', ');
  const works = (corr.associated_operations_works||[]).slice(0,5).join('; ');
  setHTML('home-remedy', `
    <div class="remedy-cell"><div class="rc-label">⚗️ Picatrix — ${esc(ruler)}</div>
      <div class="rc-body">${esc(notes)}</div>
      ${animals?`<div class="rc-sub"><strong>Creatures:</strong> ${esc(animals)}</div>`:''}
      ${works?`<div class="rc-sub"><strong>Works:</strong> ${esc(works)}</div>`:''}
    </div>
    <div class="remedy-cell"><div class="rc-label">📕 Red Magick (Al-Toukhi)</div>
      <div class="rc-body">After the manner of Al-Toukhi's <em>Red Magick</em>, the square below may be charged as a servitor-trap for a djinn of the ${esc(ruler)} order — yet Lilly counsels discretion: name the spirit, bind it to the work, and never leave the seal unfinished.</div>
    </div>
    <div class="remedy-cell remedy-square">${kameaHTML(ruler)}</div>`);

  // ── WHAT THE MASTERS WOULD SAY ──
  const naks = ia.nakshatra||{};
  const moonLat = (live&&live.planets&&live.planets.Moon&&live.planets.Moon.latitude!=null)?live.planets.Moon.latitude.toFixed(2)+'°':'—';
  const scholarHTML = `
    <p>Lilly's synthesis, in the spirit of the old masters:</p>
    <p>Today the sky is ruled by <strong>${esc(ruler)}</strong>, and the Moon walks the mansion of <strong>${esc(mp.picatrix_name||'—')}</strong> (${esc(mp.arabic_name||'')}), whose nature is <em>${esc(mp.nature||'mixed')}</em>. ${esc(mp.benefic?('The mansion is spoken of as '+mp.benefic+'.'):'')}</p>
    <p><strong>Abu Ma'shar</strong> would read the general elections of the day by this ruler; <strong>Al-Kindi</strong> would weigh the rays and influences falling upon Kariega; <strong>Al-Biruni</strong> would fix the mansion's precise degree and the Moon's latitude (${moonLat}). <strong>Al-Buni</strong> would trace the divine Names through the awfaq of ${esc(ruler)}; and <strong>Ibn Arabi</strong> would see in this hour a theophany — the Real disclosing Himself through the planet's light.</p>
    <p>The Moon is <em>${esc(moonPh.phase||'—')}</em>; the Moon's nakshatra is <strong>${esc(naks.name||'—')}</strong> (lord ${esc(naks.lord||'—')}, deity ${esc(naks.deity||'—')}). ${majors.length?('The chief aspect now is '+majors[0].p1+' '+majors[0].aspect+' '+majors[0].p2+'.'):'The planets move without pressing aspect.'}</p>`;
  setHTML('home-scholar', scholarHTML);
}

// ─── Boot ───────────────────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {
  startLillyLive();

  // Planet panel close
  const ppClose = document.getElementById('planet-panel-close');
  if (ppClose) ppClose.addEventListener('click', closePlanetPanel);

  // Re-render recent conversation whenever the chat tab is shown
  const chatTab = document.getElementById('tab-chat');
  if (chatTab) {
    const obs = new MutationObserver(() => {
      if (chatTab.classList.contains('active')) lillyRenderRecent();
    });
    obs.observe(chatTab, { attributes: true, attributeFilter: ['class'] });
  }

  // Refresh the home chamber whenever the home tab is opened, and once at boot
  const homeTab = document.getElementById('tab-home');
  if (homeTab) {
    const hobs = new MutationObserver(() => {
      if (homeTab.classList.contains('active')) renderHomeChamber();
    });
    hobs.observe(homeTab, { attributes: true, attributeFilter: ['class'] });
    renderHomeChamber();
  }

  // Initial greeting in chat tab (single Lilly avatar)
  const msgs = document.getElementById('chat-messages');
  if (msgs && !msgs.dataset.lillyGreeted) {
    msgs.dataset.lillyGreeted = '1';
    msgs.innerHTML = `<div class="chat-msg"><div class="avatar"><img src="${LILLY_AVATAR}" alt="Lilly"></div><div class="bubble">Lilly is waiting… ✨ Ask me about the stars, the cards, the mansions, or the old grimoires.</div></div>`;
  }
});
