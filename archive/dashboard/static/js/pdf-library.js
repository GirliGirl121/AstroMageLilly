function bookColor(idx) { return BOOK_COLORS[idx % BOOK_COLORS.length]; }
function bookIcon(idx) { return BOOK_ICONS[idx % BOOK_ICONS.length]; }

async function loadLibrary() {
  const shelf = document.getElementById('library-shelf');
  shelf.innerHTML = '<div class="loading">📚 Loading sacred texts...</div>';
  try {
    libAllBooks = await loadJSON('/api/library/books');
    if(!libAllBooks || !libAllBooks.length) {
      shelf.innerHTML = '<div class="loading">No books yet. Click <strong>📥 Import</strong> to add PDFs from your collection.</div>';
      return;
    }
    let html = '';
    const perRow = 4;
    for(let i = 0; i < libAllBooks.length; i += perRow) {
      html += '<div class="shelf-row">';
      for(let j = i; j < i + perRow && j < libAllBooks.length; j++) {
        const b = libAllBooks[j];
        const color = bookColor(j);
        const icon = bookIcon(j);
        const pages = b.page_count || 0;
        const progress = b.progress_pct || 0;
        const ocrBadge = b.ocr_used ? ' <span style="font-size:10px;opacity:0.7">OCR</span>' : '';
        html += `<div class="book-item" data-id="${b.id}" title="${esc(b.title)}">
          <div class="book-spine" style="background:linear-gradient(180deg, ${color}dd, ${color}88)">
            <span class="book-icon">${icon}</span>
            <span class="book-spine-title">${esc(b.title)}</span>
          </div>
          <div class="book-footer">
            <span class="book-footer-author">${esc(b.author)}</span>
            <span class="book-footer-size">${pages} pages${ocrBadge}</span>
          </div>
          ${progress > 0 ? `<div class="book-progress-bar"><div class="book-progress-fill" style="width:${progress}%;background:${color}"></div></div>` : ''}
        </div>`;
      }
      html += '</div>';
    }
    document.getElementById('library-book-count').textContent = libAllBooks.length + ' books';
    shelf.innerHTML = html;
  } catch(e) { shelf.innerHTML = '<div class="loading">✨ The library shelves are quiet... '+e.message+'</div>'; }
}

// Click handler for book items
document.getElementById('library-shelf').addEventListener('click', (e) => {
  const bookItem = e.target.closest('.book-item');
  if(bookItem) libOpenBook(bookItem.dataset.id);
});

async function libOpenBook(bookId) {
  console.log('📖 Opening book:', bookId);
  libCurrentId = bookId;
  libCurrentPage = 1;
  document.getElementById('library-empty').style.display = 'none';
  document.getElementById('library-reader').style.display = 'flex';

  document.querySelectorAll('.book-item').forEach(b => b.classList.remove('active'));
  const el = document.querySelector(`.book-item[data-id="${bookId}"]`);
  if(el) el.classList.add('active');

  const content = document.getElementById('library-reader-content');
  const toolbar = document.getElementById('library-reader-toolbar');
  const tocDiv = document.getElementById('library-reader-toc');
  const footer = document.getElementById('library-reader-footer');

  toolbar.innerHTML = `<div class="lib-toolbar-loading"><span>📖</span> Opening...</div>`;
  tocDiv.innerHTML = '';
  footer.innerHTML = '';
  content.innerHTML = '<div class="loading">🌙 Opening the book...</div>';

  try {
    // Fetch book metadata + TOC in parallel
    const [meta, toc] = await Promise.all([
      loadJSON(`/api/library/book/${bookId}`),
      loadJSON(`/api/library/book/${bookId}/toc`)
    ]);

    if(!meta) throw new Error('Book not found');

    libTotalPages = meta.page_count || 0;

    // Toolbar
    toolbar.innerHTML = `
      <div class="lib-toolbar-left">
        <span class="lib-toolbar-icon">${bookIcon(libAllBooks.findIndex(b=>b.id===bookId))}</span>
        <div>
          <div class="lib-toolbar-title">${esc(meta.title)}</div>
          <div class="lib-toolbar-subtitle">${esc(meta.author)} · ${libTotalPages} pages · ${meta.ocr_used ? 'OCR' : 'Text'}</div>
        </div>
      </div>
      <div class="lib-toolbar-controls">
        <button class="lib-ctrl-btn" onclick="libToggleTOC()" title="Table of Contents">📑 TOC</button>
        <button class="lib-ctrl-btn" onclick="libChangeFontSize(-2)" title="Smaller font">A-</button>
        <button class="lib-ctrl-btn" onclick="libChangeFontSize(2)" title="Larger font">A+</button>
        <button class="lib-ctrl-btn" onclick="libToggleTheme()" title="Light/Dark mode">${libDarkMode ? '☀️' : '🌙'}</button>
        <button class="lib-ctrl-btn" onclick="libAddBookmark(${libCurrentPage})" title="Bookmark this page">🔖</button>
        <button class="lib-ctrl-btn" onclick="libShowHighlights()" title="My highlights & notes">✨ Notes</button>
      </div>`;

    // TOC dropdown
    if(toc && toc.length) {
      let tocHtml = '<div class="lib-toc-list">';
      toc.forEach(t => {
        tocHtml += `<div class="lib-toc-item" onclick="libGoToPage(${t.page_number});libToggleTOC()">
          ${'&nbsp;'.repeat(t.level * 4)}📄 ${esc(t.title)} <span class="lib-toc-page">p.${t.page_number}</span></div>`;
      });
      tocHtml += '</div>';
      tocDiv.innerHTML = `<div class="lib-toc-header">📑 Table of Contents</div>${tocHtml}`;
    }

    // Load page content
    await libLoadPage(libCurrentPage);

    // Footer with pagination
    libRenderFooter();
  } catch(e) {
    content.innerHTML = `<div class="loading">✨ ${e.message}</div>`;
    toolbar.innerHTML = '';
  }
}

async function libLoadPage(pageNum) {
  const content = document.getElementById('library-reader-content');
  content.innerHTML = '<div class="loading">📖 Loading page...</div>';
  
  try {
    const page = await loadJSON(`/api/library/book/${libCurrentId}/page/${pageNum}`);
    if(!page) {
      content.innerHTML = '<div class="loading">Page not found</div>';
      return;
    }
    
    // Convert markdown-ish to HTML
    let text = page.content || '';
    text = libRenderMarkdown(text);
    content.innerHTML = text;
    content.style.fontSize = libFontSize + 'px';
    content.className = 'library-reader-content ' + (libDarkMode ? 'lib-dark' : 'lib-light');
    content.scrollTop = 0;
  } catch(e) {
    content.innerHTML = `<div class="loading">Error: ${e.message}</div>`;
  }
}

function libRenderMarkdown(text) {
  if(!text) return '<div class="loading">(empty page)</div>';
  
  // Escape HTML
  let html = esc(text);
  
  // Headings
  html = html.replace(/^#### (.+)$/gm, '<h4 class="lib-h4">$1</h4>');
  html = html.replace(/^### (.+)$/gm,  '<h3 class="lib-h3">$1</h3>');
  html = html.replace(/^## (.+)$/gm,   '<h2 class="lib-h2">$1</h2>');
  html = html.replace(/^# (.+)$/gm,    '<h1 class="lib-h1">$1</h1>');
  
  // Bold / italic
  html = html.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>');
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
  
  // Code
  html = html.replace(/`(.+?)`/g, '<code>$1</code>');
  
  // Horizontal rules
  html = html.replace(/^---+$/gm, '<hr>');
  html = html.replace(/^\*\*\*+$/gm, '<hr>');
  
  // Blockquotes
  html = html.replace(/^&gt; (.+)$/gm, '<blockquote>$1</blockquote>');
  
  // Lists
  html = html.replace(/^(\d+)\. (.+)$/gm, '<li class="lib-num">$2</li>');
  html = html.replace(/^[-*] (.+)$/gm, '<li class="lib-bullet">$2</li>');
  
  // Paragraphs - split by blank lines, wrap non-text in <p>
  const blocks = html.split(/\n{2,}/);
  let result = '';
  for(let block of blocks) {
    block = block.trim();
    if(!block) continue;
    // Skip if already wrapped in block-level element
    if(/^<(h[1-6]|hr|blockquote|ul|ol)/.test(block)) {
      // Wrap list items in <ul>
      if(block.includes('<li class="lib-num">')) {
        block = '<ol>' + block + '</ol>';
      } else if(block.includes('<li class="lib-bullet">')) {
        block = '<ul>' + block + '</ul>';
      }
      result += block;
    } else {
      // Handle mixed list/text blocks
      if(block.includes('<li>')) {
        const lis = block.split('\n').filter(l => l.trim());
        result += '<ul>' + lis.map(l => l.replace(/^\s*[-*] /, '').replace(/^\d+\.\s*/, '')) + '</ul>';
      } else {
        block = block.replace(/\n/g, '<br>');
        result += '<p>' + block + '</p>';
      }
    }
  }
  
  return result;
}

function libRenderFooter() {
  const footer = document.getElementById('library-reader-footer');
  const prev = libCurrentPage > 1;
  const next = libCurrentPage < libTotalPages;
  footer.innerHTML = `
    <div class="lib-footer-nav">
      <button class="lib-nav-btn" ${prev ? '' : 'disabled'} onclick="libGoToPage(${libCurrentPage - 1})">◀ Prev</button>
      <div class="lib-footer-center">
        <input type="number" class="lib-page-input" value="${libCurrentPage}" min="1" max="${libTotalPages}" onchange="libGoToPage(parseInt(this.value))" />
        <span class="lib-page-info"> / ${libTotalPages} pages</span>
      </div>
      <button class="lib-nav-btn" ${next ? '' : 'disabled'} onclick="libGoToPage(${libCurrentPage + 1})">Next ▶</button>
    </div>
    <div class="lib-footer-progress">
      <div class="lib-progress-fill" style="width:${((libCurrentPage/Math.max(libTotalPages,1))*100).toFixed(1)}%"></div>
      <span class="lib-progress-text">${((libCurrentPage/Math.max(libTotalPages,1))*100).toFixed(1)}%</span>
    </div>`;
  
  // Update server progress
  try { fetch(`/api/library/book/${libCurrentId}/progress`, {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({page:libCurrentPage})}); } catch(e) {}
}

function libGoToPage(n) {
  n = Math.max(1, Math.min(n, libTotalPages));
  libCurrentPage = n;
  libLoadPage(n);
  libRenderFooter();
  document.querySelector('.library-reader-content').scrollTop = 0;
}

function libChangeFontSize(delta) {
  libFontSize = Math.max(12, Math.min(32, libFontSize + delta));
  document.getElementById('library-reader-content').style.fontSize = libFontSize + 'px';
}

function libToggleTheme() {
  libDarkMode = !libDarkMode;
  document.getElementById('library-reader-content').className = 'library-reader-content ' + (libDarkMode ? 'lib-dark' : 'lib-light');
  const btn = document.querySelector('.lib-ctrl-btn[onclick*="libToggleTheme"]');
  if(btn) btn.textContent = libDarkMode ? '☀️' : '🌙';
}

function libToggleTOC() {
  const toc = document.getElementById('library-reader-toc');
  toc.classList.toggle('lib-toc-open');
}

function libShowHighlights() {
  if(!libCurrentId || !libCurrentPage) return;
  Promise.all([
    loadJSON(`/api/library/book/${libCurrentId}/highlights`),
    loadJSON(`/api/library/book/${libCurrentId}/notes`)
  ]).then(([highlights, notes]) => {
    let html = '<div class="lib-notes-panel"><h3>✨ Highlights & Notes</h3>';
    if(highlights && highlights.length) {
      html += '<h4>Highlights</h4>';
      for(const h of highlights) {
        html += `<div class="lib-highlight-item" style="border-left:3px solid ${h.color}">
          <strong>p.${h.page_number}:</strong> ${esc(h.selected_text)}
          ${h.note ? '<br><em>Note: '+esc(h.note)+'</em>' : ''}
        </div>`;
      }
    }
    if(notes && notes.length) {
      html += '<h4>Notes</h4>';
      for(const n of notes) {
        html += `<div class="lib-note-item">
          <strong>p.${n.page_number}:</strong> ${esc(n.content)}
          <br><small>${n.date_created.split('T')[0]}</small>
        </div>`;
      }
    }
    if(!highlights?.length && !notes?.length) {
      html += '<p style="opacity:0.6">No highlights or notes yet. Right-click a page to add notes.</p>';
    }
    html += '</div>';
    document.getElementById('library-reader-content').innerHTML = html;
  });
}

async function libAddBookmark(page) {
  try {
    await fetch(`/api/library/book/${libCurrentId}/bookmark`, {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({page: page, title: `Page ${page}`})
    });
    alert('🔖 Bookmarked page ' + page);
  } catch(e) { alert('Bookmark failed: ' + e.message); }
}

// Global library search
async function librarySearch() {
  const query = document.getElementById('library-search-input').value.trim();
  if(!query) return;
  
  const shelf = document.getElementById('library-shelf');
  shelf.innerHTML = '<div class="loading">🔍 Searching...</div>';
  
  try {
    const results = await loadJSON(`/api/library/search?q=${encodeURIComponent(query)}`);
    if(!results.results || !results.results.length) {
      shelf.innerHTML = `<div class="loading">No results for "${esc(query)}".</div>`;
      return;
    }
    let html = `<div style="padding:8px 12px;font-size:13px;opacity:0.7">Found ${results.results.length} results for "${esc(query)}"<br><hr style="border-color:rgba(255,255,255,0.05);margin:8px 0"></div>`;
    const byBook = {};
    for(const r of results.results) {
      if(!byBook[r.book_id]) byBook[r.book_id] = {title: r.book_title, results: []};
      byBook[r.book_id].results.push(r);
    }
    for(const [bookId, data] of Object.entries(byBook)) {
      html += `<div class="lib-search-book" onclick="libOpenBook('${bookId}')">
        <strong>📖 ${esc(data.title)}</strong> <span style="font-size:11px;opacity:0.6">(${data.results.length} hits)</span>
      </div>`;
      for(const r of data.results.slice(0,3)) {
        html += `<div class="lib-search-result" onclick="event.stopPropagation();libOpenBook('${bookId}');setTimeout(()=>libGoToPage(${r.page_number}),800)">
          <span style="opacity:0.5">p.${r.page_number}:</span> ${esc(r.snippet)}
        </div>`;
      }
    }
    shelf.innerHTML = html;
  } catch(e) {
    shelf.innerHTML = `<div class="loading">Search error: ${e.message}</div>`;
  }
}

// Import PDFs
async function importAllPDFs() {
  const shelf = document.getElementById('library-shelf');
  shelf.innerHTML = '<div class="loading">📥 Importing PDFs... This may take a while.</div>';
  try {
    const resp = await fetch('/api/library/import', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({directory: '/home/ladylefey/Documents/magewisdom'})
    });
    const result = await resp.json();
    shelf.innerHTML = `<div class="loading">Import started! ${result.imported ? result.imported.length : 0} books being processed.<br>
      <br>This happens in the background. Refresh the library in a few minutes to see them all. ✨
      <br><br><button class="btn btn-sm" onclick="loadLibrary()">🔄 Refresh Library</button></div>`;
  } catch(e) {
    shelf.innerHTML = `<div class="loading">Import error: ${e.message}</div>`;
  }
}

// Keyboard navigation for book reader
document.addEventListener('keydown', (e) => {
  if(!libCurrentId || !document.getElementById('tab-library')?.classList.contains('active')) return;
  if(e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
  const panel = document.querySelector('.library-reader-content');
  if(!panel) return;
  if(e.key === 'ArrowLeft') { e.preventDefault(); libGoToPage(libCurrentPage - 1); }
  if(e.key === 'ArrowRight') { e.preventDefault(); libGoToPage(libCurrentPage + 1); }
});

// Load library when tab is shown
document.addEventListener('DOMContentLoaded', () => {
  const observer = new MutationObserver(() => {
    const libTab = document.getElementById('tab-library');
    if(libTab && libTab.classList.contains('active') && !libTab.dataset.loaded) {
      libTab.dataset.loaded = 'true';
      loadLibrary();
    }
  });
  const tabPages = document.querySelectorAll('.tab-page');
  tabPages.forEach(t => observer.observe(t, {attributes: true, attributeFilter: ['class']}));
});

// ══════════ Chat ══════════
