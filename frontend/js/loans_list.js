const loanListRows = document.getElementById("loanListRows");
const loanListState = document.getElementById("loanListState");
const loanFilterButtons = document.querySelectorAll("#loanFilters button");

function getSelectedStatusFromQuery() {
    return new URLSearchParams(window.location.search).get("status") || "all";
}

function setActiveFilter(status) {
    loanFilterButtons.forEach((button) => {
        button.classList.toggle("active", button.dataset.status === status);
    });
}

async function loadLoanList(status = "all") {
    setActiveFilter(status);
    loanListState.textContent = "Loading loans...";

    try {
        const loans = await getLoans(status === "all" ? {} : { status });
        if (!loans.length) {
            loanListRows.innerHTML = "";
            loanListState.textContent = "No loans found for this filter.";
            return;
        }

        loanListState.textContent = "";
        loanListRows.innerHTML = loans.map((loan) => `
            <tr>
                <td><a class="inline-link" href="loans.html?loan_id=${loan.id}">${loan.id}</a></td>
                <td>${loan.customer_name}</td>
                <td>${loan.officer_name || "—"}</td>
                <td>${loan.amount}</td>
                <td><span class="status ${loan.status}">${loan.status}</span></td>
                <td>${loan.start_date}</td>
            </tr>
        `).join("");
    } catch (err) {
        loanListRows.innerHTML = "";
        loanListState.textContent = err.message;
    }
}

loanFilterButtons.forEach((button) => {
    button.addEventListener("click", () => loadLoanList(button.dataset.status));
});

loadLoanList(getSelectedStatusFromQuery());