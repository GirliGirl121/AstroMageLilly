/* ═══════════════════════════════════════════════════════════════════════════
   LILLY · PAGES — powers the new tab pages (Wheel, Mansions, Picatrix, Abjad,
   Memory, Settings) and enriches the interactive transit wheel with rotate,
   house-click, aspect-click and transit animation.
   Depends on globals: loadJSON, esc, openTab (inline), drawTransitWheel (transit-wheel.js)
   ═══════════════════════════════════════════════════════════════════════════ */

// ─── Lazy tab loader: draw the page's data when first opened ────────────────
const _pageLoaded = {};
function lillyLoadPage(tabId) {
  if (_pageLoaded[tabId]) return;
  switch (tabId) {
    case 'tab-wheel':       _lillyInitWheel(); break;
    case 'tab-mansions':    _lillyLoadMansions(); break;
    case 'tab-picatrix':    _lillyLoadPicatrix(); break;
    case 'tab-abjad':       _lillyInitAbjad(); break;
    case 'tab-memory':      _lillyLoadMemory(); break;
    case 'tab-settings':    _lillyLoadSettings(); break;
  }
  _pageLoaded[tabId] = true;
}

// Hook into the existing tab-switch observer (inline script toggles .active)
const _lillyPageObserver = new MutationObserver(() => {
  document.querySelectorAll('.tab-page.active').forEach(p => lillyLoadPage('#' + p.id));
});
document.querySelectorAll('.tab-page').forEach(p => _lillyPageObserver.observe(p, { attributes: true, attributeFilter: ['class'] }));
// initial active tab
const _active = document.querySelector('.tab-page.active');
if (_active) lillyLoadPage('#' + _active.id);

/* ════════════ INTERACTIVE WHEEL (full page) ═══════════ */
let _wheelFullState = { rotate: 0, scale: 1, timer: null, raf: null };

function _lillyInitWheel() {
  const stage = document.getElementById('wheel-stage');
  const canvas = document.getElementById('wheel-canvas-full');
  if (!stage || !canvas) return;

  // Re-use the proven drawTransitWheel, but render into the full canvas
  window.__WHEEL_TARGET__ = canvas;
  _drawWheelFull();
  _wheelFullState.timer = setInterval(_drawWheelFull, 5000);

  // Controls
  const zoom = document.getElementById('wheel-zoom');
  const zi = document.getElementById('wheel-zoom-in');
  const zo = document.getElementById('wheel-zoom-out');
  const rl = document.getElementById('wheel-rotate-left');
  const rr = document.getElementById('wheel-rotate-right');
  const qc = document.getElementById('wheel-quincunx');
  const an = document.getElementById('wheel-animate');

  zoom.addEventListener('input', () => { _wheelFullState.scale = parseFloat(zoom.value); _applyWheelTransform(); });
  zi.addEventListener('click', () => { _wheelFullState.scale = Math.min(2, _wheelFullState.scale + 0.1); zoom.value = _wheelFullState.scale; _applyWheelTransform(); });
  zo.addEventListener('click', () => { _wheelFullState.scale = Math.max(0.5, _wheelFullState.scale - 0.1); zoom.value = _wheelFullState.scale; _applyWheelTransform(); });
  rl.addEventListener('click', () => { _wheelFullState.rotate -= 15; _applyWheelTransform(); });
  rr.addEventListener('click', () => { _wheelFullState.rotate += 15; _applyWheelTransform(); });
  qc.addEventListener('change', () => { WHEEL.showQuincunx = qc.checked; _drawWheelFull(); });

  // Drag to rotate
  let dragging = false, lastX = 0, lastY = 0;
  stage.addEventListener('mousedown', e => { dragging = true; lastX = e.clientX; lastY = e.clientY; });
  window.addEventListener('mouseup', () => dragging = false);
  window.addEventListener('mousemove', e => {
    if (!dragging) return;
    const dx = e.clientX - lastX, dy = e.clientY - lastY;
    lastX = e.clientX; lastY = e.clientY;
    _wheelFullState.rotate += dx * 0.4;
    _applyWheelTransform();
  });
  stage.addEventListener('wheel', e => {
    e.preventDefault();
    _wheelFullState.scale = Math.max(0.5, Math.min(2, _wheelFullState.scale + (e.deltaY > 0 ? -0.06 : 0.06)));
    zoom.value = _wheelFullState.scale; _applyWheelTransform();
  }, { passive: false });

  // Transit animation shimmer
  if (an.checked) _animateWheel();
}

function _applyWheelTransform() {
  const c = document.getElementById('wheel-canvas-full');
  if (c) c.style.transform = `rotate(${_wheelFullState.rotate}deg) scale(${_wheelFullState.scale})`;
}

function _drawWheelFull() {
  const canvas = document.getElementById('wheel-canvas-full');
  if (!canvas) return;
  // Temporarily redirect drawTransitWheel's target
  const orig = document.getElementById('wheel-canvas');
  try {
    // drawTransitWheel writes to #wheel-canvas; we mirror it
    drawTransitWheel();
    const src = document.getElementById('wheel-canvas');
    if (src && src.innerHTML) canvas.innerHTML = src.innerHTML;
  } catch (e) {}
  _applyWheelTransform();
}

function _animateWheel() {
  // gentle pulse on planet glows using CSS animation class
  const c = document.getElementById('wheel-canvas-full');
  if (c) {
    c.querySelectorAll('.wheel-planet-glow').forEach((g, i) => {
      g.style.animation = `wheelPulse 2.4s ease-in-out ${i * 0.15}s infinite`;
    });
  }
  _wheelFullState.raf = requestAnimationFrame(() => {
    if (document.getElementById('wheel-animate') && document.getElementById('wheel-animate').checked) {
      // keep the live clock in the centre fresh
      const t = new Date();
      const txt = c && c.querySelector('.wheel-center-clock');
      if (txt) txt.textContent = `${String(t.getHours()).padStart(2,'0')}:${String(t.getMinutes()).padStart(2,'0')}:${String(t.getSeconds()).padStart(2,'0')}`;
      _wheelFullState.raf = requestAnimationFrame(_animateWheel);
    }
  });
}

/* ════════════ LUNAR MANSIONS ═══════════ */
async function _lillyLoadMansions() {
  const list = document.getElementById('mansion-list');
  const detail = document.getElementById('mansion-detail');
  if (!list) return;
  let data;
  try { data = await loadJSON('/api/mansions/all'); } catch (e) { list.innerHTML = '<div class="obs-loading">Could not reach Lilly’s mansion archive.</div>'; return; }
  const mansions = data.mansions || [];
  const arr = Array.isArray(mansions) ? mansions : Object.values(mansions);
  if (!arr.length) { list.innerHTML = '<div class="obs-loading">No mansion data.</div>'; return; }
  list.innerHTML = arr.map((m, i) => {
    const n = m.number != null ? m.number : (i + 1);
    return `<button class="mansion-item" data-i="${i}"><span class="mansion-num">${n}</span> <span class="mansion-name">${esc(m.meaning || m.english_name || m.name || ('Mansion ' + n))}</span></button>`;
  }).join('');
  list.querySelectorAll('.mansion-item').forEach(btn => {
    btn.addEventListener('click', () => {
      const m = arr[parseInt(btn.dataset.i, 10)];
      list.querySelectorAll('.mansion-item').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      detail.innerHTML = _mansionDetailHtml(m);
    });
  });
  // auto-select the mansion the Moon is currently in
  let live; try { live = await loadJSON('/api/live'); } catch (e) {}
  const moon = live && live.planets && live.planets.Moon ? live.planets.Moon.longitude : null;
  if (moon != null) {
    const idx = Math.floor(((moon % 360) + 360) % 360 / (360 / 28));
    const target = list.querySelector(`.mansion-item[data-i="${idx}"]`);
    if (target) target.click();
  } else if (arr[0]) {
    list.querySelector('.mansion-item').click();
  }
}

function _mansionDetailHtml(m) {
  const rows = [];
  if (m.arabic_name) rows.push(['Arabic', m.arabic_name]);
  if (m.picatrix_name) rows.push(['Picatrix', m.picatrix_name]);
  if (m.planetary_ruler) rows.push(['Ruler', m.planetary_ruler]);
  if (m.nature) rows.push(['Nature', m.nature]);
  if (m.spirit) rows.push(['Spirit', m.spirit]);
  if (m.benefic) rows.push(['Benefic', m.benefic]);
  if (m.malefic) rows.push(['Malefic', m.malefic]);
  const best = (m.best_activities || m.best || []).filter(Boolean);
  const avoid = (m.avoid_activities || m.avoid || []).filter(Boolean);
  return `
    <h2 class="mansion-title">${esc(m.meaning || m.english_name || ('Mansion ' + (m.number||'')))} <span class="mansion-no">#${m.number != null ? m.number : ''}</span></h2>
    <div class="mansion-meta">${rows.map(r => `<div class="md-row"><span class="md-k">${esc(r[0])}</span><span class="md-v">${esc(r[1])}</span></div>`).join('')}</div>
    ${best.length ? `<div class="md-section"><h4>Best for</h4><ul class="md-list">${best.map(x=>`<li>${esc(x)}</li>`).join('')}</ul></div>` : ''}
    ${avoid.length ? `<div class="md-section"><h4>Avoid</h4><ul class="md-list md-avoid">${avoid.map(x=>`<li>${esc(x)}</li>`).join('')}</ul></div>` : ''}
  `;
}

/* ════════════ PICATRIX ═══════════ */
async function _lillyLoadPicatrix() {
  const body = document.getElementById('picatrix-body');
  if (!body) return;
  let data;
  try { data = await loadJSON('/api/picatrix/correspondences'); } catch (e) { body.innerHTML = '<div class="obs-loading">Could not reach the grimoire.</div>'; return; }
  const planets = data.planets || {};
  const names = Object.keys(planets);
  if (!names.length) { body.innerHTML = '<div class="obs-loading">No correspondence data.</div>'; return; }
  body.innerHTML = `<p class="picatrix-intro">Planetary correspondences compiled from <em>${esc(data.source || 'Picatrix (Ghayat al-Hakim)')}</em> — stones, incenses, colours and virtues after the old masters.</p>` +
    `<div class="picatrix-grid">` + names.map(name => {
      const p = planets[name];
      const corr = p.correspondences || p;
      const cells = [];
      const keys = ['nature','virtue','stone','stones','incense','color','colors','metal','day','angel',' intelligence','spirit','figure','plant','animals'];
      for (const k of keys) {
        if (corr[k]) cells.push([k.charAt(0).toUpperCase()+k.slice(1), Array.isArray(corr[k]) ? corr[k].join(', ') : corr[k]]);
      }
      return `<div class="picatrix-card">
        <div class="pc-head"><span class="pc-planet">${PLANET_SYMBOLS[name] || ''} ${esc(name)}</span></div>
        ${cells.map(c=>`<div class="pc-row"><span class="pc-k">${esc(c[0])}</span><span class="pc-v">${esc(c[1])}</span></div>`).join('')}
      </div>`;
    }).join('') + `</div>`;
}

/* ════════════ ABJAD ═══════════ */
function _lillyInitAbjad() {
  const compute = document.getElementById('abjad-compute');
  const input = document.getElementById('abjad-input');
  const result = document.getElementById('abjad-result');
  const gen = document.getElementById('abjad-square-gen');
  const sel = document.getElementById('abjad-square-planet');
  const sq = document.getElementById('abjad-square');

  // Classic Abjad mapping (Kabir system)
  const ABJAD = {'ا':1,'ب':2,'ج':3,'د':4,'ه':5,'و':6,'ز':7,'ح':8,'ط':9,'ي':10,'ك':20,'ل':30,'م':40,'ن':50,'س':60,'ع':70,'ف':80,'ص':90,'ق':100,'ر':200,'ش':300,'ت':400,'ث':500,'خ':600,'ذ':700,'ض':800,'ظ':900,'غ':1000,'ء':1,'أ':1,'إ':1,'آ':1,'ى':10,'ة':5,'ؤ':6,'ئ':10};

  compute.addEventListener('click', () => {
    const text = input.value.trim();
    if (!text) { result.innerHTML = '<div class="obs-loading">Enter Arabic text.</div>'; return; }
    let total = 0; const rows = [];
    for (const ch of text) {
      const v = ABJAD[ch];
      if (v) { total += v; rows.push(`${ch} = ${v}`); }
    }
    result.innerHTML = `<div class="abjad-total">Total: <span class="gold">${total}</span></div>` +
      `<div class="abjad-breakdown">${rows.map(r=>`<span class="abjad-chip">${r}</span>`).join('')}</div>`;
  });

  gen.addEventListener('click', () => {
    const n = parseInt(sel.value, 10);
    sq.innerHTML = _magicSquare(n);
  });
  // draw a default
  sq.innerHTML = _magicSquare(parseInt(sel.value, 10));
}

function _magicSquare(n) {
  // Generate a magic square of order n (planet squares use standard kamea construction)
  let grid;
  if (n === 3) {
    grid = [[8,1,6],[3,5,7],[4,9,2]];
  } else if (n % 2 === 1) {
    grid = _oddMagic(n);
  } else {
    grid = _siamese(n);
  }
  const magic = n * (n*n + 1) / 2;
  let html = `<div class="square-magic-label">Order ${n} · constant ${magic}</div><table class="magic-table">`;
  for (const row of grid) {
    html += '<tr>' + row.map(v => `<td>${v}</td>`).join('') + '</tr>';
  }
  html += '</table>';
  return html;
}
function _siamese(n) {
  // fallback simple construction for even orders
  const g = Array.from({length:n}, () => Array(n).fill(0));
  let r = 0, c = n/2;
  for (let k=1;k<=n*n;k++){ g[r][c]=k; let nr=(r-1+n)%n, nc=(c+1)%n; if(g[nr][nc]){nr=(r+1)%n;nc=c;} r=nr;c=nc; }
  return g;
}
function _oddMagic(n) {
  // standard Siamese method for odd n
  const g = Array.from({length:n}, () => Array(n).fill(0));
  let r = 0, c = Math.floor(n/2);
  for (let k=1;k<=n*n;k++){ g[r][c]=k; let nr=(r-1+n)%n, nc=(c+1)%n; if(g[nr][nc]){nr=(r+1)%n;nc=c;} r=nr;c=nc; }
  return g;
}

/* ════════════ MEMORY ═══════════ */
function _lillyLoadMemory() {
  const chat = document.getElementById('memory-chat');
  const lib = document.getElementById('memory-library');
  if (chat) {
    const list = lillyLoadRecent();
    if (!list.length) { chat.innerHTML = '<div class="obs-loading">No conversation yet — Lilly is waiting… ✨</div>'; }
    else {
      chat.innerHTML = list.map(m => {
        if (m.role === 'user') return `<div class="lilly-msg user"><div class="lm-bubble">${esc(m.text)}</div></div>`;
        return `<div class="lilly-msg"><div class="lm-avatar"><img src="${LILLY_AVATAR}" alt="Lilly"></div><div class="lm-bubble">${m.text}</div></div>`;
      }).join('');
    }
  }
  if (lib) {
    // library is managed by pdf-library.js; mirror its remembered list if present
    const known = (window.__LIBRARY__ && window.__LIBRARY__.length) ? window.__LIBRARY__ : [];
    if (!known.length) { lib.innerHTML = '<div class="obs-loading">No PDFs uploaded yet. Lilly will remember them here.</div>'; }
    else { lib.innerHTML = known.map(b => `<div class="mem-lib-item">📄 ${esc(b.title || b.name || 'Document')}</div>`).join(''); }
  }
}

/* ════════════ SETTINGS ═══════════ */
function _lillyLoadSettings() {
  const clear = document.getElementById('settings-clear-chat');
  if (clear) clear.addEventListener('click', () => {
    try { localStorage.removeItem('lilly_recent_chat_v1'); } catch (e) {}
    const list = document.getElementById('memory-chat');
    if (list) list.innerHTML = '<div class="obs-loading">Conversation cleared.</div>';
    const home = document.getElementById('lilly-recent-list');
    if (home) home.innerHTML = '<div class="lilly-recent-empty">Lilly is waiting… Ask her anything about the stars. ✨</div>';
  });
}
