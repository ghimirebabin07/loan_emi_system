document.getElementById("paymentForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const resultBox = document.getElementById("paymentResult");
    resultBox.innerHTML = "";

    const data = {
        emi_id: Number(document.getElementById("emi_id").value),
        amount_paid: Number(document.getElementById("amount_paid").value),
        payment_mode: document.getElementById("payment_mode").value,
    };

    try {
        const result = await recordPayment(data);
        e.target.reset();
        const message = result.message || "Payment recorded.";
        const scheduleLink = result.loan_id
            ? `<a class="inline-link" href="loans.html?loan_id=${result.loan_id}">View updated loan schedule</a>`
            : "";
        resultBox.innerHTML = `
            <div class="card">
                <div class="label">${message}</div>
                <div class="value">EMI #${result.emi_id ?? ""}</div>
                <div class="meta">Loan #${result.loan_id ?? ""}${result.loan_status ? ` · ${result.loan_status}` : ""}</div>
                ${scheduleLink}
            </div>
        `;
    } catch (err) {
        resultBox.innerHTML = `<div class="error">${err.message}</div>`;
    }
});