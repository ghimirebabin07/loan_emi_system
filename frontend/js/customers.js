async function loadCustomers() {
    const rows = document.getElementById("customerRows");
    const customers = await getCustomers();
    rows.innerHTML = customers.map(c => `
        <tr>
            <td>${c.id}</td>
            <td>${c.name}</td>
            <td>${c.phone}</td>
            <td>${c.address || "—"}</td>
            <td><button class="delete" data-id="${c.id}">Delete</button></td>
        </tr>
    `).join("");
}

document.getElementById("customerForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const errorBox = document.getElementById("formError");
    errorBox.textContent = "";

    const data = {
        name: document.getElementById("name").value,
        phone: document.getElementById("phone").value,
        address: document.getElementById("address").value || null,
    };

    try {
        await createCustomer(data);
        e.target.reset();
        loadCustomers();
        // show success message
        errorBox.innerHTML = `<span class="success">Customer added successfully</span>`;
        setTimeout(() => { errorBox.innerHTML = ""; }, 3000);
    } catch (err) {
        errorBox.textContent = err.message;
    }
});

// event delegation: one listener on the table body handles every delete button,
// including ones that don't exist yet when the page first loads
document.getElementById("customerRows").addEventListener("click", async (e) => {
    if (!e.target.matches("button.delete")) return;

    const id = e.target.dataset.id;
    const row = e.target.closest("tr");
    const name = row.children[1].textContent;

    if (!confirm(`Delete customer "${name}" (#${id})? This cannot be undone.`)) return;

    try {
        await deleteCustomer(id);
        loadCustomers();
    } catch (err) {
        alert(err.message);
    }
});

loadCustomers();