// ══════════ Init ══════════
loadHome();
loadNatal();
initNatalCRUD();
document.getElementById('btn-refresh').addEventListener('click', loadHome);
document.getElementById('btn-notif').addEventListener('click', () => alert('🔔 Notifications coming soon!'));
});
