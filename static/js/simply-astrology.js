
    // Search filter
    document.getElementById('simply-search').addEventListener('input', function() {
      const q = this.value.toLowerCase();
      document.querySelectorAll('.simply-nav-item').forEach(item => {
        const name = item.querySelector('.simply-nav-name').textContent.toLowerCase();
        item.style.display = name.includes(q) ? 'flex' : 'none';
      });
    });
  } catch(e) {
    nav.innerHTML = '<div class="simply-empty">Failed to load knowledge base</div>';
    sc.innerHTML = `<div class="simply-welcome"><p>Error: ${e.message}</p></div>`;
  }
}

// ═══ Horoscope Tab ═══
function switchHoro(type) {
  document.querySelectorAll('.horo-nav-item').forEach(item => item.classList.remove('active'));
  const navItem = document.querySelector('.horo-nav-item[data-horo="' + type + '"]');
  if(navItem) navItem.classList.add('active');
  var container = document.getElementById('horo-content');
  container.innerHTML = '<div class="horo-loading">Loading the stars...</div>';
  var endpoints = {daily:'/api/horoscope/daily',weekly:'/api/horoscope/weekly',monthly:'/api/horoscope/monthly',love:'/api/horoscope/love',career:'/api/horoscope/career',health:'/api/horoscope/health',compat:'/api/horoscope/compatibility'};
  fetch(endpoints[type]).then(function(r){return r.json()}).then(function(data){
    if(type==='daily') renderDailyHoro(container, data);
    else if(type==='weekly') renderWeeklyHoro(container, data);
    else if(type==='monthly') renderMonthlyHoro(container, data);
    else if(type==='love') renderLoveHoro(container, data);
    else if(type==='career') renderCareerHoro(container, data);
    else if(type==='health') renderHealthHoro(container, data);
    else if(type==='compat') renderCompatHoro(container, data);
  }).catch(function(e){container.innerHTML='<div class="horo-loading">Error: '+e.message+'</div>'});
}

function renderDailyHoro(c, d) {
  var today = new Date().toLocaleDateString('en-GB',{weekday:'long',day:'numeric',month:'long',year:'numeric'});
  var glyphs = {Aries:'\u2648',Taurus:'\u2649',Gemini:'\u264A',Cancer:'\u264B',Leo:'\u264C',Virgo:'\u264D',Libra:'\u264E',Scorpio:'\u264F',Sagittarius:'\u2650',Capricorn:'\u2651',Aquarius:'\u2652',Pisces:'\u2653'};
  var elements = {Aries:'\ud83d\udd25 Fire',Taurus:'\ud83c\udf0d Earth',Gemini:'\ud83c\udf2c Air',Cancer:'\ud83d\udca7 Water',Leo:'\ud83d\udd25 Fire',Virgo:'\ud83c\udf0d Earth',Libra:'\ud83c\udf2c Air',Scorpio:'\ud83d\udca7 Water',Sagittarius:'\ud83d\udd25 Fire',Capricorn:'\ud83c\udf0d Earth',Aquarius:'\ud83c\udf2c Air',Pisces:'\ud83d\udca7 Water'};
  var allSigns = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'];
  var html = '<div class="horo-title">\u2b50 Daily Horoscope</div>';
  html += '<div class="horo-date">'+today+' \u00b7 '+d.moon_emoji+' '+d.moon_phase+'</div>';
  html += '<div class="horo-overall">The Sun is in <strong>'+d.sign+'</strong> today, with <strong>'+d.moon_phase+'</strong> '+d.moon_emoji+' illuminating the sky.</div>';
  if(d.aspect_interpretations && d.aspect_interpretations.length) {
    html += '<div class="horo-section-label">\u2728 Key Aspects</div><div class="horo-aspects">';
    d.aspect_interpretations.slice(0,5).forEach(function(txt){ html += '<span class="horo-aspect-pill">'+txt+'</span>'; });
    html += '</div>';
  }
  html += '<div class="horo-section-label">\ud83d\udd2e All 12 Signs</div><div class="horo-signs-grid">';
  allSigns.forEach(function(sn) {
    var interps = d.sign_interpretations && d.sign_interpretations[sn];
    var transiting = d.transits ? d.transits.filter(function(p){ return p.sign === sn; }).map(function(p){ return p.symbol+' '+p.name; }) : [];
    html += '<div class="horo-sign-card"><div class="horo-sign-glyph">'+glyphs[sn]+'</div><div class="horo-sign-name">'+sn+'</div><div class="horo-sign-element">'+elements[sn]+'</div>';
    if(transiting.length) { html += '<div class="horo-sign-transit">'+transiting.join(', ')+'</div>'; }
function simplySelect(idx) {
  // Update nav highlight
  document.querySelectorAll('.simply-nav-item').forEach(item => item.classList.remove('active'));
  const navItem = document.querySelector(`.simply-nav-item[data-idx="${idx}"]`);
  if(navItem) navItem.classList.add('active');

  // Show selected section, hide others
  document.querySelectorAll('.simply-section').forEach(s => s.classList.remove('active'));
  const section = document.getElementById(`simply-sec-${idx}`);
  if(section) section.classList.add('active');
}

function simplyToggleCard(card) {
  const wasOpen = card.classList.contains('open');
  // Close all other cards in this section
  card.closest('.simply-section').querySelectorAll('.simply-card').forEach(c => {
    c.classList.remove('open');
    c.querySelector('.simply-card-arrow').textContent = '▶';
  });
  if(!wasOpen) {
    card.classList.add('open');
    card.querySelector('.simply-card-arrow').textContent = '▼';
    setTimeout(() => card.scrollIntoView({behavior: 'smooth', block: 'nearest'}), 100);
  }
}

