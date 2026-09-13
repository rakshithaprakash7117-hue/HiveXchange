/**
 * HiveXchange — Wallet Controller (wallet.js)
 */
document.addEventListener('DOMContentLoaded', function () {
    const isDecoy = document.body.dataset.env === 'decoy' || true;
    const sessionData = window.getHiveSessionData(isDecoy);
    // Render Balances
    const valWalletTotal = document.getElementById('val-wallet-total');
    if (valWalletTotal) {
        valWalletTotal.textContent = window.HiveUtils.formatCurrency(sessionData.portfolioTotal);
    }
    // Modal Trigger Setup
    setupWalletModals();
    setupAddressCopier();
});
function setupWalletModals() {
    const modal = document.getElementById('walletActionModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBodyContent');
    const closeBtn = document.getElementById('closeModalBtn');
    if (!modal) return;
    const openModal = (title, contentHtml) => {
        if (modalTitle) modalTitle.textContent = title;
        if (modalBody) modalBody.innerHTML = contentHtml;
        modal.classList.add('active');
    };
    if (closeBtn) {
        closeBtn.addEventListener('click', () => modal.classList.remove('active'));
    }
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.classList.remove('active');
    });
    const btnDeposit = document.getElementById('btnDepositAction');
    const btnWithdraw = document.getElementById('btnWithdrawAction');
    const btnTransfer = document.getElementById('btnTransferAction');
    if (btnDeposit) {
        btnDeposit.addEventListener('click', () => {
            openModal('Deposit Assets', `
                <p style="color:var(--text-secondary); margin-bottom:1rem; font-size:0.9rem;">
                    Select asset and send only supported digital tokens to your assigned custody address.
                </p>
                <div class="form-group">
                    <label class="form-label">Network / Token</label>
                    <select class="form-input">
                        <option>BTC — Bitcoin Network</option>
                        <option>ETH — Ethereum ERC-20</option>
                        <option>USDT — Tether USD (TRC-20 / ERC-20)</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Deposit Address</label>
                    <div style="display:flex; gap:0.5rem;">
                        <input type="text" class="form-input num-tabular" value="0x7A4F89b1C9024eD849a204859d01228459a992CD" readonly>
                        <button class="btn btn-secondary" onclick="navigator.clipboard.writeText('0x7A4F89b1C9024eD849a204859d01228459a992CD')">Copy</button>
                    </div>
                </div>
            `);
        });
    }
    if (btnWithdraw) {
        btnWithdraw.addEventListener('click', () => {
            openModal('Withdrawal Request', `
                <div class="form-group">
                    <label class="form-label">Destination Address</label>
                    <input type="text" class="form-input num-tabular" placeholder="Enter recipient wallet address">
                </div>
                <div class="form-group">
                    <label class="form-label">Amount (USDT)</label>
                    <input type="number" class="form-input num-tabular" placeholder="0.00" value="12500">
                </div>
                <div style="background-color:var(--amber-glow); border:1px solid var(--border-accent); padding:0.85rem; border-radius:var(--radius-md); font-size:0.85rem; color:var(--amber-primary); margin-bottom:1.5rem;">
                    Multi-Sig Approval Required: Withdrawals exceeding $10,000 USD require secondary hardware authorization.
                </div>
                <button class="btn btn-primary" style="width:100%;">Submit Authorization</button>
            `);
        });
    }
    if (btnTransfer) {
        btnTransfer.addEventListener('click', () => {
            openModal('Internal Transfer', `
                <div class="form-group">
                    <label class="form-label">From Vault Account</label>
                    <input type="text" class="form-input" value="Main Cold Vault (HX-8942)" readonly>
                </div>
                <div class="form-group">
                    <label class="form-label">To Sub-Account</label>
                    <select class="form-input">
                        <option>Spot Trading Account</option>
                        <option>NFT Vault Sub-Wallet</option>
                    </select>
                </div>
                <button class="btn btn-primary" style="width:100%;">Confirm Transfer</button>
            `);
        });
    }
}
function setupAddressCopier() {
    document.querySelectorAll('.copy-addr-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const addr = this.dataset.addr || '0x7A4F...92CD';
            navigator.clipboard.writeText(addr);
            const origText = this.textContent;
            this.textContent = 'Copied!';
            setTimeout(() => { this.textContent = origText; }, 1500);
        });
    });
}
