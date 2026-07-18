async function refreshNatalChartList() {
  const sel = document.getElementById('natal-chart-select');
  if(!sel) return;
  try {
    const charts = await loadJSON('/api/natal/charts', {});
    const curVal = sel.value;
    sel.innerHTML = '<option value="">Gigi (Default)</option>';
    charts.forEach(function(c) {
      const opt = document.createElement('option');
      opt.value = c.id;
      opt.textContent = c.name + ' (' + c.birth_date + ')';
      sel.appendChild(opt);
    });
    sel.value = String(currentNatalChartId || '');
  } catch(e) {
    console.warn('Failed to load chart list:', e);
  }
}

function natalShowSaveModal() {
  const d = currentNatalData;
  if(!d) return;
  // Parse date/time into form values
  let dateStr = d.birth_date || '';
  let timeStr = d.birth_time || '';
  let nameStr = d.name || '';
  let locStr = d.location || '';
  let latStr = String(d.latitude || d.lat || '-33.925');
  let lonStr = String(d.longitude || d.lon || '18.424');
  let tzStr = String(d.tz_offset || '2');

  const overlay = document.createElement('div');
  overlay.className = 'natal-modal-overlay';
  overlay.innerHTML =
    '<div class="natal-modal">' +
    '<h3>' + (currentNatalChartId ? '✏️ Edit Chart' : '💾 Save Chart') + '</h3>' +
    '<label>Chart Name</label>' +
    '<input id="natal-modal-name" value="' + esc(nameStr) + '" placeholder="e.g. Gigi">' +
    '<label>Birth Date</label>' +
    '<input id="natal-modal-date" type="date" value="' + dateStr + '">' +
    '<label>Birth Time (24h)</label>' +
    '<input id="natal-modal-time" type="time" value="' + timeStr + '">' +
    '<label>Latitude</label>' +
    '<input id="natal-modal-lat" type="number" step="any" value="' + latStr + '">' +
    '<label>Longitude</label>' +
    '<input id="natal-modal-lon" type="number" step="any" value="' + lonStr + '">' +
    '<label>Location Name</label>' +
    '<input id="natal-modal-location" value="' + esc(locStr) + '" placeholder="e.g. Cape Town">' +
    '<label>UTC Offset</label>' +
    '<input id="natal-modal-tz" type="number" step="0.5" value="' + tzStr + '">' +
    '<div class="natal-modal-buttons">' +
    '<button class="natal-modal-btn cancel" id="natal-modal-cancel">Cancel</button>' +
    '<button class="natal-modal-btn primary" id="natal-modal-confirm">' + (currentNatalChartId ? 'Update' : 'Save') + '</button>' +
    '</div></div>';
  document.body.appendChild(overlay);

  document.getElementById('natal-modal-cancel').addEventListener('click', function() {
    overlay.remove();
  });

  document.getElementById('natal-modal-confirm').addEventListener('click', async function() {
    const chartData = {
      name: document.getElementById('natal-modal-name').value || 'Unnamed',
      birth_date: document.getElementById('natal-modal-date').value,
      birth_time: document.getElementById('natal-modal-time').value,
      lat: parseFloat(document.getElementById('natal-modal-lat').value) || 0,
      lon: parseFloat(document.getElementById('natal-modal-lon').value) || 0,
      location: document.getElementById('natal-modal-location').value || '',
      tz_offset: parseFloat(document.getElementById('natal-modal-tz').value) || 2,
    };
    if(!chartData.birth_date || !chartData.birth_time) {
      alert('Please fill in date and time');
      return;
    }
    try {
      if(currentNatalChartId) {
        await fetch('/api/natal/chart/' + currentNatalChartId, {
          method:'PUT',
          headers:{'Content-Type':'application/json'},
          body:JSON.stringify(chartData)
        });
      } else {
        const res = await fetch('/api/natal/chart/save', {
          method:'POST',
          headers:{'Content-Type':'application/json'},
          body:JSON.stringify(chartData)
        });
        const data = await res.json();
        currentNatalChartId = data.id;
      }
      overlay.remove();
      await refreshNatalChartList();
      await loadNatal(currentNatalChartId);
    } catch(e) {
      alert('Failed to save chart: ' + e.message);
    }
  });
}

function initNatalCRUD() {
  const sel = document.getElementById('natal-chart-select');
  const btnNew = document.getElementById('natal-btn-new');
  const btnSave = document.getElementById('natal-btn-save');
  const btnDelete = document.getElementById('natal-btn-delete');

  if(sel) {
    sel.addEventListener('change', function() {
      const val = sel.value;
      if(val) {
        loadNatal(parseInt(val));
      } else {
        loadNatal(null);
      }
    });
  }
  if(btnNew) {
    btnNew.addEventListener('click', function() {
      currentNatalChartId = null;
      loadNatal(null);
      // Reset the select
      if(sel) sel.value = '';
    });
  }
  if(btnSave) {
    btnSave.addEventListener('click', natalShowSaveModal);
  }
  if(btnDelete) {
    btnDelete.addEventListener('click', async function() {
      if(!currentNatalChartId) {
        alert('No saved chart selected to delete.');
        return;
      }
      if(!confirm('Delete this saved chart? This cannot be undone.')) return;
      try {
        await fetch('/api/natal/chart/' + currentNatalChartId, {method:'DELETE'});
        currentNatalChartId = null;
        await refreshNatalChartList();
        await loadNatal(null);
      } catch(e) {
        alert('Failed to delete chart: ' + e.message);
      }
    });
  }

  // Load the chart list on init
  refreshNatalChartList();
}

// ══════════ Init ══════════
loadHome();
loadNatal();
initNatalCRUD();
document.getElementById('btn-refresh').addEventListener('click', loadHome);
document.getElementById('btn-notif').addEventListener('click', () => alert('🔔 Notifications coming soon!'));
});
