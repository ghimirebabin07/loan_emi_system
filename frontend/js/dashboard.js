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

async function loadCompletedLoans() {
    const rows = document.getElementById("completedLoanRows");
    const state = document.getElementById("completedLoanState");

    if (!rows || !state) return;

    try {
        const loans = await getLoans({ status: "completed" });
        if (!loans.length) {
            rows.innerHTML = "";
            state.textContent = "No completed loans yet.";
            return;
        }

        state.textContent = "";
        rows.innerHTML = loans.map((loan) => `
            <tr>
                <td><a class="inline-link" href="pages/loans.html?loan_id=${loan.id}">${loan.id}</a></td>
                <td>${loan.customer_name}</td>
                <td>${loan.officer_name || "—"}</td>
                <td>${loan.amount}</td>
                <td><span class="status ${loan.status}">${loan.status}</span></td>
                <td>${loan.start_date}</td>
            </tr>
        `).join("");
    } catch (err) {
        state.textContent = err.message;
    }
}

loadSummary();
loadCompletedLoans();