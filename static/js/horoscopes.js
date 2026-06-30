    if(interps && interps.length) { html += '<div class="horo-sign-interp">'+interps.join('<br>')+'</div>'; }
    html += '</div>';
  });
  html += '</div>';
  c.innerHTML = html;
}

function renderWeeklyHoro(c, d) {
  var html = '<div class="horo-title">📅 Weekly Horoscope</div>';
  html += '<div class="horo-date">Week '+d.week+'</div>';
  html += '<div class="horo-overall"><strong>Focus:</strong> '+d.focus+'</div>';
  html += '<div class="horo-interp">'+d.message+'<br><br>'+d.summary+'</div>';
  c.innerHTML = html;
}

function renderMonthlyHoro(c, d) {
  var html = '<div class="horo-title">🌕 Monthly Overview</div>';
  html += '<div class="horo-date">'+d.month+'</div>';
  html += '<div class="horo-overall"><strong>Focus:</strong> '+d.focus+'</div>';
  html += '<div class="horo-interp"><strong>Planetary Influences:</strong> '+d.planetary_influences+'<br><br><strong>Advice:</strong> '+d.advice+'</div>';
  c.innerHTML = html;
}

function renderLoveHoro(c, d) {
  var today = new Date().toLocaleDateString('en-GB',{weekday:'long',day:'numeric',month:'long',year:'numeric'});
  var html = '<div class="horo-title">💕 Love Horoscope</div>';
  html += '<div class="horo-date">'+today+'</div>';
  html += '<div class="horo-love-grid">';
  html += '<div class="horo-planet-card"><div class="horo-planet-symbol">♀</div><div class="horo-planet-name">Venus</div><div class="horo-planet-pos">'+d.venus_sign+' '+(d.venus_retrograde==='yes'?'℞':'')+'</div></div>';
  html += '<div class="horo-planet-card"><div class="horo-planet-symbol">♂</div><div class="horo-planet-name">Mars</div><div class="horo-planet-pos">'+d.mars_sign+' '+(d.mars_retrograde==='yes'?'℞':'')+'</div></div>';
  html += '</div>';
  html += '<div class="horo-interp">'+d.message+'<br><br>'+d.advice+'</div>';
  c.innerHTML = html;
}

function renderCareerHoro(c, d) {
  var today = new Date().toLocaleDateString('en-GB',{weekday:'long',day:'numeric',month:'long',year:'numeric'});
  var html = '<div class="horo-title">💼 Career & Money</div>';
  html += '<div class="horo-date">'+today+'</div>';
  html += '<div class="horo-love-grid">';
  html += '<div class="horo-planet-card"><div class="horo-planet-symbol">♄</div><div class="horo-planet-name">Saturn</div><div class="horo-planet-pos">'+d.saturn_sign+'</div></div>';
  html += '<div class="horo-planet-card"><div class="horo-planet-symbol">♃</div><div class="horo-planet-name">Jupiter</div><div class="horo-planet-pos">'+d.jupiter_sign+'</div></div>';
  html += '</div>';
  html += '<div class="horo-interp">'+d.message+'<br><br>'+d.advice+'</div>';
  c.innerHTML = html;
}

function renderHealthHoro(c, d) {
  var today = new Date().toLocaleDateString('en-GB',{weekday:'long',day:'numeric',month:'long',year:'numeric'});
  var html = '<div class="horo-title">🌿 Health & Wellness</div>';
  html += '<div class="horo-date">'+today+'</div>';
  html += '<div class="horo-love-grid">';
  html += '<div class="horo-planet-card"><div class="horo-planet-symbol">☽</div><div class="horo-planet-name">Moon</div><div class="horo-planet-pos">'+d.moon_sign+' ('+d.moon_phase+')</div></div>';
  html += '</div>';
  html += '<div class="horo-interp">'+d.message+'<br><br>'+d.advice+'</div>';
  c.innerHTML = html;
}

function renderCompatHoro(c, d) {
  var signs = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'];
  var glyphs = ['♈','♉','♊','♋','♌','♍','♎','♏','♐','♑','♒','♓'];
  var elems = {Aries:'Fire',Taurus:'Earth',Gemini:'Air',Cancer:'Water',Leo:'Fire',Virgo:'Earth',Libra:'Air',Scorpio:'Water',Sagittarius:'Fire',Capricorn:'Earth',Aquarius:'Air',Pisces:'Water'};
  var elemColors = {Fire:'#ff6b35',Earth:'#8b6914',Air:'#87ceeb',Water:'#4a90d9'};
  // Score + colored heart for pair
  // Hearts: 🩷 pink (natural) ❤️ red (harmonious) 🧡 orange (great chemistry) 💛 yellow (mutual understanding) 💚 green (good balance) 🩵 light blue (volatile) 💙 blue (work combo) 🩷 pink (low commitment) 🖤 grey (nothing in common)
  var catHeart = {natural:'🩷',harmonious:'❤️',moderate:'💚',volatile:'🩵'};
  var catColor = {natural:'#ff69b4',harmonious:'#e74c3c',moderate:'#4caf50',volatile:'#e74c3c'};
  var catLabel = {natural:'Natural Partners',harmonious:'Harmonious',moderate:'Good Balance',volatile:'Challenging'};
  function getScore(s1,s2) {
    var e1=elems[s1],e2=elems[s2];
    if(s1===s2) return {score:70,note:'Familiar energy — comfortable but can stagnate',cat:'harmonious'};
    if(e1===e2) return {score:88,note:'Natural harmony — same element understanding',cat:'natural'};
    if((e1==='Fire'&&e2==='Air')||(e1==='Air'&&e2==='Fire')) return {score:82,note:'Complementary — energizing and passionate',cat:'harmonious'};
    if((e1==='Earth'&&e2==='Water')||(e1==='Water'&&e2==='Earth')) return {score:85,note:'Nurturing bond — mutual growth',cat:'natural'};
    if((e1==='Fire'&&e2==='Water')||(e1==='Water'&&e2==='Fire')) return {score:42,note:'Challenging — requires patience & compromise',cat:'volatile'};
    if((e1==='Air'&&e2==='Earth')||(e1==='Earth'&&e2==='Air')) return {score:48,note:'Different worlds — effort needed',cat:'volatile'};
    if((e1==='Fire'&&e2==='Earth')||(e1==='Earth'&&e2==='Fire')) return {score:65,note:'Balanced with effort — steady warmth',cat:'moderate'};
    if((e1==='Air'&&e2==='Water')||(e1==='Water'&&e2==='Air')) return {score:60,note:'Mind meets heart — can flow or flood',cat:'moderate'};
    return {score:55,note:'Neutral — takes conscious work',cat:'moderate'};
  }

  var today = new Date().toLocaleDateString('en-GB',{weekday:'long',day:'numeric',month:'long',year:'numeric'});
  var html = '<div class="horo-title">💖 Compatibility</div>';
  html += '<div class="horo-date">'+today+'</div>';

  // Legend with colored hearts
  html += '<div class="horo-compat-legend">';
  Object.keys(catColor).forEach(function(cat){
    html += '<span class="horo-legend-item"><span class="horo-legend-heart">'+catHeart[cat]+'</span>'+catLabel[cat]+'</span>';
  });
  html += '</div>';

  // Matrix
  html += '<div class="horo-matrix-wrap"><table class="horo-matrix"><thead><tr><th></th>';
  signs.forEach(function(s,i){html+='<th>'+glyphs[i]+'</th>'});
  html += '</tr></thead><tbody>';
  signs.forEach(function(s1,i){
    html += '<tr><th>'+glyphs[i]+' '+s1+'</th>';
    signs.forEach(function(s2,j){
      var r = getScore(s1,s2);
      var color = catColor[r.cat];
      var heart = catHeart[r.cat];
      html += '<td class="horo-matrix-cell" style="background:'+color+'22;border-color:'+color+'" data-s1="'+s1+'" data-s2="'+s2+'" data-score="'+r.score+'" data-note="'+esc(r.note)+'" onclick="showCompatDetail(this)"><span class="horo-cell-heart">'+heart+'</span><span class="horo-cell-pct">'+r.score+'</span></td>';
    });
    html += '</tr>';
  });
  html += '</tbody></table></div>';

  // Detail panel
  html += '<div id="compat-detail" class="horo-compat-detail" style="display:none"></div>';

  // Element harmony
  html += '<div class="horo-section-label">🔥 Element Harmony</div><div class="horo-compat-elements">';
  var elemEmoji = {Fire:'🔥',Earth:'🌍',Air:'💨',Water:'💧'};
  Object.keys(d.elements).forEach(function(elem){
    var ed = d.elements[elem];
    html += '<div class="horo-elem-card"><div class="horo-elem-name">'+elemEmoji[elem]+' '+elem+'</div><div class="horo-elem-best">Best: '+ed.best.join(', ')+'</div><div class="horo-elem-chal">Challenging: '+(ed.challenging.join(', ')||'—')+'</div></div>';
  });
  html += '</div>';

  c.innerHTML = html;
}

function showCompatDetail(el) {
  var s1 = el.dataset.s1, s2 = el.dataset.s2, score = el.dataset.score, note = el.dataset.note;
  var color = parseInt(score) >= 80 ? '#9b59b6' : parseInt(score) >= 65 ? '#e67e22' : '#e74c3c';
  document.getElementById('compat-detail').style.display = 'block';
  document.getElementById('compat-detail').innerHTML =
    '<div class="horo-detail-score" style="color:'+color+'">'+score+'%</div>' +
    '<div class="horo-detail-signs">'+s1+' 💕 '+s2+'</div>' +
    '<div class="horo-detail-note">'+note+'</div>' +
    '<div class="horo-detail-advice">'+getCompatAdvice(s1,s2,parseInt(score))+'</div>';
}

function getCompatAdvice(s1,s2,score) {
  if(score >= 85) return 'A deeply natural connection. Communication flows easily and mutual understanding comes effortlessly. Nurture this bond with gratitude.';
  if(score >= 70) return 'Strong potential with some effort needed. Focus on appreciating your differences — they complement rather than divide.';
  if(score >= 55) return 'This pairing requires conscious work. Practice patience and active listening. The growth you experience together is the reward.';
  return 'A challenging but transformative match. Set clear boundaries, communicate honestly, and remember that opposites can attract — with mutual respect.';
}

function toggleBook(id) {
  const el = document.getElementById(`book-${id}`);
  const all = document.querySelectorAll('.book-detail');
  all.forEach(d => { if(d !== el) d.classList.remove('open'); });
  el.classList.toggle('open');
  if(el.classList.contains('open')) {
    setTimeout(() => el.scrollIntoView({behavior: 'smooth', block: 'center'}), 100);
  }
}

