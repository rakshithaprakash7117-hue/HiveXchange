/**
 * HiveXchange — Core Client Utilities & Session Synthetic Data Engine (hive.js)
 */
(function () {
  'use strict';
  // Utility Formatters
  window.HiveUtils = {
    formatCurrency: function (num) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(num);
    },
    formatPercent: function (num) {
      const prefix = num >= 0 ? '+' : '';
      return prefix + num.toFixed(2) + '%';
    },
    formatCrypto: function (num, symbol) {
      return num.toLocaleString('en-US', { minimumFractionDigits: 4, maximumFractionDigits: 4 }) + ' ' + symbol;
    }
  };
  /**
   * Deterministic Account Data Generator
   * Generates financial metrics bounded within plausible ranges once per session.
   */
  window.getHiveSessionData = function (isDecoy) {
    const storageKey = isDecoy ? 'hx_decoy_account_v1' : 'hx_user_account_v1';
    const cached = sessionStorage.getItem(storageKey);
    if (cached) {
      try {
        return JSON.parse(cached);
      } catch (e) {
        sessionStorage.removeItem(storageKey);
      }
    }
    // Seeded values for consistent simulation
    const baseValue = isDecoy ? 84250.75 : 34820.50;
    const availCash = isDecoy ? 7450.00 : 3240.25;
    const change24h = isDecoy ? 3.42 : -1.18;
    const pnl = isDecoy ? 14200.50 : 2840.10;
    const dataset = {
      portfolioTotal: baseValue,
      availableCash: availCash,
      change24h: change24h,
      unrealizedPnL: pnl,
      holdings: [
        { symbol: 'BTC', name: 'Bitcoin', amount: isDecoy ? 1.25 : 0.45, price: 62450.00, change: 2.15 },
        { symbol: 'ETH', name: 'Ethereum', amount: isDecoy ? 8.5 : 3.2, price: 3420.50, change: -0.85 },
        { symbol: 'SOL', name: 'Solana', amount: isDecoy ? 45.0 : 18.0, price: 145.20, change: 4.80 },
        { symbol: 'USDT', name: 'Tether USD', amount: availCash, price: 1.00, change: 0.01 },
        { symbol: 'LINK', name: 'Chainlink', amount: isDecoy ? 220.0 : 0.0, price: 16.80, change: 1.20 }
      ],
      transactions: [
        { type: 'Buy', asset: 'BTC', amount: '0.15 BTC', value: '$9,367.50', status: 'Completed', date: '2026-09-11 14:22' },
        { type: 'Deposit', asset: 'USDT', amount: '2,500 USDT', value: '$2,500.00', status: 'Completed', date: '2026-09-10 09:15' },
        { type: 'Withdrawal', asset: 'USDT', amount: isDecoy ? '12,500 USDT' : '500 USDT', value: isDecoy ? '$12,500.00' : '$500.00', status: isDecoy ? 'Pending' : 'Completed', date: '2026-09-12 18:40' },
        { type: 'Sell', asset: 'ETH', amount: '1.2 ETH', value: '$4,104.60', status: 'Completed', date: '2026-09-08 22:04' }
      ]
    };
    sessionStorage.setItem(storageKey, JSON.stringify(dataset));
    return dataset;
  };
})();
