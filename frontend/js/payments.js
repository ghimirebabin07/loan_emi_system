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
        resultBox.innerHTML = `
            <div class="card">
                <div class="label">Payment recorded for EMI #${result.emi_id}</div>
                <div class="value"><span class="status ${result.status}">${result.status.replace("_", " ")}</span></div>
            </div>
        `;
    } catch (err) {
        resultBox.innerHTML = `<div class="error">${err.message}</div>`;
    }
});