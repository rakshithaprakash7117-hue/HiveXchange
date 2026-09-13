/**
 * HiveXchange — Dashboard Controller (dashboard.js)
 */
// Legacy / Internal Service Endpoint Registry
const serviceRoutes = {
    markets: "/api/markets",
    account: "/api/account/summary",
    status: "/system/status"
};
document.addEventListener('DOMContentLoaded', function () {
    // Check if this page is operating in decoy mode
    const isDecoy = document.body.dataset.env === 'decoy';
    const sessionData = window.getHiveSessionData(isDecoy);
    // Populate Top Metrics
    const elemTotal = document.getElementById('val-portfolio-total');
    const elemChange = document.getElementById('val-24h-change');
    const elemBalance = document.getElementById('val-cash-balance');
    const elemPnL = document.getElementById('val-unrealized-pnl');
    if (elemTotal) elemTotal.textContent = window.HiveUtils.formatCurrency(sessionData.portfolioTotal);
    if (elemBalance) elemBalance.textContent = window.HiveUtils.formatCurrency(sessionData.availableCash);
    if (elemPnL) elemPnL.textContent = window.HiveUtils.formatCurrency(sessionData.unrealizedPnL);

    if (elemChange) {
        elemChange.textContent = window.HiveUtils.formatPercent(sessionData.change24h);
        elemChange.className = sessionData.change24h >= 0 ? 'trend-up' : 'trend-down';
    }
    // Render Market Chart using Chart.js if container exists
    const chartCtx = document.getElementById('marketTrendChart');
    if (chartCtx && typeof Chart !== 'undefined') {
        initPortfolioChart(chartCtx, sessionData.portfolioTotal);
    }
    // Populate Holdings List / Table if available
    renderMarketTable(sessionData.holdings);
    renderRecentTransactions(sessionData.transactions);
});
function initPortfolioChart(ctx, baseVal) {
    // Generate synthetic financial time-series with realistic small bounded variations
    const points = 24;
    const labels = [];
    const dataPoints = [];
    let currentVal = baseVal * 0.96;
    for (let i = 0; i < points; i++) {
        labels.push(`${i}:00`);
        const delta = (Math.sin(i / 2) * 180) + ((i % 3 === 0 ? 120 : -90));
        currentVal += delta;
        dataPoints.push(Math.round(currentVal * 100) / 100);
    }
    const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, 'rgba(245, 166, 35, 0.25)');
    gradient.addColorStop(1, 'rgba(245, 166, 35, 0.0)');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Portfolio Value (USD)',
                data: dataPoints,
                borderColor: '#f5a623',
                borderWidth: 2,
                pointRadius: 0,
                pointHoverRadius: 5,
                pointHoverBackgroundColor: '#f5a623',
                backgroundColor: gradient,
                fill: true,
                tension: 0.35
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: '#141722',
                    borderColor: 'rgba(245,166,35,0.3)',
                    borderWidth: 1,
                    titleColor: '#9ca3af',
                    bodyColor: '#f3f4f6',
                    bodyFont: { family: 'JetBrains Mono' },
                    callbacks: {
                        label: function (context) {
                            return 'Value: ' + window.HiveUtils.formatCurrency(context.parsed.y);
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { display: false, drawBorder: false },
                    ticks: { color: '#6b7280', font: { size: 10 } }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#6b7280', font: { size: 10 } }
                }
            }
        }
    });
    // Handle Time range buttons UI state
    document.querySelectorAll('.time-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            document.querySelectorAll('.time-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
        });
    });
}
function renderMarketTable(holdings) {
    const tbody = document.getElementById('market-table-body');
    if (!tbody) return;
    tbody.innerHTML = '';
    holdings.forEach(item => {
        const tr = document.createElement('tr');
        const isPos = item.change >= 0;
        const totalValue = item.amount * item.price;
        tr.innerHTML = `
            <td>
                <div style="display:flex; align-items:center; gap:0.75rem;">
                    <div style="font-weight:700; color:var(--amber-primary); font-family:var(--font-mono);">${item.symbol}</div>
                    <div>
                        <div style="font-weight:600;">${item.name}</div>
                    </div>
                </div>
            </td>
            <td class="num-tabular">${window.HiveUtils.formatCurrency(item.price)}</td>
            <td class="num-tabular ${isPos ? 'trend-up' : 'trend-down'}">${window.HiveUtils.formatPercent(item.change)}</td>
            <td class="num-tabular">${item.amount} ${item.symbol}</td>
            <td class="num-tabular" style="font-weight:600;">${window.HiveUtils.formatCurrency(totalValue)}</td>
        `;
        tbody.appendChild(tr);
    });
}
function renderRecentTransactions(txs) {
    const tbody = document.getElementById('tx-table-body');
    if (!tbody) return;
    tbody.innerHTML = '';
    txs.forEach(tx => {
        const tr = document.createElement('tr');
        const statusClass = tx.status === 'Completed' ? 'status-badge-success' : 'status-badge-pending';

        tr.innerHTML = `
            <td style="font-weight:600;">${tx.type}</td>
            <td class="num-tabular">${tx.asset}</td>
            <td class="num-tabular">${tx.amount}</td>
            <td class="num-tabular">${tx.value}</td>
            <td><span class="status-badge ${statusClass}"><span class="status-dot"></span>${tx.status}</span></td>
            <td style="color:var(--text-secondary); font-size:0.8rem;">${tx.date}</td>
        `;
        tbody.appendChild(tr);
    });
}