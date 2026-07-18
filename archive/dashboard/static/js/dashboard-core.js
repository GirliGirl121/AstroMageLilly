// ══════════ Sidebar ══════════
const sidebar = document.getElementById('sidebar');
const hamburger = document.getElementById('hamburger');
const pinBtn = document.getElementById('pin-btn');
let sidebarPinned = localStorage.getItem('sidebar_pinned') === 'true';

if(sidebarPinned) { sidebar.classList.remove('closed'); pinBtn.classList.add('pinned'); pinBtn.textContent = '📍'; }
// On desktop (> 900px), keep sidebar open by default
else if(window.innerWidth > 900) { sidebar.classList.remove('closed'); }
else { sidebar.classList.add('closed'); }

function openSidebar() { sidebar.classList.remove('closed'); }
function closeSidebar() { if(!sidebarPinned) sidebar.classList.add('closed'); }
function toggleSidebar() {
  if(sidebar.classList.contains('closed')) openSidebar();
  else if(!sidebarPinned) closeSidebar();
  else { sidebarPinned=false; pinBtn.classList.remove('pinned'); pinBtn.textContent='📌'; localStorage.setItem('sidebar_pinned','false'); closeSidebar(); }
}

hamburger.addEventListener('click', toggleSidebar);
pinBtn.addEventListener('click', () => {
  sidebarPinned = !sidebarPinned;
  pinBtn.classList.toggle('pinned'); pinBtn.textContent = sidebarPinned ? '📍' : '📌';
  if(sidebarPinned) openSidebar(); else closeSidebar();
  localStorage.setItem('sidebar_pinned', sidebarPinned);
});
document.getElementById('avatar-mini').addEventListener('click', openSidebar);

// Tab switching
document.querySelectorAll('.sidebar-nav-item').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.sidebar-nav-item').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-page').forEach(t => t.classList.remove('active'));
    btn.classList.add('active');
    const tab = document.getElementById(btn.dataset.tab);
    if(tab) tab.classList.add('active');
    // Pause starfield on reading tabs (CPU saver)
    document.getElementById('starfield').dataset.active = (btn.dataset.tab === 'tab-home') ? 'true' : 'false';
    // Sync toggle button icon with current state
    const starsBtn = document.getElementById('btn-stars');
    if(starsBtn) starsBtn.textContent = (btn.dataset.tab === 'tab-home') ? '✨' : '🌙';
    if(window.innerWidth <= 900 && !sidebarPinned) closeSidebar();
    // Lazy load
    const lazy = {
      'tab-natal': 'natal-worksheet', 'tab-library': 'library-shelf',
      'tab-quran': 'quran-full-content', 'tab-hadith': 'hadith-full-content',
      'tab-dashas': 'dashas-content', 'tab-nakshatras': 'nakshatras-full-content', 'tab-transits': 'live-content',
      'tab-horoscope': 'horo-content', 'tab-magi': 'magi-astro-bar',
      // 'tab-simply' removed from lazy — content is now static
    };
    const cid = lazy[btn.dataset.tab];
    if(cid && document.getElementById(cid).innerHTML.includes('Loading')) {
      if(btn.dataset.tab === 'tab-natal') loadNatal();
      else if(btn.dataset.tab === 'tab-transits') loadLive();
      else if(btn.dataset.tab === 'tab-library') loadLibrary();
      else if(btn.dataset.tab === 'tab-simply') loadSimply();
      else if(btn.dataset.tab === 'tab-dashas') loadDashasFull();
      else if(btn.dataset.tab === 'tab-nakshatras') loadNakshatrasFull();
      else if(btn.dataset.tab === 'tab-horoscope') switchHoro('daily');
      else if(btn.dataset.tab === 'tab-magi') magiLoadDay(document.getElementById('magi-date-input').value || magiFormatDate(new Date()));
      else if(btn.dataset.tab === 'tab-quran') loadQuranFull();
      else if(btn.dataset.tab === 'tab-hadith') loadHadithFull();
    }
    // Tarot has its own section-based lazy load
    if(btn.dataset.tab === 'tab-tarot') loadTarotFull();
  });
});

// ══════════ Helpers ══════════
async function loadJSON(p, opts) { const r = await fetch(p, opts); if(!r.ok) throw new Error(p+': '+r.status); return r.json(); }
function esc(t) { const d = document.createElement('div'); d.textContent = t; return d.innerHTML; }

// Natal Chart CRUD state
let currentNatalChartId = null;
let currentNatalData = null;

