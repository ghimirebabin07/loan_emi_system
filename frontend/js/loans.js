// Dropdowns removed — the form accepts numeric IDs directly.

document.getElementById("loanForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const errorBox = document.getElementById("loanFormError");
    errorBox.textContent = "";

    const data = {
        customer_id: Number(document.getElementById("customer_id").value),
        officer_id: Number(document.getElementById("officer_id").value),
        amount: Number(document.getElementById("amount").value),
        interest_rate: Number(document.getElementById("interest_rate").value),
        tenure_months: Number(document.getElementById("tenure_months").value),
    };

    try {
        const loan = await createLoan(data);
        document.getElementById("amount").value = "";
        document.getElementById("interest_rate").value = "";
        document.getElementById("tenure_months").value = "";
        document.getElementById("lookupId").value = loan.id;
        renderLoan(loan);
        const msg = document.getElementById("loanFormMessage");
        msg.innerHTML = `<div class="success">Loan created successfully (ID ${loan.id})</div>`;
        setTimeout(() => { msg.innerHTML = ""; }, 3000);
    } catch (err) {
        errorBox.textContent = err.message;
    }
});

document.getElementById("lookupForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = document.getElementById("lookupId").value;
    try {
        const loan = await getLoan(id);
        renderLoan(loan);
    } catch (err) {
        document.getElementById("emiRows").innerHTML =
            `<tr><td colspan="4" class="error">Loan not found</td></tr>`;
    }
});

async function renderLoan(loan) {
    const balance = await getBalance(loan.id);

    document.getElementById("loanSummary").innerHTML = `
        <div class="card"><div class="label">Loan ID</div><div class="value">${loan.id}</div></div>
        <div class="card"><div class="label">Amount</div><div class="value">Rs. ${loan.amount}</div></div>
        <div class="card"><div class="label">Outstanding</div><div class="value">Rs. ${balance.outstanding_balance}</div></div>
    `;

    document.getElementById("emiRows").innerHTML = loan.emis.map(e => `
        <tr>
            <td>${e.id}</td>
            <td>${e.due_date}</td>
            <td>${e.emi_amount}</td>
            <td><span class="status ${e.status}">${e.status.replace("_", " ")}</span></td>
        </tr>
    `).join("");
}

// no-op: dropdown population removed