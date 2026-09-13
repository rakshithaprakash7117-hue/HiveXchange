/**
 * HiveXchange — Defender SOC Monitoring Console Script (monitor.js)
 */
document.addEventListener('DOMContentLoaded', function () {
    // Initialize SOC Telemetry Charts if Chart.js is available
    const ctxLogins = document.getElementById('chartLoginOutcomes');
    if (ctxLogins && typeof Chart !== 'undefined') {
        initLoginOutcomesChart(ctxLogins);
    }
    const ctxEvents = document.getElementById('chartSecurityEvents');
    if (ctxEvents && typeof Chart !== 'undefined') {
        initSecurityEventsChart(ctxEvents);
    }
});
function initLoginOutcomesChart(ctx) {
    // Parse counts from HTML data attributes or fallback metrics
    const failed = parseInt(ctx.dataset.failed || '0', 10);
    const valid = parseInt(ctx.dataset.valid || '0', 10);
    const decoy = parseInt(ctx.dataset.decoy || '0', 10);
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Failed Attempts', 'Valid Users', 'Decoy Diversions'],
            datasets: [{
                data: [failed || 14, valid || 3, decoy || 8],
                backgroundColor: ['#ef4444', '#10b981', '#f5a623'],
                borderColor: '#0e111a',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#94a3b8', font: { family: 'Inter', size: 11 } }
                }
            },
            cutout: '70%'
        }
    });
}
function initSecurityEventsChart(ctx) {
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['HARD_PATH', 'SENSITIVE', 'CANARY', 'DECOY_ACC', 'WALLET'],
            datasets: [{
                label: 'Security Probe Count',
                data: [12, 19, 5, 8, 4],
                backgroundColor: ['#ef4444', '#eab308', '#a855f7', '#f5a623', '#06b6d4'],
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: '#64748b', font: { family: 'JetBrains Mono', size: 10 } }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#64748b', font: { family: 'JetBrains Mono', size: 10 } }
                }
            }
        }
    });
}
