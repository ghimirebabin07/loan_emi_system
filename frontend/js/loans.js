const customerSelect = document.getElementById("customer_id");
const officerSelect = document.getElementById("officer_id");
const customerHistoryRows = document.getElementById("customerHistoryRows");
const customerHistoryState = document.getElementById("customerHistoryState");

function getLoanIdFromQuery() {
    return new URLSearchParams(window.location.search).get("loan_id");
}

function renderLoanRows(rows) {
    if (!rows.length) {
        customerHistoryRows.innerHTML = "";
        customerHistoryState.textContent = "No loan history found for this customer yet.";
        return;
    }

    customerHistoryState.textContent = "";
    customerHistoryRows.innerHTML = rows.map((loan) => `
        <tr>
            <td><a class="inline-link" href="loans.html?loan_id=${loan.id}">${loan.id}</a></td>
            <td>${loan.amount}</td>
            <td><span class="status ${loan.status}">${loan.status.replace("_", " ")}</span></td>
            <td>${loan.start_date}</td>
            <td>${loan.officer_name || "—"}</td>
        </tr>
    `).join("");
}

async function loadCustomersForCreateLoan() {
    const customers = await getCustomers();
    customerSelect.innerHTML = ['<option value="">Select a customer</option>']
        .concat(customers.map((customer) => `<option value="${customer.id}">${customer.id} - ${customer.name}</option>`))
        .join("");
}

async function loadOfficersForCreateLoan() {
    const officers = await getOfficers();
    officerSelect.innerHTML = ['<option value="">Select an officer</option>']
        .concat(officers.map((officer) => `<option value="${officer.id}">${officer.id} - ${officer.name}</option>`))
        .join("");
}

async function loadCustomerHistory(customerId) {
    if (!customerId) {
        customerHistoryRows.innerHTML = "";
        customerHistoryState.textContent = "Select a customer to view loan history.";
        return;
    }

    customerHistoryState.textContent = "Loading history...";
    try {
        const rows = await getCustomerLoanHistory(customerId);
        renderLoanRows(rows);
    } catch (err) {
        customerHistoryRows.innerHTML = "";
        customerHistoryState.textContent = err.message;
    }
}

document.getElementById("loanForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const errorBox = document.getElementById("loanFormError");
    errorBox.textContent = "";

    const data = {
        customer_id: Number(customerSelect.value),
        officer_id: Number(officerSelect.value),
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
        const url = new URL(window.location.href);
        url.searchParams.set("loan_id", loan.id);
        window.history.replaceState({}, "", url);
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
        <div class="card"><div class="label">Status</div><div class="value"><span class="status ${loan.status}">${loan.status}</span></div></div>
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

customerSelect.addEventListener("change", () => loadCustomerHistory(customerSelect.value));

document.addEventListener("DOMContentLoaded", async () => {
    await Promise.all([
        loadCustomersForCreateLoan(),
        loadOfficersForCreateLoan(),
    ]);

    const selectedLoanId = getLoanIdFromQuery();
    if (selectedLoanId) {
        document.getElementById("lookupId").value = selectedLoanId;
        try {
            const loan = await getLoan(selectedLoanId);
            renderLoan(loan);
        } catch (err) {
            document.getElementById("emiRows").innerHTML = `<tr><td colspan="4" class="error">${err.message}</td></tr>`;
        }
    }
});