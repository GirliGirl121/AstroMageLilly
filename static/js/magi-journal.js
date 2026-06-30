function magiFormatDate(d) {
  const y = d.getFullYear(), m = String(d.getMonth()+1).padStart(2,'0'), day = String(d.getDate()).padStart(2,'0');
  return `${y}-${m}-${day}`;
}

function magiDayName(d) {
  return ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'][d.getDay()];
}

function magiMonthName(m) {
  return ['January','February','March','April','May','June','July','August','September','October','November','December'][m];
}

async function magiLoadDay(dateStr) {
  try {
    const data = await loadJSON(`/api/diary/day?date=${dateStr}`);
    // Update display
    const d = new Date(dateStr+'T12:00:00');
    document.getElementById('magi-day-name').textContent = magiDayName(d);
    document.getElementById('magi-day-date').textContent = dateStr;
    document.getElementById('magi-date-input').value = dateStr;

    // Astro bar — full MagiJournal desktop feature parity
    const astro = data.astro || {};
    const ab = document.getElementById('magi-astro-bar');
    // Planetary hours with spirits
    let phHtml = '';
    (astro.planetary_hours||[]).forEach(function(h){
      var sym = PLANET_SYMBOLS[h.planet]||'';
      var col = PLANET_COLORS[h.planet]||'#fff';
      phHtml += '<span class="magi-hour-pill" style="border-color:'+col+'"><span style="color:'+col+'">'+sym+'</span> '+(h.planet||'')+' <small>'+(h.spendant_name||h.spirit_name||'')+'</small></span>';
    });
    // Recommendations
    var recs = (astro.recommendations||[]).slice(0,5);
    var avoids = (astro.avoid||[]).slice(0,5);
    // Picatrix refs
    var refs = (astro.picatrix_references||[]).slice(0,4);
    var elections = (astro.elections||[]).slice(0,3);
    ab.innerHTML = '<div class="magi-astro-grid">' +
      '<div class="magi-astro-main">' +
        '<div class="magi-astro-row"><span class="magi-astro-label">Day Ruler:</span> <strong>'+(astro.day_ruler||'—')+'</strong> '+(astro.day_ruler_ar||'')+'</div>' +
        '<div class="magi-astro-row"><span class="magi-astro-label">Moon:</span> <strong>'+(astro.moon_sign||'—')+'</strong> &middot; Mansion <strong>'+(astro.moon_mansion||'—')+'</strong> #'+(astro.mansion_index>=0?astro.mansion_index+1:'—')+'</div>' +
        '<div class="magi-astro-row"><span class="magi-astro-label">Spirit:</span> <strong>'+(astro.mansion_spirit_name||astro.mansion_spirit||'—')+'</strong> '+(astro.mansion_spirit_arabic||'')+'</div>' +
        '<div class="magi-astro-row"><span class="magi-astro-label">Nature:</span> <strong>'+(astro.mansion_nature||'—')+'</strong></div>' +
      '</div>' +
      '<div class="magi-astro-side">' +
        (recs.length ? '<div class="magi-astro-recs"><span class="magi-astro-label green">✓ Recommended</span>'+recs.map(function(r){return '<div class="magi-rec-item">• '+r+'</div>';}).join('')+'</div>' : '') +
        (avoids.length ? '<div class="magi-astro-avoids"><span class="magi-astro-label red">✗ Avoid</span>'+avoids.map(function(a){return '<div class="magi-avoid-item">• '+a+'</div>';}).join('')+'</div>' : '') +
      '</div>' +
    '</div>' +
    (phHtml ? '<div class="magi-astro-hours">' + phHtml + '</div>' : '') +
    (elections.length ? '<div class="magi-astro-elections"><span class="magi-astro-label">⚡ Elections:</span> '+elections.map(function(e){return '<span class="magi-election-pill">'+(e.category||e.rating||'').replace(/_/g,' ')+': '+(e.operation||'').substring(0,60)+'</span>';}).join(' ') + '</div>' : '') +
    (refs.length ? '<div class="magi-astro-refs"><span class="magi-astro-label">📜 Picatrix:</span> <small>'+refs.join(' &middot; ')+'</small></div>' : '');

    // Diary
    const diary = data.diary;
    const ta = document.getElementById('magi-diary-text');
    ta.value = diary ? diary.content : '';

    // Tasks
    magiRenderTasks(data.tasks || []);

    // Dreams
    const dream = data.dreams;
    document.getElementById('magi-dream-text').value = dream ? dream.content : '';

    // Bookmark/Favorite
    const bmBtn = document.getElementById('magi-bookmark-btn');
    bmBtn.textContent = data.is_bookmarked ? '★ Bookmarked' : '☆ Bookmark';
    bmBtn.dataset.bookmarked = data.is_bookmarked ? 'true' : 'false';
    const fvBtn = document.getElementById('magi-favorite-btn');
    fvBtn.textContent = data.is_favorited ? '♥ Favorited' : '♡ Favorite';
    fvBtn.dataset.favorited = data.is_favorited ? 'true' : 'false';

    // Month calendar
    magiRenderMonth(d.getFullYear(), d.getMonth()+1, parseInt(dateStr.split('-')[2]));

    // Bookmarks/favorites counts
    magiLoadCounts();
  } catch(e) {
    console.error('Magi load error:', e);
  }
}

function magiRenderTasks(tasks) {
  const list = document.getElementById('magi-task-list');
  if (!tasks.length) {
    list.innerHTML = '<div class="magi-empty">No tasks for this day ✨</div>';
    return;
  }
  list.innerHTML = tasks.map(t => `
    <div class="magi-task-item ${t.done ? 'done' : ''}">
      <input type="checkbox" ${t.done ? 'checked' : ''} data-id="${t.id}" class="magi-task-cb">
      <span class="magi-task-text">${esc(t.text)}</span>
      <button class="magi-task-del" data-id="${t.id}">✕</button>
    </div>
  `).join('');
  // Bind events
  list.querySelectorAll('.magi-task-cb').forEach(cb => {
    cb.addEventListener('change', async () => {
      await loadJSON('/api/diary/task/toggle', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({id: parseInt(cb.dataset.id)})});
      magiLoadDay(document.getElementById('magi-date-input').value);
    });
  });
  list.querySelectorAll('.magi-task-del').forEach(btn => {
    btn.addEventListener('click', async () => {
      await loadJSON('/api/diary/task/delete', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({id: parseInt(btn.dataset.id)})});
      magiLoadDay(document.getElementById('magi-date-input').value);
    });
  });
}

async function magiRenderMonth(year, month, activeDay) {
  document.getElementById('magi-month-title').textContent = `${magiMonthName(month-1)} ${year}`;
  try {
    const data = await loadJSON(`/api/diary/month?year=${year}&month=${month}`);
    const days = data.days || [];
    const grid = document.getElementById('magi-cal-grid');
    const firstDay = new Date(year, month-1, 1).getDay(); // 0=Sun
    const daysInMonth = new Date(year, month, 0).getDate();
    // Convert to Mon-start
    let startOffset = firstDay === 0 ? 6 : firstDay - 1;
    let html = '';
    for(let i=0; i<startOffset; i++) html += '<div class="magi-cal-empty"></div>';
    for(let d=1; d<=daysInMonth; d++) {
      const dateStr = `${year}-${String(month).padStart(2,'0')}-${String(d).padStart(2,'0')}`;
      const dayInfo = days.find(dd => dd.day === d);
      const isActive = d === activeDay;
      const hasDiary = dayInfo && dayInfo.moon_mansion;
      html += `<div class="magi-cal-day ${isActive ? 'active' : ''} ${dayInfo ? 'has-data' : ''}"
                   data-date="${dateStr}" onclick="magiGoToDate('${dateStr}')">
        <span class="magi-cal-num">${d}</span>
        ${dayInfo ? `<span class="magi-cal-icon">${dayInfo.moon_sign||''}</span>` : ''}
      </div>`;
    }
    grid.innerHTML = html;
  } catch(e) {
    document.getElementById('magi-cal-grid').innerHTML = '<div class="magi-empty">Could not load calendar</div>';
  }
}

function magiGoToDate(dateStr) {
  magiLoadDay(dateStr);
}

async function magiLoadCounts() {
  try {
    const bm = await loadJSON('/api/diary/bookmarks');
    document.getElementById('magi-bm-count').textContent = bm.length;
    const fv = await loadJSON('/api/diary/favorites');
    document.getElementById('magi-fav-count').textContent = fv.length;
  } catch(e) {}
}

// ══════════ MagiJournal Event Bindings ══════════
document.addEventListener('DOMContentLoaded', () => {
  // Day navigation
  document.getElementById('magi-prev-day').addEventListener('click', () => {
    const d = new Date(document.getElementById('magi-date-input').value+'T12:00:00');
    d.setDate(d.getDate()-1);
    magiLoadDay(magiFormatDate(d));
  });
  document.getElementById('magi-next-day').addEventListener('click', () => {
    const d = new Date(document.getElementById('magi-date-input').value+'T12:00:00');
    d.setDate(d.getDate()+1);
    magiLoadDay(magiFormatDate(d));
  });
  document.getElementById('magi-today-btn').addEventListener('click', () => {
    magiLoadDay(magiFormatDate(new Date()));
  });
  document.getElementById('magi-date-input').addEventListener('change', function() {
    magiLoadDay(this.value);
  });

  // Month navigation
  document.getElementById('magi-prev-month').addEventListener('click', () => {
    const current = document.getElementById('magi-month-title').textContent;
    const d = new Date(document.getElementById('magi-date-input').value+'T12:00:00');
    d.setMonth(d.getMonth()-1);
    const dateStr = magiFormatDate(d);
    magiLoadDay(dateStr);
  });
  document.getElementById('magi-next-month').addEventListener('click', () => {
    const d = new Date(document.getElementById('magi-date-input').value+'T12:00:00');
    d.setMonth(d.getMonth()+1);
    const dateStr = magiFormatDate(d);
    magiLoadDay(dateStr);
  });

  // Tab switching inside MagiJournal (Diary/Tasks/Dreams sub-tabs)
  document.querySelectorAll('.magi-tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.magi-tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.magi-tab-content').forEach(t => t.classList.remove('active'));
      btn.classList.add('active');
      const tab = document.getElementById('magi-tab-'+btn.dataset.magiTab);
      if(tab) tab.classList.add('active');
    });
  });

  // View switching (Day/Week/Year/Search)
  document.querySelectorAll('.magi-view-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.magi-view-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      var view = btn.dataset.magiView;
      document.querySelectorAll('.magi-view').forEach(v => v.style.display = 'none');
      var viewEl = document.getElementById('magi-view-'+view);
      if(viewEl) viewEl.style.display = 'block';
      if(view === 'week') magiRenderWeek();
      if(view === 'year') magiRenderYear();
    });
  });

  // Auto-save diary on typing (debounced)
  document.getElementById('magi-diary-text').addEventListener('input', () => {
    clearTimeout(magiAutoSave);
    magiAutoSave = setTimeout(async () => {
      const dateStr = document.getElementById('magi-date-input').value;
      const content = document.getElementById('magi-diary-text').value;
      await loadJSON('/api/diary/save', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({date: dateStr, content: content})});
      const status = document.getElementById('magi-saved-status');
      status.textContent = '✨ Saved';
      setTimeout(() => { status.textContent = ''; }, 2000);
    }, 800);
  });

  // Bookmark
  document.getElementById('magi-bookmark-btn').addEventListener('click', async () => {
    const dateStr = document.getElementById('magi-date-input').value;
    const res = await loadJSON('/api/diary/bookmark/toggle', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({date: dateStr})});
    magiLoadDay(dateStr);
  });

  // Favorite
  document.getElementById('magi-favorite-btn').addEventListener('click', async () => {
    const dateStr = document.getElementById('magi-date-input').value;
    const res = await loadJSON('/api/diary/favorite/toggle', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({date: dateStr})});
    magiLoadDay(dateStr);
  });

  // Add task
  document.getElementById('magi-task-add').addEventListener('click', async () => {
    const input = document.getElementById('magi-task-input');
    const text = input.value.trim();
    if(!text) return;
    input.value = '';
    const dateStr = document.getElementById('magi-date-input').value;
    await loadJSON('/api/diary/task/add', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({date: dateStr, text: text})});
    magiLoadDay(dateStr);
  });
  document.getElementById('magi-task-input').addEventListener('keydown', e => {
    if(e.key === 'Enter') document.getElementById('magi-task-add').click();
  });

  // Dream save (auto-save)
  document.getElementById('magi-dream-text').addEventListener('input', () => {
    clearTimeout(magiAutoSave);
    magiAutoSave = setTimeout(async () => {
      const dateStr = document.getElementById('magi-date-input').value;
      const content = document.getElementById('magi-dream-text').value;
      await loadJSON('/api/diary/dream/save', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({date: dateStr, content: content})});
    }, 800);
  });

  // Search
  document.getElementById('magi-search-btn').addEventListener('click', async () => {
    const q = document.getElementById('magi-search-input').value.trim();
    if(!q) return;
    const results = await loadJSON(`/api/diary/search?q=${encodeURIComponent(q)}`);
    const container = document.getElementById('magi-search-results');
    const r = results.results || {};
    let html = '';
    if(r.diary) html += `<div class="magi-sr-group"><div class="magi-sr-label">📝 Diary</div>${r.diary.map(e => `<div class="magi-sr-item" onclick="magiGoToDate('${e.date}')"><span class="magi-sr-date">${e.date}</span> ${esc(e.content.slice(0,80))}${e.content.length>80?'…':''}</div>`).join('')}</div>`;
    if(r.tasks) html += `<div class="magi-sr-group"><div class="magi-sr-label">☑ Tasks</div>${r.tasks.map(t => `<div class="magi-sr-item" onclick="magiGoToDate('${t.date}')"><span class="magi-sr-date">${t.date}</span> ${esc(t.text)}</div>`).join('')}</div>`;
    if(r.dreams) html += `<div class="magi-sr-group"><div class="magi-sr-label">🌙 Dreams</div>${r.dreams.map(d => `<div class="magi-sr-item" onclick="magiGoToDate('${d.date}')"><span class="magi-sr-date">${d.date}</span> ${esc(d.content.slice(0,80))}${d.content.length>80?'…':''}</div>`).join('')}</div>`;
    if(!html) html = '<div class="magi-empty">No results found</div>';
    container.innerHTML = html;
  });
  document.getElementById('magi-search-input').addEventListener('keydown', e => {
    if(e.key === 'Enter') document.getElementById('magi-search-btn').click();
  });

  // Bookmarks popup
  document.getElementById('magi-show-bookmarks').addEventListener('click', async () => {
    const bm = await loadJSON('/api/diary/bookmarks');
    const container = document.getElementById('magi-search-results');
    if(!bm.length) { container.innerHTML = '<div class="magi-empty">No bookmarks yet</div>'; return; }
    let html = '<div class="magi-sr-label">📌 Bookmarks</div>';
    for(const b of bm) {
      html += `<div class="magi-sr-item" onclick="magiGoToDate('${b.date}')">
        <span class="magi-sr-date">${b.date}</span> ${esc(b.note)}
        <button class="magi-sr-del" onclick="event.stopPropagation(); remBM(${b.id})">✕</button>
      </div>`;
    }
    container.innerHTML = html;
    // Switch to search tab
    document.querySelector('[data-magi-tab="search"]').click();
  });

  // Favorites popup
  document.getElementById('magi-show-favorites').addEventListener('click', async () => {
    const fv = await loadJSON('/api/diary/favorites');
    const container = document.getElementById('magi-search-results');
    if(!fv.length) { container.innerHTML = '<div class="magi-empty">No favorites yet</div>'; return; }
    let html = '<div class="magi-sr-label">♥ Favorites</div>';
    for(const f of fv) {
      html += `<div class="magi-sr-item" onclick="magiGoToDate('${f.date}')">
        <span class="magi-sr-date">${f.date}</span> ${esc(f.note)}
        <button class="magi-sr-del" onclick="event.stopPropagation(); remFV(${f.id})">✕</button>
      </div>`;
    }
    container.innerHTML = html;
    document.querySelector('[data-magi-tab="search"]').click();
  });

  // Load recent searches
  async function loadRecentSearches() {
    try {
      const hist = await loadJSON('/api/diary/search-history');
      const container = document.getElementById('magi-recent-searches');
      if(hist.length) {
        container.innerHTML = '<div class="magi-sr-label">Recent searches</div>' +
          hist.map(h => `<span class="magi-recent-tag" onclick="document.getElementById('magi-search-input').value='${esc(h.query)}'; document.getElementById('magi-search-btn').click();">${esc(h.query)}</span>`).join('');
      }
    } catch(e) {}
  }
  loadRecentSearches();

  // ═══ Week View ═══
  var magiWeekStart = new Date();
  magiWeekStart.setDate(magiWeekStart.getDate() - magiWeekStart.getDay()); // Monday
  function magiRenderWeek() {
    var start = new Date(magiWeekStart);
    var end = new Date(start); end.setDate(end.getDate() + 6);
    document.getElementById('magi-week-title').textContent = start.toLocaleDateString('en-US',{month:'short',day:'numeric'}) + ' — ' + end.toLocaleDateString('en-US',{month:'short',day:'numeric',year:'numeric'});
    var grid = document.getElementById('magi-week-grid');
    grid.innerHTML = '';
    for(var i = 0; i < 7; i++) {
      var d = new Date(start); d.setDate(d.getDate() + i);
      var dateStr = d.toISOString().split('T')[0];
      var dayName = d.toLocaleDateString('en-US',{weekday:'short'});
      var dayNum = d.getDate();
      var cell = document.createElement('div');
      cell.className = 'magi-week-day';
      cell.innerHTML = '<div class="magi-week-dayname">'+dayName+'</div><div class="magi-week-daynum">'+dayNum+'</div><div class="magi-week-moon" id="magi-week-moon-'+i+'">—</div><div class="magi-week-ruler" id="magi-week-ruler-'+i+'">—</div>';
      (function(idx, ds){
        cell.addEventListener('click', function(){ magiLoadDay(ds); document.querySelector('[data-magi-tab="diary"]').click(); });
        fetch('/api/diary/day?date='+ds).then(r=>r.json()).then(function(data){
          var astro = data.astro || {};
          var moonEl = document.getElementById('magi-week-moon-'+idx);
          var rulerEl = document.getElementById('magi-week-ruler-'+idx);
          if(moonEl) moonEl.textContent = '☽ '+(astro.moon_sign||'—').substring(0,3);
          if(rulerEl) rulerEl.textContent = (astro.day_ruler||'—').substring(0,3);
        }).catch(function(){});
      })(i, dateStr);
      grid.appendChild(cell);
    }
  }
  document.getElementById('magi-prev-week').addEventListener('click', function(){ magiWeekStart.setDate(magiWeekStart.getDate() - 7); magiRenderWeek(); });
  document.getElementById('magi-next-week').addEventListener('click', function(){ magiWeekStart.setDate(magiWeekStart.getDate() + 7); magiRenderWeek(); });

  // ═══ Year View ═══
  magiYear = new Date().getFullYear();
  function magiRenderYear() {
    document.getElementById('magi-year-title').textContent = magiYear;
    var grid = document.getElementById('magi-year-grid');
    grid.innerHTML = '';
    var monthNames = ['January','February','March','April','May','June','July','August','September','October','November','December'];
    for(var m = 0; m < 12; m++) {
      var card = document.createElement('div');
      card.className = 'magi-year-month';
      card.innerHTML = '<div class="magi-year-month-name">'+monthNames[m]+'</div><div class="magi-year-month-data" id="magi-year-month-'+m+'">Loading...</div>';
      (function(idx){
        fetch('/api/diary/month?year='+magiYear+'&month='+(idx+1)).then(r=>r.json()).then(function(data){
          var el = document.getElementById('magi-year-month-'+idx);
          if(data && data.length) {
            var totalAspects = 0;
            data.forEach(function(d){ totalAspects += (d.aspects||[]).length; });
            el.innerHTML = data.length+' days<br>'+totalAspects+' aspects';
          } else {
            el.innerHTML = '—';
          }
        }).catch(function(){});
      })(m);
      grid.appendChild(card);
    }
  }
  document.getElementById('magi-prev-year').addEventListener('click', function(){ magiYear--; magiRenderYear(); });
  document.getElementById('magi-next-year').addEventListener('click', function(){ magiYear++; magiRenderYear(); });

  // Init: load today
  magiLoadDay(magiFormatDate(new Date()));
  magiRenderWeek();
  magiRenderYear();

async function remBM(id) {
  await loadJSON('/api/diary/bookmark/remove', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({id})});
  document.getElementById('magi-show-bookmarks').click();
}

async function remFV(id) {
  await loadJSON('/api/diary/favorite/remove', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({id})});
  document.getElementById('magi-show-favorites').click();
}

// ══════════ NATAL CHART CRUD ══════════

