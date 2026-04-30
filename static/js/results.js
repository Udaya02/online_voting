/* ── Results Page JavaScript — Chart.js + Live Polling ──────────── */

let resultsChart = null;

document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('results-chart');
    if (!canvas) return;

    const electionId = canvas.dataset.electionId;
    const isActive = canvas.dataset.isActive === 'true';

    // Initialize chart
    initChart(canvas);
    fetchResults(electionId);

    // Poll every 5 seconds if election is active
    if (isActive) {
        setInterval(() => fetchResults(electionId), 5000);
    }

    // Animate result bars
    setTimeout(animateBars, 300);
});

function initChart(canvas) {
    const ctx = canvas.getContext('2d');
    resultsChart = new Chart(ctx, {
        type: 'doughnut',
        data: { labels: [], datasets: [{ data: [], backgroundColor: [], borderWidth: 0 }] },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: {
                legend: { position: 'bottom', labels: { color: '#475569', padding: 16, font: { family: 'Inter' } } }
            }
        }
    });
}

function fetchResults(electionId) {
    fetch(`/api/election/${electionId}/results/`)
        .then(r => r.json())
        .then(data => {
            updateChart(data.candidates);
            updateBars(data.candidates);
            updateTotalVotes(data.election.total_votes);
        })
        .catch(err => console.error('Error fetching results:', err));
}

const COLORS = ['#4f6ef7','#3b82f6','#16a34a','#d97706','#dc2626','#7c3aed','#db2777','#0d9488','#ea580c','#0891b2'];

function updateChart(candidates) {
    if (!resultsChart) return;
    resultsChart.data.labels = candidates.map(c => c.name);
    resultsChart.data.datasets[0].data = candidates.map(c => c.votes);
    resultsChart.data.datasets[0].backgroundColor = candidates.map((_, i) => COLORS[i % COLORS.length]);
    resultsChart.update('none');
}

function updateBars(candidates) {
    candidates.forEach((c, i) => {
        const fill = document.getElementById(`bar-fill-${c.id}`);
        const pct = document.getElementById(`bar-pct-${c.id}`);
        const votes = document.getElementById(`bar-votes-${c.id}`);
        if (fill) fill.style.width = `${c.percentage}%`;
        if (pct) pct.textContent = `${c.percentage}%`;
        if (votes) votes.textContent = `${c.votes} votes`;
    });
}

function updateTotalVotes(total) {
    const el = document.getElementById('total-votes-count');
    if (el) el.textContent = total;
}

function animateBars() {
    document.querySelectorAll('.result-bar-fill').forEach(bar => {
        const width = bar.style.width;
        bar.style.width = '0%';
        setTimeout(() => { bar.style.width = width; }, 100);
    });
}
