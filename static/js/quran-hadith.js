async function loadQuranFull() {
  const qc = document.getElementById('quran-full-content');
  try {
    const d = await loadJSON('/api/quran-hadith');
    // Fetch only page 1 of verses (20 verses) instead of the full 41MB
    const vp = await loadJSON('/api/quran/verses?page=1&per_page=20');

    let html = `<div class="sacred-book">
      <div class="book-bismillah">\u0628\u0650\u0633\u0652\u0645\u0650 \u0627\u0644\u0644\u064e\u0651\u0647\u0650 \u0627\u0644\u0631\u064e\u0651\u062d\u0652\u0645\u064e\u0646\u0650 \u0627\u0644\u0631\u064e\u0651\u062d\u0650\u064a\u0645\u0650</div>
      <div class="illuminated-verse">
        <div class="illumined-label">\u2726 Today's Illuminated Verse</div>
        <div class="illumined-arabic">${(d.quran||{}).arabic||''}</div>
        <div class="illumined-translation">${(d.quran||{}).translation||''}</div>
        <div class="illumined-ref">\u2014 ${(d.quran||{}).surahNameEn||''} (${(d.quran||{}).surah||''}:${(d.quran||{}).ayah||''})</div>
        ${(d.quran||{}).theme ? `<span class="illumined-theme">\u2726 ${(d.quran||{}).theme}</span>` : ''}
      </div>
      <div class="quran-scroll">
        <div class="quran-scroll-header">
          <h3 class="section-title">\ud83d\udcd6 Quran Verses</h3>
          <span class="verse-count">${vp.total} total &middot; showing ${vp.verses.length}</span>
        </div>
        <div class="quran-theme-filters">
          <button class="active" data-theme="all" onclick="filterQuran('all',this)">All</button>
          ${(vp.themes||[]).map(t => `<button data-theme="${esc(t)}" onclick="filterQuran('${esc(t)}',this)">${t}</button>`).join('')}
        </div>
        <div class="quran-ayat" id="quran-ayat-list">`;
    for(const v of (vp.verses||[])) {
      html += `<div class="quran-ayah" data-theme="${esc(v.theme||'')}">
        <div class="quran-ayah-number">${v.ayah}</div>
        <div class="quran-ayah-text">
          <div class="quran-ayah-arabic">${v.arabic}</div>
          <div class="quran-ayah-trans">${v.translation}</div>
          <div class="quran-ayah-ref">${v.surahNameEn} (${v.surah}:${v.ayah}) ${v.theme ? `<span class="quran-ayah-theme">${v.theme}</span>` : ''}</div>
        </div>
      </div>`; }
    // Page navigation
    if(vp.total_pages > 1) {
      html += `<div class="quran-pagination" id="quran-pagination">
        <button onclick="quranPage(1)" disabled>&#9664;&#9664;</button>
        <button onclick="quranPage(${vp.page-1})" ${vp.page <= 1 ? 'disabled' : ''}>&#9664;</button>
        <span>Page ${vp.page} of ${vp.total_pages}</span>
        <button onclick="quranPage(${vp.page+1})" ${vp.page >= vp.total_pages ? 'disabled' : ''}>&#9654;</button>
        <button onclick="quranPage(${vp.total_pages})" ${vp.page >= vp.total_pages ? 'disabled' : ''}>&#9654;&#9654;</button>
      </div>`;
    }
    html += `</div></div></div>`;
    qc.innerHTML = html;
  } catch(e) { qc.innerHTML = `<div class="loading">${e.message}</div>`; }
}

let quranCurrentPage = 1;
let quranCurrentFilter = 'all';

async function quranPage(page) {
  quranCurrentPage = page;
  const qc = document.getElementById('quran-full-content');
  try {
    const vp = await loadJSON(`/api/quran/verses?page=${page}&per_page=20`);
    let ayatHtml = '';
    for(const v of (vp.verses||[])) {
      const show = quranCurrentFilter === 'all' || v.theme === quranCurrentFilter;
      ayatHtml += `<div class="quran-ayah" data-theme="${esc(v.theme||'')}" style="${show ? '' : 'display:none'}">
        <div class="quran-ayah-number">${v.ayah}</div>
        <div class="quran-ayah-text">
          <div class="quran-ayah-arabic">${v.arabic}</div>
          <div class="quran-ayah-trans">${v.translation}</div>
          <div class="quran-ayah-ref">${v.surahNameEn} (${v.surah}:${v.ayah}) ${v.theme ? `<span class="quran-ayah-theme">${v.theme}</span>` : ''}</div>
        </div>
      </div>`;
    }
    document.getElementById('quran-ayat-list').innerHTML = ayatHtml;
    const pg = document.getElementById('quran-pagination');
    if(pg) {
      pg.innerHTML = `
        <button onclick="quranPage(1)" ${page <= 1 ? 'disabled' : ''}>&#9664;&#9664;</button>
        <button onclick="quranPage(${page-1})" ${page <= 1 ? 'disabled' : ''}>&#9664;</button>
        <span>Page ${page} of ${vp.total_pages}</span>
        <button onclick="quranPage(${page+1})" ${page >= vp.total_pages ? 'disabled' : ''}>&#9654;</button>
        <button onclick="quranPage(${vp.total_pages})" ${page >= vp.total_pages ? 'disabled' : ''}>&#9654;&#9654;</button>`;
    }
    // Re-apply filter
    if(quranCurrentFilter !== 'all') filterQuran(quranCurrentFilter, document.querySelector(`.quran-theme-filters button[data-theme="${quranCurrentFilter}"]`));
  } catch(e) { /* ignore */ }
}

function filterQuran(theme, btn) {
  quranCurrentFilter = theme;
  document.querySelectorAll('.quran-theme-filters button').forEach(b => b.classList.remove('active'));
  if(btn) btn.classList.add('active');
  document.querySelectorAll('.quran-ayah').forEach(el => {
    if(theme === 'all') { el.style.display = 'grid'; return; }
    el.style.display = (el.dataset.theme === theme) ? 'grid' : 'none';
  });
}

async function loadHadithFull() {
  const hc = document.getElementById('hadith-full-content');
  try {
    const d = await loadJSON('/api/quran-hadith');
    const books = await loadJSON('/api/hadith/books');
    // Load first book's narrations paginated
    const firstBook = (books||[])[0]?.bookName || '';
    const firstNar = firstBook ? await loadJSON(`/api/hadith/narrations?book=${encodeURIComponent(firstBook)}&page=1&per_page=20`) : {narrations:[]};

    const volIcons = {'Sahih al-Bukhari':'\ud83d\udcd7','Sahih Muslim':'\ud83d\udcd8','Sunan Abi Dawud':'\ud83d\udcd5'};
    const volEmojis = {'Sahih al-Bukhari':'\ud83d\udd4c','Sahih Muslim':'\ud83d\udd4c','Sunan Abi Dawud':'\u270d\ufe0f'};

    let html = `<div class="hadith-collections">
      <div class="hadith-spotlight">
        <div class="hadith-spotlight-box">
          <div class="hadith-spotlight-label">\u2726 Today's Selected Narration</div>
          <div class="hadith-spotlight-text">${((d.hadith||{}).english||'').replace(/\n/g, ' ').replace(/\s+/g, ' ')}</div>
          <div class="hadith-spotlight-ref">\u2014 ${(d.hadith||{}).bookName||''} (Ref: ${(d.hadith||{}).idInBook||''})</div>
          ${(d.hadith||{}).theme ? `<span class="hadith-spotlight-theme">${(d.hadith||{}).theme}</span>` : ''}
        </div>
      </div>
      <div class="hadith-book-tabs">`;
    for(const b of (books||[])) {
      html += `<button class="hadith-book-tab ${b.bookName === firstBook ? 'active' : ''}" data-book="${esc(b.bookName)}" onclick="hadithSelectBook('${esc(b.bookName)}', this)">
        ${volIcons[b.bookName]||'\ud83d\udcd6'} ${b.bookName} <span class="hadith-book-count">${b.count}</span>
      </button>`;
    }
    html += `</div>
      <div class="hadith-search-bar">
        <span class="hadith-search-icon">🔍</span>
        <input type="text" class="hadith-search-input" id="hadith-search-input"
          placeholder="Search narrations..." oninput="hadithSearch()"
          onkeydown="if(event.key==='Enter') hadithSearch()">
        <button class="hadith-search-clear" id="hadith-search-clear" onclick="hadithClearSearch()" style="display:none">✕</button>
      </div>
      <div class="hadith-narration-area" id="hadith-narration-area">`;
    for(const h of (firstNar.narrations||[])) {
      const text = (h.english||h.arabic||'').replace(/\n/g, ' ').replace(/\s+/g, ' ').trim();
      html += `<div class="narration-item">
        <div class="narration-text">${text}</div>
        <div class="narration-ref">\u2014 Ref: ${h.idInBook||'\u2014'}</div>
      </div>`;
    }
    if(firstNar.total_pages > 1) {
      html += `<div class="hadith-pagination" id="hadith-pagination">
        <span>Page 1 of ${firstNar.total_pages}</span>
        <button onclick="hadithPage(2)">\u25b6</button>
      </div>`;
    }
    html += `</div></div>`;
    hc.innerHTML = html;
  } catch(e) { hc.innerHTML = `<div class="loading">${e.message}</div>`; }
}

let hadithCurrentBook = '';
let hadithCurrentPage = 1;
let hadithSearchTimer = null;

async function hadithSelectBook(book, btn) {
  hadithCurrentBook = book;
  hadithCurrentPage = 1;
  document.querySelectorAll('.hadith-book-tab').forEach(b => b.classList.remove('active'));
  if(btn) btn.classList.add('active');
  // clear search when switching books
  const si = document.getElementById('hadith-search-input');
  if(si) { si.value = ''; document.getElementById('hadith-search-clear').style.display='none'; }
  await hadithLoadPage(book, 1, '');
}

async function hadithLoadPage(book, page, search) {
  if(search === undefined) search = document.getElementById('hadith-search-input')?.value?.trim() || '';
  const area = document.getElementById('hadith-narration-area');
  try {
    let url = `/api/hadith/narrations?book=${encodeURIComponent(book)}&page=${page}&per_page=20`;
    if(search) url += `&search=${encodeURIComponent(search)}`;
    const data = await loadJSON(url);
    let html = '';
    if(data.total === 0) {
      html = `<div class="narration-empty">${search ? '✨ No narrations match "'+esc(search)+'"' : '✨ No narrations found'}</div>`;
    } else {
      for(const h of (data.narrations||[])) {
        const text = (h.english||h.arabic||'').replace(/\n/g, ' ').replace(/\s+/g, ' ').trim();
        html += `<div class="narration-item">
          <div class="narration-text">${text}</div>
          <div class="narration-ref">\u2014 ${h.narratorEn ? h.narratorEn+' \u2014 ' : ''}Ref: ${h.idInBook||'\u2014'}</div>
        </div>`;
      }
      if(data.total_pages > 1) {
        html += `<div class="hadith-pagination" id="hadith-pagination">
          <button onclick="hadithPage(${page-1})" ${page <= 1 ? 'disabled' : ''}>\u25c0</button>
          <span>Page ${page} of ${data.total_pages}${search ? ' ('+data.total+' results)' : ''}</span>
          <button onclick="hadithPage(${page+1})" ${page >= data.total_pages ? 'disabled' : ''}>\u25b6</button>
        </div>`;
      }
    }
    area.innerHTML = html;
  } catch(e) { area.innerHTML = `<div class="loading">${e.message}</div>`; }
}

async function hadithPage(page) {
  hadithCurrentPage = page;
  const book = hadithCurrentBook || document.querySelector('.hadith-book-tab.active')?.dataset?.book || '';
  const search = document.getElementById('hadith-search-input')?.value?.trim() || '';
  await hadithLoadPage(book, page, search);
}

function hadithSearch() {
  if(hadithSearchTimer) clearTimeout(hadithSearchTimer);
  hadithSearchTimer = setTimeout(() => {
    hadithSearchTimer = null;
    const si = document.getElementById('hadith-search-input');
    const q = si?.value?.trim() || '';
    document.getElementById('hadith-search-clear').style.display = q ? 'block' : 'none';
    if(!hadithCurrentBook) {
      const active = document.querySelector('.hadith-book-tab.active');
      hadithCurrentBook = active?.dataset?.book || '';
    }
    hadithCurrentPage = 1;
    hadithLoadPage(hadithCurrentBook, 1, q);
  }, 300);
}

function hadithClearSearch() {
  const si = document.getElementById('hadith-search-input');
  if(si) { si.value = ''; }
  document.getElementById('hadith-search-clear').style.display = 'none';
  if(hadithSearchTimer) clearTimeout(hadithSearchTimer);
  if(!hadithCurrentBook) {
    const active = document.querySelector('.hadith-book-tab.active');
    hadithCurrentBook = active?.dataset?.book || '';
  }
  hadithCurrentPage = 1;
  hadithLoadPage(hadithCurrentBook, 1, '');
}

// ══════════ Sacred Library (Dynamic) ══════════

let libCurrentId = null;
let libCurrentPage = 1;
let libTotalPages = 0;
let libFontSize = 18;
let libDarkMode = true;
let libAllBooks = [];

const BOOK_COLORS = ['#F59E0B','#F97316','#10B981','#7C3AED','#EF4444','#DC2626','#3B82F6','#06B6D4','#22C55E','#EC4899','#8B5CF6','#14B8A6'];
const BOOK_ICONS = ['📖','📜','🔮','☀️','🌙','⚡','🪐','🔭','⭐','📕','📗','📘'];

