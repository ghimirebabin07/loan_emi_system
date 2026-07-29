async function loadSummary() {
    const container = document.getElementById("summaryCards");
    try {
        const summary = await getSummary();
        container.innerHTML = `
            <div class="card">
                <div class="label">Total Active Loans</div>
                <div class="value">${summary.total_active_loans}</div>
            </div>
            <div class="card">
                <div class="label">Overdue EMIs</div>
                <div class="value">${summary.total_overdue_emis}</div>
            </div>
            <div class="card">
                <div class="label">Total Outstanding</div>
                <div class="value">Rs. ${summary.total_outstanding_amount}</div>
            </div>
        `;
    } catch (err) {
        container.innerHTML = `<div class="error">Could not load summary — is the backend running? (${err.message})</div>`;
    }
}

loadSummary(); 