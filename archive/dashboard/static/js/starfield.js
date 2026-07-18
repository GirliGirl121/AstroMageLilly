// ══════════ Starfield ══════════
// CPU-optimized: pauses when tab hidden, throttled to ~30fps, fewer stars
(function(){
  const c = document.getElementById('starfield');
  c.dataset.active = 'true'; // 'false' = paused to save CPU
  const ctx = c.getContext('2d');
  let stars = [], running = true, frameSkip = 0;
  function resize(){
    c.width = window.innerWidth; c.height = window.innerHeight;
    stars = [];
    for(let i = 0; i < 100; i++){
      stars.push({
        x: Math.random()*c.width, y: Math.random()*c.height,
        r: Math.random()*1.2+0.3, a: Math.random()*0.5+0.2, da: (Math.random()-0.5)*0.015
      });
    }
  }
  function draw(){
    if(!running || c.dataset.active === 'false') return;
    // Skip every other frame → ~30fps throttle
    frameSkip = 1 - frameSkip;
    if(frameSkip) { requestAnimationFrame(draw); return; }
    ctx.clearRect(0,0,c.width,c.height);
    for(const s of stars){
      s.a += s.da;
      if(s.a>0.7||s.a<0.1) s.da*=-1;
      ctx.beginPath(); ctx.arc(s.x,s.y,s.r,0,Math.PI*2);
      ctx.fillStyle = `rgba(255,220,180,${s.a})`;
      ctx.fill();
    }
    requestAnimationFrame(draw);
  }
  // Pause when tab hidden (Page Visibility API)
  document.addEventListener('visibilitychange', () => {
    running = !document.hidden;
    if(running && c.dataset.active !== 'false') requestAnimationFrame(draw);
  });
  window.addEventListener('resize',resize); resize(); draw();
})();

// ══════════ Starfield Toggle (CPU Saver) ══════════
document.getElementById('btn-stars')?.addEventListener('click', function() {
  const sf = document.getElementById('starfield');
  const isActive = sf.dataset.active !== 'false';
  sf.dataset.active = isActive ? 'false' : 'true';
  this.textContent = isActive ? '🌙' : '✨';
  this.classList.toggle('stars-off', isActive);
  this.title = isActive ? 'Turn stars on' : 'Turn stars off (CPU saver)';
});

// ══════════ Performance Mode Toggle ══════════
const perfToggle = document.getElementById('btn-perf');
let perfMode = localStorage.getItem('perf_mode') === 'true';
function applyPerfMode(on) {
  document.body.classList.toggle('perf-mode', on);
  perfToggle.textContent = on ? '🌀' : '⚡';
  perfToggle.title = on ? '🌀 Performance mode ON — all animations frozen' : '⚡ Performance mode OFF — full cosmic glow';
  localStorage.setItem('perf_mode', on);
  // Also auto-pause starfield when perf mode is on
  const sf = document.getElementById('starfield');
  const starsBtn = document.getElementById('btn-stars');
  if (on) {
    sf.dataset.active = 'false';
    if (starsBtn) { starsBtn.textContent = '🌙'; starsBtn.classList.add('stars-off'); }
  } else {
    // Only re-enable if we're on the home tab
    const activeTab = document.querySelector('.sidebar-nav-item.active');
    if (activeTab && activeTab.dataset.tab === 'tab-home') {
      sf.dataset.active = 'true';
      if (starsBtn) { starsBtn.textContent = '✨'; starsBtn.classList.remove('stars-off'); }
    }
  }
}
perfToggle?.addEventListener('click', () => {
  perfMode = !perfMode;
  applyPerfMode(perfMode);
});
// Restore saved preference on load
applyPerfMode(perfMode);

