/* ═══════════════════════════════════════════════════════════════════════════
   LILLY · CORE — homepage live loop, hero tiles, recent-conversation rendering.
   openTab, lillyAsk, sendChat, LILLY_AVATAR, lillyLoadRecent/SaveRecent, esc,
   loadJSON are defined in the inline script (templates/index.html).
   ═══════════════════════════════════════════════════════════════════════════ */

// ─── Utilities ───────────────────────────────────────────────────────────────
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

// ─── Boot ───────────────────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {
  startLillyLive();

  // Re-render recent conversation whenever the chat tab is shown
  const chatTab = document.getElementById('tab-chat');
  if (chatTab) {
    const obs = new MutationObserver(() => {
      if (chatTab.classList.contains('active')) lillyRenderRecent();
    });
    obs.observe(chatTab, { attributes: true, attributeFilter: ['class'] });
  }

  // Initial greeting in chat tab (single Lilly avatar)
  const msgs = document.getElementById('chat-messages');
  if (msgs && !msgs.dataset.lillyGreeted) {
    msgs.dataset.lillyGreeted = '1';
    msgs.innerHTML = `<div class="chat-msg"><div class="avatar"><img src="${LILLY_AVATAR}" alt="Lilly"></div><div class="bubble">Lilly is waiting… ✨ Ask me about the stars, the cards, the mansions, or the old grimoires.</div></div>`;
  }
});
