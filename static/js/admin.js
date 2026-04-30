/* ── Admin Dashboard JavaScript ──────────── */

document.addEventListener('DOMContentLoaded', () => {
    // Animate stat counters
    document.querySelectorAll('[data-count]').forEach(el => {
        const target = parseInt(el.dataset.count);
        animateCounter(el, target);
    });

    // Refresh admin stats every 15 seconds
    const statsContainer = document.getElementById('admin-stats');
    if (statsContainer) {
        setInterval(refreshAdminStats, 15000);
    }

    // Delete confirmation
    document.querySelectorAll('.delete-form').forEach(form => {
        form.addEventListener('submit', (e) => {
            if (!confirm('Are you sure you want to delete this? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
});

function refreshAdminStats() {
    fetch('/api/admin/stats/')
        .then(r => r.json())
        .then(data => {
            const map = {
                'stat-total-elections': data.total_elections,
                'stat-active-elections': data.active_elections,
                'stat-total-votes': data.total_votes,
                'stat-total-voters': data.total_voters,
            };
            Object.entries(map).forEach(([id, val]) => {
                const el = document.getElementById(id);
                if (el) el.textContent = val;
            });
        })
        .catch(() => {});
}
