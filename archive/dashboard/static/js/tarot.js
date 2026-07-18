async function loadTarotFull() {
  // Load shared tarot data once
  try {
    const td = await loadJSON('/static/tarot_data.json');
    window._tarotData = td;
    // Build flat cards list if not present in data
    if(!td.cards) {
      const all = [...(td.major_arcana||[])];
      for(const suit of ['wands','cups','swords','pentacles']) {
        for(const c of (td.minor_arcana?.[suit]||[])) { c.suit = suit; all.push(c); }
      }
      td.cards = all;
    }
    tarotLoadCardLibrary();
    tarotLoadJournal();
    tarotLoadLearnTarot();
    switchTarotSection('new-reading', document.querySelector('[data-tarot-section="new-reading"]'));
  } catch(e) { /* silent */ }
}

// ══════════ Tarot Section Switching ══════════
function switchTarotSection(section, btn) {
  document.querySelectorAll('.tarot-section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.tarot-subnav-item').forEach(b => b.classList.remove('active'));
  const target = document.getElementById('tarot-'+section);
  if(target) target.classList.add('active');
  if(btn) btn.classList.add('active');
  // Lazy-load sections on first visit
  if(section==='card-library' && window._tarotData) {
    const grid = document.getElementById('tarot-library-grid');
    if(grid && grid.innerHTML.includes('Loading')) tarotLoadCardLibrary();
  }
  if(section==='learn-tarot') {
    const lc = document.getElementById('tarot-learn-content');
    if(lc && lc.innerHTML.includes('Loading')) tarotLoadLearnTarot();
  }
}

// ══════════ Card Image (RWS Public Domain Ready) ══════════
// The original 1909 Rider-Waite-Smith deck is public domain.
// Add images to /static/tarot_cards/ following this convention:
//   major_00_fool.jpg ... major_21_world.jpg
//   minor_wands_01_ace.jpg ... minor_pentacles_14_king.jpg
//   minor_cups_01_ace.jpg ... minor_swords_14_king.jpg
function tarotCardFace(card) {
  const suit = card.suit || 'major';
  const emoji = suit==='major'?'⭐':suit==='wands'?'🪄':suit==='cups'?'🏆':suit==='swords'?'⚔️':'🪙';
  const label = suit==='major'?'Major Arcana':suit.charAt(0).toUpperCase()+suit.slice(1);
  // Try to load RWS image, fall back to styled placeholder
  const id = String(card.id||0).padStart(2,'0');
  const slug = (card.name||'').toLowerCase().replace(/[^a-z0-9]+/g,'_').replace(/^_|_$/g,'');
  const imgPath = `/static/tarot_cards/${suit}_${id}_${slug}.jpg`;
  return `<div class="tarot-card-face" data-img="${imgPath}" style="background:var(--bg-card);border:1px solid var(--border);border-radius:8px;padding:12px;text-align:center;min-height:130px;display:flex;flex-direction:column;align-items:center;justify-content:center">
    <div style="font-size:32px;margin-bottom:4px">${emoji}</div>
    <div style="font-size:10px;color:var(--text-muted)">${label}</div>
  </div>`;
}

// ══════════ 🔮 New Reading ══════════
async function tarotDrawCards() {
  const count = parseInt(document.getElementById('tarot-spread-select').value);
  const resultDiv = document.getElementById('tarot-reading-result');
  if(!resultDiv) return;
  resultDiv.innerHTML = '<div class="loading">🔮 Drawing cards...</div>';
  try {
    const data = await loadJSON('/api/tarot/draw?count='+count);
    const cards = data.cards||[];
    const spreadNames = {1:'Quick Insight',3:'Past · Present · Future',5:'Cross of Intent',10:'Celtic Cross'};
    const positions = {1:['The Message'],3:['Past','Present','Future'],5:['Self','Challenge','Past','Future','Outcome'],10:['Self','Challenge','Past','Future','Above','Below','Advice','External','Hopes','Outcome']};
    const pos = positions[count]||cards.map((_,i)=>'Card '+(i+1));
    let html = `<div class="tarot-spread-label">${spreadNames[count]||count+' cards'}</div>
      <div class="tarot-cards-row">`;
    for(let i=0;i<cards.length;i++) {
      const c = cards[i];
      html += `<div class="tarot-card-display">
        ${tarotCardFace(c)}
        <div class="tarot-card-pos">${pos[i]||''}</div>
        <div class="tarot-card-name">${c.name}</div>
        <div class="tarot-card-keywords">${(c.keywords||[]).join(' · ')}</div>
        <div class="tarot-card-meaning">${c.upright||c.upright_meaning||''}</div>
      </div>`;
    }
    html += `</div><div class="tarot-reading-actions">
      <button class="tarot-save-btn" onclick="tarotSaveReading(${JSON.stringify(cards.map(c=>({name:c.name,suit:c.suit,keywords:c.keywords,upright:c.upright||c.upright_meaning||''})))})">💾 Save Reading</button>
      <button class="tarot-draw-btn" onclick="tarotDrawCards()">🔮 Draw Again</button>
    </div>`;
    resultDiv.innerHTML = html;
  } catch(e) { resultDiv.innerHTML = `<div class="loading">${e.message}</div>`; }
}

// ══════════ 📚 Card Library ══════════
async function tarotLoadCardLibrary(filter) {
  const grid = document.getElementById('tarot-library-grid');
  if(!grid||!window._tarotData) return;
  const allCards = window._tarotData.cards||[];
  let html = `<div class="tarot-grid">`;
  for(const c of allCards) {
    const suit = c.suit||'major';
    if(filter&&filter!=='all'&&suit!==filter) continue;
    html += `<div class="tarot-card-item" data-suit="${suit}" onclick="tarotShowCardDetail('${esc(c.name)}')">
      ${tarotCardFace(c)}
      <div class="tarot-card-item-name">${c.name}</div>
      <div class="tarot-card-item-kw">${(c.keywords||[]).slice(0,2).join(', ')}</div>
    </div>`;
  }
  html += `</div>
    <div class="tarot-card-detail-overlay" id="tarot-card-detail" style="display:none" onclick="this.style.display='none'">
      <div class="tarot-card-detail-box" onclick="event.stopPropagation()">
        <button class="tarot-detail-close" onclick="document.getElementById('tarot-card-detail').style.display='none'">✕</button>
        <div id="tarot-card-detail-body"></div>
      </div>
    </div>`;
  grid.innerHTML = html;
  // Define filter function globally
  window.tarotFilterLibrary = function(f, btn) {
    document.querySelectorAll('.tarot-filter-btn').forEach(b=>b.classList.remove('active'));
    if(btn) btn.classList.add('active');
    document.querySelectorAll('.tarot-card-item').forEach(el=>{
      el.style.display = (f==='all'||el.dataset.suit===f)?'':'none';
    });
  };
  window.tarotShowCardDetail = function(name) {
    const card = allCards.find(c=>c.name===name);
    if(!card) return;
    const overlay = document.getElementById('tarot-card-detail');
    const body = document.getElementById('tarot-card-detail-body');
    if(!overlay||!body) return;
    body.innerHTML = `<div class="tarot-detail-layout">
      <div class="tarot-detail-image">${tarotCardFace(card)}</div>
      <div class="tarot-detail-info">
        <h2 class="tarot-detail-name">${card.name}</h2>
        <div class="tarot-detail-suit">${card.suit==='major'?'⭐ Major Arcana':card.suit.charAt(0).toUpperCase()+card.suit.slice(1)}</div>
        <div class="tarot-detail-keywords">${(card.keywords||[]).join(' · ')}</div>
        <div class="tarot-detail-section"><strong>Upright:</strong> ${card.upright||card.upright_meaning||'—'}</div>
        <div class="tarot-detail-section"><strong>Reversed:</strong> ${card.reversed||card.reversed_meaning||card.meaning_rev||'—'}</div>
        <div class="tarot-detail-daily"><em>Daily Message:</em> ${card.daily||card.daily_message||'—'}</div>
      </div>
    </div>`;
    overlay.style.display = 'flex';
  };
}

// ══════════ 📖 Reading Journal ══════════
function tarotLoadJournal() {
  const jc = document.getElementById('tarot-journal-content');
  if(!jc) return;
  const saved = JSON.parse(localStorage.getItem('tarotReadings')||'[]');
  if(saved.length===0) {
    jc.innerHTML = '<div class="tarot-journal-empty">Your saved readings will appear here. Perform a reading and save it to your journal! 📓</div>';
    return;
  }
  let html = '<div class="tarot-journal-list">';
  for(let i=saved.length-1;i>=0;i--) {
    const r = saved[i];
    const cards = r.cards||[];
    html += `<div class="tarot-journal-entry" onclick="tarotViewSavedReading(${i})">
      <div class="tarot-journal-date">${r.date||'Unknown'}</div>
      <div class="tarot-journal-spread">${cards.length} card${cards.length!==1?'s':''}</div>
      <div class="tarot-journal-cards">${cards.map(c=>c.name).join(' · ')}</div>
    </div>`;
  }
  html += '</div>';
  jc.innerHTML = html;
}

function tarotSaveReading(cards) {
  const readings = JSON.parse(localStorage.getItem('tarotReadings')||'[]');
  readings.push({
    date: new Date().toLocaleDateString('en-ZA',{year:'numeric',month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'}),
    cards: cards
  });
  localStorage.setItem('tarotReadings', JSON.stringify(readings));
  alert('💾 Reading saved to your journal!');
  tarotLoadJournal();
}

function tarotViewSavedReading(idx) {
  const readings = JSON.parse(localStorage.getItem('tarotReadings')||'[]');
  const r = readings[idx];
  if(!r) return;
  let html = `<div class="tarot-saved-detail">
    <div class="tarot-saved-date">📅 ${r.date}</div>
    <div class="tarot-cards-row">`;
  for(const c of (r.cards||[])) {
    html += `<div class="tarot-card-display">
      ${tarotCardFace(c)}
      <div class="tarot-card-name">${c.name}</div>
      <div class="tarot-card-keywords">${(c.keywords||[]).join(' · ')}</div>
      <div class="tarot-card-meaning">${c.upright||''}</div>
    </div>`;
  }
  html += `</div>
    <div class="tarot-reading-actions">
      <button class="tarot-draw-btn" onclick="if(confirm('Delete this reading?')){const r=JSON.parse(localStorage.getItem('tarotReadings')||'[]');r.splice(${idx},1);localStorage.setItem('tarotReadings',JSON.stringify(r));tarotLoadJournal();}">🗑️ Delete</button>
      <button class="tarot-draw-btn" onclick="tarotLoadJournal()">← Back to Journal</button>
    </div>`;
  document.getElementById('tarot-journal-content').innerHTML = html;
}

// ══════════ ⭐ Learn Tarot ══════════
async function tarotLoadLearnTarot() {
  const lc = document.getElementById('tarot-learn-content');
  if(!lc) return;
  const allCards = window._tarotData?.cards || [];
  const majorCards = allCards.filter(c=>c.suit==='major');
  const wandCards = allCards.filter(c=>c.suit==='wands');
  const cupCards = allCards.filter(c=>c.suit==='cups');
  const swordCards = allCards.filter(c=>c.suit==='swords');
  const pentCards = allCards.filter(c=>c.suit==='pentacles');

  lc.innerHTML = `<div class="tarot-learn-intro">
    A beginner's guide to the <strong>Rider-Waite-Smith Tarot</strong> — 78 cards of wisdom, symbolism, and self-discovery.
    The RWS deck, illustrated by <strong>Pamela Colman Smith</strong> in 1909 under the guidance of occultist A. E. Waite, revolutionised tarot with fully illustrated minor arcana cards.
  </div>

  <!-- ═══════ Card Index — All 78 Cards ═══════ -->
  <details class="tarot-learn-section" open>
    <summary class="tarot-learn-summary">🃏 Card Index — Browse All 78 Cards</summary>
    <div class="tarot-learn-body">
      <p>Click any card below to see its meaning, keywords, and daily message.</p>
      <div class="tarot-learn-filters" style="display:flex;gap:4px;flex-wrap:wrap;margin-bottom:12px">
        <button class="tarot-filter-btn active" onclick="tarotLearnFilter('all',this)">All</button>
        <button class="tarot-filter-btn" onclick="tarotLearnFilter('major',this)">⭐ Major</button>
        <button class="tarot-filter-btn" onclick="tarotLearnFilter('wands',this)">🪄 Wands</button>
        <button class="tarot-filter-btn" onclick="tarotLearnFilter('cups',this)">🏆 Cups</button>
        <button class="tarot-filter-btn" onclick="tarotLearnFilter('swords',this)">⚔️ Swords</button>
        <button class="tarot-filter-btn" onclick="tarotLearnFilter('pentacles',this)">🪙 Pentacles</button>
      </div>
      <input class="tarot-learn-search" id="tarot-learn-search" type="text" placeholder="Search cards by name, keyword, or meaning..." oninput="tarotLearnSearch(this)" style="width:100%;padding:10px 14px;background:var(--bg-card);border:1px solid var(--border);border-radius:8px;color:var(--text-primary);font-size:13px;font-family:inherit;margin-bottom:12px;box-sizing:border-box">
      <div class="tarot-learn-grid" id="tarot-learn-grid">Loading...
    </div>
    </div>
  </details>

  <!-- ═══════ The Fool's Journey ═══════ -->
  <details class="tarot-learn-section">
    <summary class="tarot-learn-summary">🛤️ The Fool's Journey — Major Arcana Deep Dive</summary>
    <div class="tarot-learn-body">
      <p>The 22 Major Arcana cards tell the story of <strong>The Fool's Journey</strong> — a spiritual allegory of the soul's growth from innocence to enlightenment. Each card is a stage of transformation.</p>
      <div class="tarot-fools-journey">
        <table style="width:100%;border-collapse:collapse;font-size:13px">
          <tr style="color:var(--gold);border-bottom:1px solid var(--border)"><th style="padding:6px 8px;text-align:left">#</th><th style="padding:6px 8px;text-align:left">Card</th><th style="padding:6px 8px;text-align:left">Lesson</th><th style="padding:6px 8px;text-align:left">Keyword</th></tr>
          <tr><td style="padding:6px 8px">0</td><td style="padding:6px 8px;font-weight:600">The Fool</td><td style="padding:6px 8px">The soul begins the journey with trust and innocence. Everything is possible.</td><td style="padding:6px 8px;color:var(--pink)">Beginnings</td></tr>
          <tr><td style="padding:6px 8px">1</td><td style="padding:6px 8px;font-weight:600">The Magician</td><td style="padding:6px 8px">Awakening to your own power. You have all the tools you need.</td><td style="padding:6px 8px;color:var(--pink)">Manifestation</td></tr>
          <tr><td style="padding:6px 8px">2</td><td style="padding:6px 8px;font-weight:600">The High Priestess</td><td style="padding:6px 8px">Turning inward. Intuition and hidden knowledge awaken.</td><td style="padding:6px 8px;color:var(--pink)">Intuition</td></tr>
          <tr><td style="padding:6px 8px">3</td><td style="padding:6px 8px;font-weight:600">The Empress</td><td style="padding:6px 8px">Connection to nature, fertility, and creative abundance.</td><td style="padding:6px 8px;color:var(--pink)">Nurture</td></tr>
          <tr><td style="padding:6px 8px">4</td><td style="padding:6px 8px;font-weight:600">The Emperor</td><td style="padding:6px 8px">Structure, authority, and the establishment of order.</td><td style="padding:6px 8px;color:var(--pink)">Authority</td></tr>
          <tr><td style="padding:6px 8px">5</td><td style="padding:6px 8px;font-weight:600">The Hierophant</td><td style="padding:6px 8px">Seeking wisdom from tradition, teachers, and spiritual institutions.</td><td style="padding:6px 8px;color:var(--pink)">Tradition</td></tr>
          <tr><td style="padding:6px 8px">6</td><td style="padding:6px 8px;font-weight:600">The Lovers</td><td style="padding:6px 8px">Choices of the heart. Union, values, and commitment.</td><td style="padding:6px 8px;color:var(--pink)">Love</td></tr>
          <tr><td style="padding:6px 8px">7</td><td style="padding:6px 8px;font-weight:600">The Chariot</td><td style="padding:6px 8px">Willpower and determination. Steer opposing forces toward victory.</td><td style="padding:6px 8px;color:var(--pink)">Willpower</td></tr>
          <tr><td style="padding:6px 8px">8</td><td style="padding:6px 8px;font-weight:600">Strength</td><td style="padding:6px 8px">Inner courage, compassion, and gentle mastery over instinct.</td><td style="padding:6px 8px;color:var(--pink)">Courage</td></tr>
          <tr><td style="padding:6px 8px">9</td><td style="padding:6px 8px;font-weight:600">The Hermit</td><td style="padding:6px 8px">Solitude, introspection, and the search for deeper truth.</td><td style="padding:6px 8px;color:var(--pink)">Wisdom</td></tr>
          <tr><td style="padding:6px 8px">10</td><td style="padding:6px 8px;font-weight:600">Wheel of Fortune</td><td style="padding:6px 8px">The cycles of life turn. Fate, change, and destiny unfold.</td><td style="padding:6px 8px;color:var(--pink)">Cycles</td></tr>
          <tr><td style="padding:6px 8px">11</td><td style="padding:6px 8px;font-weight:600">Justice</td><td style="padding:6px 8px">Truth, fairness, and karmic accountability. What you sow, you reap.</td><td style="padding:6px 8px;color:var(--pink)">Accountability</td></tr>
          <tr><td style="padding:6px 8px">12</td><td style="padding:6px 8px;font-weight:600">The Hanged Man</td><td style="padding:6px 8px">Surrender, pause, and seeing the world from a new perspective.</td><td style="padding:6px 8px;color:var(--pink)">Surrender</td></tr>
          <tr><td style="padding:6px 8px">13</td><td style="padding:6px 8px;font-weight:600">Death</td><td style="padding:6px 8px">Endings that make way for transformation. Release what no longer serves.</td><td style="padding:6px 8px;color:var(--pink)">Transformation</td></tr>
          <tr><td style="padding:6px 8px">14</td><td style="padding:6px 8px;font-weight:600">Temperance</td><td style="padding:6px 8px">Balance, patience, and the alchemical blending of opposites.</td><td style="padding:6px 8px;color:var(--pink)">Balance</td></tr>
          <tr><td style="padding:6px 8px">15</td><td style="padding:6px 8px;font-weight:600">The Devil</td><td style="padding:6px 8px">Confronting shadow, attachment, and the chains we create for ourselves.</td><td style="padding:6px 8px;color:var(--pink)">Shadow</td></tr>
          <tr><td style="padding:6px 8px">16</td><td style="padding:6px 8px;font-weight:600">The Tower</td><td style="padding:6px 8px">Sudden upheaval that shatters illusions. Rebuild on truth.</td><td style="padding:6px 8px;color:var(--pink)">Upheaval</td></tr>
          <tr><td style="padding:6px 8px">17</td><td style="padding:6px 8px;font-weight:600">The Star</td><td style="padding:6px 8px">Hope, healing, and divine inspiration after the storm.</td><td style="padding:6px 8px;color:var(--pink)">Hope</td></tr>
          <tr><td style="padding:6px 8px">18</td><td style="padding:6px 8px;font-weight:600">The Moon</td><td style="padding:6px 8px">Illusion, fear, and the subconscious. Trust your intuition through the dark.</td><td style="padding:6px 8px;color:var(--pink)">Illusion</td></tr>
          <tr><td style="padding:6px 8px">19</td><td style="padding:6px 8px;font-weight:600">The Sun</td><td style="padding:6px 8px">Joy, success, and radiant clarity. The light of truth shines.</td><td style="padding:6px 8px;color:var(--pink)">Joy</td></tr>
          <tr><td style="padding:6px 8px">20</td><td style="padding:6px 8px;font-weight:600">Judgement</td><td style="padding:6px 8px">A calling to rise, forgive, and embrace your higher purpose.</td><td style="padding:6px 8px;color:var(--pink)">Rebirth</td></tr>
          <tr><td style="padding:6px 8px">21</td><td style="padding:6px 8px;font-weight:600">The World</td><td style="padding:6px 8px">Completion, wholeness, and the joyful integration of all lessons.</td><td style="padding:6px 8px;color:var(--pink)">Completion</td></tr>
        </table>
      </div>
    </div>
  </details>

  <!-- ═══════ Astrology & Tarot Correspondences ═══════ -->
  <details class="tarot-learn-section">
    <summary class="tarot-learn-summary">🌌 Astrology & Tarot — Planetary & Zodical Correspondences</summary>
    <div class="tarot-learn-body">
      <p>Each Major Arcana card is associated with an astrological body or zodiac sign. The four suits correspond to the classical elements. Understanding these links deepens both your tarot and astrology practice.</p>
      <table style="width:100%;border-collapse:collapse;font-size:13px;margin-bottom:16px">
        <tr style="color:var(--gold);border-bottom:1px solid var(--border)"><th style="padding:6px 8px;text-align:left">Card</th><th style="padding:6px 8px;text-align:left">Astrology</th><th style="padding:6px 8px;text-align:left">Symbolism</th></tr>
        <tr><td style="padding:6px 8px;font-weight:600">The Fool</td><td style="padding:6px 8px">Uranus / ♒ Aquarius</td><td style="padding:6px 8px">Divine madness, liberation, the free spirit</td></tr>
        <tr><td style="padding:6px 8px;font-weight:600">The Magician</td><td style="padding:6px 8px">Mercury / ♊ Gemini</td><td style="padding:6px 8px">Will, skill, the alchemist</td></tr>
        <tr><td style="padding:6px 8px;font-weight:600">The High Priestess</td><td style="padding:6px 8px">Moon / ♋ Cancer</td><td style="padding:6px 8px">Intuition, mystery, the subconscious</td></tr>
        <tr><td style="padding:6px 8px;font-weight:600">The Empress</td><td style="padding:6px 8px">Venus / ♉ Taurus</td><td style="padding:6px 8px">Nature, abundance, the sensual world</td></tr>
        <tr><td style="padding:6px 8px;font-weight:600">The Emperor</td><td style="padding:6px 8px">Aries / ♈ Aries</td><td style="padding:6px 8px">Authority, structure, the father</td></tr>
        <tr><td style="padding:6px 8px;font-weight:600">The Hierophant</td><td style="padding:6px 8px">Jupiter / ♐ Sagittarius</td><td style="padding:6px 8px">Tradition, wisdom, the teacher</td></tr>
        <tr><td style="padding:6px 8px;font-weight:600">The Lovers</td><td style="padding:6px 8px">Venus / ♎ Libra</td><td style="padding:6px 8px">Union, choice, the heart's truth</td></tr>
        <tr><td style="padding:6px 8px;font-weight:600">The Chariot</td><td style="padding:6px 8px">Moon / ♋ Cancer</td><td style="padding:6px 8px">Willpower, victory, the warrior</td></tr>
        <tr><td style="padding:6px 8px;font-weight:600">Strength</td><td style="padding:6px 8px">Sun / ♌ Leo</td><td style="padding:6px 8px">Courage, inner strength, the heart</td></tr>
        <tr><td style="padding:6px 8px;font-weight:600">The Hermit</td><td style="padding:6px 8px">Saturn / ♍ Virgo</td><td style="padding:6px 8px">Solitude, wisdom, the seeker</td></tr>
        <tr><td style="padding:6px 8px;font-weight:600">Wheel of Fortune</td><td style="padding:6px 8px">Jupiter / ♐ Sagittarius</td><td style="padding:6px 8px">Destiny, cycles, fortune</td></tr>
        <tr><td style="padding:6px 8px;font-weight:600">Justice</td><td style="padding:6px 8px">Venus / ♎ Libra</td><td style="padding:6px 8px">Karma, fairness, truth</td></tr>
        <tr><td style="padding:6px 8px;font-weight:600">The Hanged Man</td><td style="padding:6px 8px">Neptune / ♓ Pisces</td><td style="padding:6px 8px">Surrender, suspension, new vision</td></tr>
        <tr><td style="padding:6px 8px;font-weight:600">Death</td><td style="padding:6px 8px">Pluto / ♏ Scorpio</td><td style="padding:6px 8px">Transformation, release, the phoenix</td></tr>
        <tr><td style="padding:6px 8px;font-weight:600">Temperance</td><td style="padding:6px 8px">Jupiter / ♐ Sagittarius</td><td style="padding:6px 8px">Alchemy, balance, synthesis</td></tr>
        <tr><td style="padding:6px 8px;font-weight:600">The Devil</td><td style="padding:6px 8px">Saturn / ♑ Capricorn</td><td style="padding:6px 8px">Shadow, attachment, materialism</td></tr>
        <tr><td style="padding:6px 8px;font-weight:600">The Tower</td><td style="padding:6px 8px">Mars / ♈ Aries</td><td style="padding:6px 8px">Upheaval, breakthrough, destruction</td></tr>
        <tr><td style="padding:6px 8px;font-weight:600">The Star</td><td style="padding:6px 8px">Aquarius / ♒ Aquarius</td><td style="padding:6px 8px">Hope, inspiration, healing</td></tr>
        <tr><td style="padding:6px 8px;font-weight:600">The Moon</td><td style="padding:6px 8px">Pisces / ♓ Pisces</td><td style="padding:6px 8px">Illusion, dreams, the subconscious</td></tr>
        <tr><td style="padding:6px 8px;font-weight:600">The Sun</td><td style="padding:6px 8px">Sun / ♌ Leo</td><td style="padding:6px 8px">Joy, vitality, enlightenment</td></tr>
        <tr><td style="padding:6px 8px;font-weight:600">Judgement</td><td style="padding:6px 8px">Pluto / ♏ Scorpio</td><td style="padding:6px 8px">Rebirth, calling, awakening</td></tr>
        <tr><td style="padding:6px 8px;font-weight:600">The World</td><td style="padding:6px 8px">Saturn / ♑ Capricorn</td><td style="padding:6px 8px">Completion, mastery, the cosmic dance</td></tr>
      </table>
      <p><strong>Suit Elements:</strong> 🪄 Wands = Fire (♈ ♌ ♐) · 🏆 Cups = Water (♋ ♏ ♓) · ⚔️ Swords = Air (♊ ♎ ♒) · 🪙 Pentacles = Earth (♉ ♍ ♑)</p>
      <p><strong>Court Cards:</strong> Page (Earth of suit) · Knight (Fire of suit) · Queen (Water of suit) · King (Air of suit)</p>
    </div>
  </details>

  <!-- ═══════ Court Cards ═══════ -->
  <details class="tarot-learn-section">
    <summary class="tarot-learn-summary">👑 The Court Cards — Pages, Knights, Queens, Kings</summary>
    <div class="tarot-learn-body">
      <p>The 16 court cards represent people, personality types, or aspects of yourself. Each court card combines its rank element and suit element.</p>
      <table style="width:100%;border-collapse:collapse;font-size:13px;margin-bottom:12px">
        <tr style="color:var(--gold);border-bottom:1px solid var(--border)"><th style="padding:6px 8px;text-align:left">Rank</th><th style="padding:6px 8px;text-align:left">Element</th><th style="padding:6px 8px;text-align:left">Meaning</th></tr>
        <tr><td style="padding:6px 8px;font-weight:600">Page</td><td style="padding:6px 8px">🌍 Earth</td><td style="padding:6px 8px">Youth, messenger, student, new beginnings. The spark of curiosity.</td></tr>
        <tr><td style="padding:6px 8px;font-weight:600">Knight</td><td style="padding:6px 8px">🔥 Fire</td><td style="padding:6px 8px">Action, adventure, pursuit. Charging toward a goal with passion.</td></tr>
        <tr><td style="padding:6px 8px;font-weight:600">Queen</td><td style="padding:6px 8px">💧 Water</td><td style="padding:6px 8px">Nurturing, emotional depth, inner mastery. The receptive leader.</td></tr>
        <tr><td style="padding:6px 8px;font-weight:600">King</td><td style="padding:6px 8px">💨 Air</td><td style="padding:6px 8px">Authority, mastery, leadership. The mature expression of the suit.</td></tr>
      </table>
      <p><strong>Example — Queen of Cups:</strong> Water of Water — The most emotionally intuitive and nurturing card. Deep empathy, psychic awareness, compassionate leadership.</p>
      <p><strong>Example — Knight of Wands:</strong> Fire of Fire — Pure passionate action. Adventurous, impulsive, charismatic. The energy of a bold new venture.</p>
    </div>
  </details>

  <!-- ═══════ Numbers in Tarot ═══════ -->
  <details class="tarot-learn-section">
    <summary class="tarot-learn-summary">🔢 Numbers in Tarot — The Power of Numerological Meaning</summary>
    <div class="tarot-learn-body">
      <p>Each numbered card (Ace through 10) in the Minor Arcana carries numerological significance that combines with its suit element.</p>
      <table style="width:100%;border-collapse:collapse;font-size:13px;margin-bottom:12px">
        <tr style="color:var(--gold);border-bottom:1px solid var(--border)"><th style="padding:6px 8px;text-align:left">Number</th><th style="padding:6px 8px;text-align:left">Meaning</th><th style="padding:6px 8px;text-align:left">In Wands (Fire)</th><th style="padding:6px 8px;text-align:left">In Cups (Water)</th></tr>
        <tr><td style="padding:6px 8px;font-weight:600">Ace (1)</td><td style="padding:6px 8px">Beginning, seed, pure potential</td><td style="padding:6px 8px">Creative spark</td><td style="padding:6px 8px">Love's beginning</td></tr>
        <tr><td style="padding:6px 8px;font-weight:600">2</td><td style="padding:6px 8px">Duality, balance, choice</td><td style="padding:6px 8px">Planning, future vision</td><td style="padding:6px 8px">Union, connection</td></tr>
        <tr><td style="padding:6px 8px;font-weight:600">3</td><td style="padding:6px 8px">Growth, expansion, collaboration</td><td style="padding:6px 8px">Expansion, exploration</td><td style="padding:6px 8px">Celebration, friendship</td></tr>
        <tr><td style="padding:6px 8px;font-weight:600">4</td><td style="padding:6px 8px">Stability, structure, foundation</td><td style="padding:6px 8px">Celebration, completion</td><td style="padding:6px 8px">Meditation, contemplation</td></tr>
        <tr><td style="padding:6px 8px;font-weight:600">5</td><td style="padding:6px 8px">Conflict, change, disruption</td><td style="padding:6px 8px">Competition, challenge</td><td style="padding:6px 8px">Loss, grief, regret</td></tr>
        <tr><td style="padding:6px 8px;font-weight:600">6</td><td style="padding:6px 8px">Harmony, balance, cooperation</td><td style="padding:6px 8px">Success, recognition</td><td style="padding:6px 8px">Nostalgia, memories</td></tr>
        <tr><td style="padding:6px 8px;font-weight:600">7</td><td style="padding:6px 8px">Spirituality, assessment, challenge</td><td style="padding:6px 8px">Competition, standing ground</td><td style="padding:6px 8px">Illusion, fantasy, choices</td></tr>
        <tr><td style="padding:6px 8px;font-weight:600">8</td><td style="padding:6px 8px">Power, movement, progress</td><td style="padding:6px 8px">Speed, momentum, action</td><td style="padding:6px 8px">Retreat, searching, walking away</td></tr>
        <tr><td style="padding:6px 8px;font-weight:600">9</td><td style="padding:6px 8px">Completion before the end, wisdom</td><td style="padding:6px 8px">Resilience, perseverance</td><td style="padding:6px 8px">Contentment, wishes fulfilled</td></tr>
        <tr><td style="padding:6px 8px;font-weight:600">10</td><td style="padding:6px 8px">Endings, cycles, culmination</td><td style="padding:6px 8px">Burden, overwhelm, responsibility</td><td style="padding:6px 8px">Divine love, completion, harmony</td></tr>
      </table>
    </div>
  </details>

  <!-- ═══════ Expanded Spreads Guide ═══════ -->
  <details class="tarot-learn-section">
    <summary class="tarot-learn-summary">🔮 Spread Guide — Position Meanings for Every Spread</summary>
    <div class="tarot-learn-body">
      <p>Each spread position has its own meaning. Understanding the position's energy transforms a card draw into a meaningful conversation.</p>

      <h4 style="color:var(--gold);margin:16px 0 8px">📖 One Card Draw</h4>
      <p>The simplest and most powerful spread. The single card speaks directly to your question or the energy of the day. Ideal for: <em>daily guidance, morning focus, quick answers.</em></p>

      <h4 style="color:var(--gold);margin:16px 0 8px">⏳ Three Card — Past · Present · Future</h4>
      <p><strong>Past:</strong> The energy or events leading to your current situation. Lessons carried forward. <strong>Present:</strong> Your current energy, focus, or challenge. What's most alive right now. <strong>Future:</strong> The trajectory you're on. Not fixed — a warning or encouragement.</p>
      <p><em>Variations:</em> Mind · Body · Spirit · Situation · Action · Outcome · You · Path · Potential</p>

      <h4 style="color:var(--gold);margin:16px 0 8px">✚ Cross of Intent (5 Cards)</h4>
      <p><strong>1 — Self:</strong> Your current state, the energy you bring. <strong>2 — Challenge:</strong> What stands in your way or needs attention. <strong>3 — Past:</strong> What shaped this situation. <strong>4 — Future:</strong> Where things are heading. <strong>5 — Outcome:</strong> The potential resolution or guidance.</p>

      <h4 style="color:var(--gold);margin:16px 0 8px">☸ Celtic Cross (10 Cards)</h4>
      <p><strong>1 — Self:</strong> The heart of the matter. Your current state. <strong>2 — Challenge:</strong> What crosses you — the obstacle. <strong>3 — Past:</strong> Foundation behind the situation. <strong>4 — Future:</strong> What's approaching or unfolding. <strong>5 — Above:</strong> Conscious goals, aspirations. <strong>6 — Below:</strong> Subconscious influences, hidden factors. <strong>7 — Advice:</strong> Your perspective, the inner voice. <strong>8 — External:</strong> How others see you or external forces. <strong>9 — Hopes & Fears:</strong> What you hope for and what you fear. <strong>10 — Outcome:</strong> The synthesis — the final message.</p>
    </div>
  </details>

  <!-- ═══════ Reversals ═══════ -->
  <details class="tarot-learn-section">
    <summary class="tarot-learn-summary">🔄 Reading Reversals — Deeper Meaning Through Upside-Down Cards</summary>
    <div class="tarot-learn-body">
      <p>A reversed card (drawn upside-down) doesn't mean "bad" — it means <strong>blocked, internalised, or shadow energy</strong>. Some readers use reversals exclusively; others don't. Both are valid.</p>
      <p><strong>Common reversal themes:</strong></p>
      <p>✨ <strong>Blocked energy</strong> — The card's upright quality is present but obstructed or delayed.</p>
      <p>✨ <strong>Internalised energy</strong> — The card speaks to your inner world rather than external action.</p>
      <p>✨ <strong>Shadow aspect</strong> — The card's quality is manifesting in an unbalanced or excessive way.</p>
      <p>✨ <strong>Integration needed</strong> — You're being called to integrate the card's lesson more fully.</p>
      <p><em>Example — The Star reversed:</em> Not lack of hope, but struggling to believe in hope. A call to heal old wounds that block trust in the universe.</p>
    </div>
  </details>

  <!-- ═══════ Tips for Readings ═══════ -->
  <details class="tarot-learn-section">
    <summary class="tarot-learn-summary">💜 Reading Tips — Deepening Your Practice</summary>
    <div class="tarot-learn-body">
      <p>✨ <strong>Create sacred space.</strong> Light a candle, breathe deeply, set an intention before drawing cards. The energy you bring shapes the reading.</p>
      <p>✨ <strong>Ask better questions.</strong> "What do I need to know about..." opens more than "Will X happen?" Open-ended questions invite the cards to speak freely.</p>
      <p>✨ <strong>Trust your intuition.</strong> Card meanings are anchors, not prison cells. If a card's imagery speaks to you differently in a reading, honour that.</p>
      <p>✨ <strong>Study the RWS imagery.</strong> Pamela Colman Smith packed every card with symbols — colours, gestures, numbers, plants, animals. These details carry meaning.</p>
      <p>✨ <strong>Keep a journal.</strong> Record your readings, the cards drawn, your interpretations, and what actually happened. Patterns will emerge over time.</p>
      <p>✨ <strong>Learn one card deeply each day.</strong> Pull a card in the morning, study its symbolism, notice where it appears in your life. 78 days = mastery.</p>
      <p>✨ <strong>Read for yourself first.</strong> The best readers know themselves. Practice self-readings before reading for others.</p>
      <p>✨ <strong>Cleanse your deck.</strong> Moonlight, crystals, intention, or simply knocking on the deck. Clear energy between readings.</p>
    </div>
  </details>

  <!-- ═══════ RWS Symbolism Guide ═══════ -->
  <details class="tarot-learn-section">
    <summary class="tarot-learn-summary">🎨 RWS Symbolism — Pamela Colman Smith's Visual Language</summary>
    <div class="tarot-learn-body">
      <p>Pamela Colman Smith (known as Pixie) was a brilliant artist who packed every RWS card with layers of meaning. Here are some recurring symbols:</p>
      <p><strong>🌹 Rose & Lily</strong> — Purity and passion. The white lily and red rose appear in The Magician, Strength, and Death.</p>
      <p><strong>🏔️ Mountains</strong> — Challenges, spiritual aspiration, obstacles to overcome. Distant peaks in The Fool, The Hermit, and many others.</p>
      <p><strong>🌊 Water</strong> — Emotions, the subconscious, the flow of life. Rivers, oceans, and cups filled with water.</p>
      <p><strong>☀️ Sunflowers</strong> — Joy, vitality, spiritual illumination. The Sun card, The Empress's crown, The World's garland.</p>
      <p><strong>🔮 Crystal</strong> — Clarity, focus, spiritual power. The Magician's tools, the crystal in The High Priestess's crown.</p>
      <p><strong>🐍 Snake</strong> — Transformation, kundalini energy, wisdom. The serpent belt on The Magician, the ouroboros of cycles.</p>
      <p><strong>📐 Cube & Cross</strong> — Material stability meeting spiritual aspiration. Found in The Hierophant, The World, and The Devil's pedestal.</p>
      <p><strong>⭐ Eight-pointed stars</strong> — Venus, love, harmony, spiritual beauty. The Star card, the Empress's crown, The World's constellation.</p>
      <p>Every detail in the RWS deck — from the direction a figure faces to the colour of their robes — was chosen with intention. Study the imagery, and the cards will speak more deeply with each reading.</p>
    </div>
  </details>`;

  // Render the card index grid after content is in the DOM
  setTimeout(() => tarotLearnRenderGrid('all'), 50);
}

// ═══════ Learn Tarot — Card Index Helpers ═══════
function tarotLearnRenderGrid(filter) {
  const grid = document.getElementById('tarot-learn-grid');
  if(!grid) return;
  const allCards = (window._tarotData?.cards||[]).filter(c => filter==='all' || c.suit===filter);
  grid.innerHTML = '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:8px">' +
    allCards.map(c => `<div class="tarot-library-card" data-suit="${c.suit}"
      onclick="tarotLearnShowCard('${esc(c.name)}')"
      style="background:var(--bg-glass);border:1px solid var(--border);border-radius:8px;padding:8px;cursor:pointer;text-align:center;transition:all 0.2s"
      onmouseover="this.style.borderColor='var(--gold)';this.style.background='var(--bg-card-hover)'"
      onmouseout="this.style.borderColor='var(--border)';this.style.background='var(--bg-glass)'">
      <div style="font-size:24px;margin-bottom:4px">${c.suit==='major'?'⭐':c.suit==='wands'?'🪄':c.suit==='cups'?'🏆':c.suit==='swords'?'⚔️':'🪙'}</div>
      <div style="font-size:11px;font-weight:600;color:var(--text-primary)">${c.name}</div>
      <div style="font-size:9px;color:var(--text-muted);margin-top:2px">${(c.keywords||[]).slice(0,2).join(', ')}</div>
    </div>`).join('') + '</div>';
}

function tarotLearnFilter(filter, btn) {
  document.querySelectorAll('.tarot-learn-filters .tarot-filter-btn').forEach(b=>b.classList.remove('active'));
  if(btn) btn.classList.add('active');
  tarotLearnRenderGrid(filter);
}

function tarotLearnSearch(input) {
  const q = input.value.toLowerCase().trim();
  const allCards = window._tarotData?.cards||[];
  if(!q) { tarotLearnRenderGrid('all'); return; }
  const matches = allCards.filter(c =>
    c.name.toLowerCase().includes(q) ||
    (c.keywords||[]).some(k=>k.toLowerCase().includes(q)) ||
    (c.upright||'').toLowerCase().includes(q)
  );
  const grid = document.getElementById('tarot-learn-grid');
  if(!grid) return;
  grid.innerHTML = matches.length===0
    ? '<div style="color:var(--text-muted);padding:20px;text-align:center">No cards match that search</div>'
    : '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:8px">' +
      matches.map(c => `<div class="tarot-library-card" data-suit="${c.suit}"
        onclick="tarotLearnShowCard('${esc(c.name)}')"
        style="background:var(--bg-glass);border:1px solid var(--border);border-radius:8px;padding:8px;cursor:pointer;text-align:center"
        onmouseover="this.style.borderColor='var(--gold)'" onmouseout="this.style.borderColor='var(--border)'">
        <div style="font-size:24px;margin-bottom:4px">${c.suit==='major'?'⭐':c.suit==='wands'?'🪄':c.suit==='cups'?'🏆':c.suit==='swords'?'⚔️':'🪙'}</div>
        <div style="font-size:11px;font-weight:600;color:var(--text-primary)">${c.name}</div>
      </div>`).join('') + '</div>';
}

function tarotLearnShowCard(name) {
  const card = (window._tarotData?.cards||[]).find(c=>c.name===name);
  if(!card) return;
  const overlay = document.getElementById('tarot-card-detail');
  const body = document.getElementById('tarot-card-detail-body');
  if(!overlay||!body) return;
  body.innerHTML = `<div class="tarot-detail-layout">
    <div class="tarot-detail-image">${tarotCardFace(card)}</div>
    <div class="tarot-detail-info">
      <h2 class="tarot-detail-name">${card.name}</h2>
      <div class="tarot-detail-suit">${card.suit==='major'?'⭐ Major Arcana':card.suit.charAt(0).toUpperCase()+card.suit.slice(1)}</div>
      <div class="tarot-detail-keywords">${(card.keywords||[]).join(' · ')}</div>
      <div class="tarot-detail-section"><strong>Upright:</strong> ${card.upright||card.upright_meaning||'—'}</div>
      <div class="tarot-detail-section"><strong>Reversed:</strong> ${card.reversed||card.reversed_meaning||card.meaning_rev||'Consider the blocked or internal aspect of this card\'s energy.'}</div>
      <div class="tarot-detail-daily"><em>✨ Daily Message:</em> ${card.daily||card.daily_message||'—'}</div>
    </div>
  </div>`;
  overlay.style.display = 'flex';
}

