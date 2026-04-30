/* ── Main JavaScript — VoteSecure ──────────── */

// Auto-dismiss toast notifications after 4 seconds
document.addEventListener('DOMContentLoaded', () => {
    // Auto-dismiss toast notifications
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(toast => {
        setTimeout(() => { toast.style.display = 'none'; }, 4500);
    });
});

// CSRF token helper for AJAX requests
function getCookie(name) {
    let val = null;
    document.cookie.split(';').forEach(c => {
        c = c.trim();
        if (c.startsWith(name + '=')) val = decodeURIComponent(c.substring(name.length + 1));
    });
    return val;
}
const csrfToken = getCookie('csrftoken');

// Fetch wrapper with CSRF
function apiFetch(url, options = {}) {
    const defaults = {
        headers: { 'X-CSRFToken': csrfToken, 'Content-Type': 'application/json' },
        credentials: 'same-origin'
    };
    return fetch(url, { ...defaults, ...options });
}

// Countdown timer for elections
function startCountdown(elementId, endDate) {
    const el = document.getElementById(elementId);
    if (!el) return;
    const end = new Date(endDate).getTime();

    function update() {
        const now = Date.now();
        const diff = end - now;
        if (diff <= 0) { el.textContent = 'Election Ended'; return; }
        const d = Math.floor(diff / 86400000);
        const h = Math.floor((diff % 86400000) / 3600000);
        const m = Math.floor((diff % 3600000) / 60000);
        const s = Math.floor((diff % 60000) / 1000);
        el.textContent = d > 0 ? `${d}d ${h}h ${m}m` : `${h}h ${m}m ${s}s`;
    }
    update();
    setInterval(update, 1000);
}

// Number counter animation
function animateCounter(el, target, duration = 1500) {
    let start = 0;
    const step = target / (duration / 16);
    function tick() {
        start += step;
        if (start >= target) { el.textContent = target; return; }
        el.textContent = Math.floor(start);
        requestAnimationFrame(tick);
    }
    tick();
}
