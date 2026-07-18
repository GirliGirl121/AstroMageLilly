// Chat UI was removed; keep sendChat function for API use but guard listeners
async function sendChat() {
  const input = document.getElementById('chat-input');
  if(!input) return;
  const msg = input.value.trim();
  if(!msg) return;
  input.value = '';
  const msgs = document.getElementById('chat-messages');
  if(!msgs) return;
  msgs.innerHTML += `<div class="chat-msg user"><div class="bubble">${esc(msg)}</div></div>`;
  msgs.scrollTop = msgs.scrollHeight;
  try {
    const reply = await loadJSON('/api/chat', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({message: msg})
    });
    msgs.innerHTML += `<div class="chat-msg"><div class="avatar">🌈</div><div class="bubble">${reply.reply||'The stars are listening...'}</div></div>`;
    msgs.scrollTop = msgs.scrollHeight;
  } catch(e) {
    msgs.innerHTML += `<div class="chat-msg"><div class="avatar">🌈</div><div class="bubble">My connection flickered... speak again, love? ✨</div></div>`;
  }
}
// Chat UI elements not currently in the DOM — listeners removed to prevent JS breakage

// ─── Translate Panel ───
document.getElementById('translate-btn').addEventListener('click', () => {
  const panel = document.getElementById('translate-panel');
  panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
});
document.getElementById('translate-close').addEventListener('click', () => {
  document.getElementById('translate-panel').style.display = 'none';
});
// Close on outside click
document.addEventListener('click', (e) => {
  const panel = document.getElementById('translate-panel');
  const btn = document.getElementById('translate-btn');
  if (panel && panel.style.display !== 'none' && !panel.contains(e.target) && !btn.contains(e.target)) {
    panel.style.display = 'none';
  }
});
// Language tab switching
document.querySelectorAll('.t-lang').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.t-lang').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const lang = btn.dataset.lang;
    const textarea = document.getElementById('translate-input');
    if (lang === 'arabic') textarea.placeholder = 'أدخل نصاً عربياً... Enter Arabic text...';
    else if (lang === 'hebrew') textarea.placeholder = 'הכנס טקסט עברי... Enter Hebrew text...';
    else if (lang === 'syriac') textarea.placeholder = 'ܡܘܬܒ ܟܬܒܐ ܣܘܪܝܝܐ... Enter Syriac text...';
    else if (lang === 'abjad') textarea.placeholder = 'Type Arabic letters to see abjad values (e.g. ب س م ا ل ل ه)';
  });
});
// Abjad quick reference
const ABJAD_MAP = {'ا':1,'ب':2,'ج':3,'د':4,'ه':5,'و':6,'ز':7,'ح':8,'ط':9,'ي':10,'ك':20,'ل':30,'م':40,'ن':50,'س':60,'ع':70,'ف':80,'ص':90,'ق':100,'ر':200,'ش':300,'ت':400,'ث':500,'خ':600,'ذ':700,'ض':800,'ظ':900,'غ':1000,'ة':5,'ى':10};
// Translate submit
document.getElementById('translate-submit').addEventListener('click', async () => {
  const input = document.getElementById('translate-input');
  const result = document.getElementById('translate-result');
  const txt = input.value.trim();
  if (!txt) return;

  // Abjad mode
  const activeLang = document.querySelector('.t-lang.active')?.dataset.lang;
  if (activeLang === 'abjad') {
    const chars = txt.split('').filter(c => ABJAD_MAP[c] !== undefined);
    const values = chars.map(c => `${c}=${ABJAD_MAP[c]}`);
    const total = chars.reduce((s, c) => s + ABJAD_MAP[c], 0);
    result.innerHTML = `<strong>🔢 Abjad Calculation:</strong><br><br>${values.join(' + ')}<br><br><strong>Total: ${total}</strong> ${chars.length > 1 ? `(${chars.length} letters)` : ''}<br><br><em>Letter values (abjad) are used in Islamic talisman design, letter magic (ilm al-huruf), and Picatrix calculations.</em>`;
    return;
  }

  result.innerHTML = '<div class="translate-placeholder">Consulting the sacred archive... 🔮</div>';
  const submitBtn = document.getElementById('translate-submit');
  submitBtn.disabled = true;
  try {
    const reply = await loadJSON('/api/chat', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({message: txt})
    });
    if (reply.reply) {
      const body = reply.reply.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
      result.innerHTML = body.replace(/\n/g, '<br>');
    }
  } catch(e) {
    result.innerHTML = '<div class="translate-placeholder">The stars are quiet... try again? 🌙</div>';
  }
  submitBtn.disabled = false;
});

// ══════════ MagiJournal Diary JS ══════════
let magiDate = new Date();
let magiMonth = magiDate.getFullYear();
let magiYear = magiDate.getFullYear();
let magiDay = magiDate.getDate();
let magiAutoSave = null;

