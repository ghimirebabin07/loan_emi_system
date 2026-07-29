async function loadOfficers() {
    const rows = document.getElementById("officerRows");
    const officers = await getOfficers();
    rows.innerHTML = officers.map(o => `
        <tr>
            <td>${o.id}</td>
            <td>${o.name}</td>
            <td>${o.branch || "—"}</td>
            <td><button class="delete" data-id="${o.id}">Delete</button></td>
        </tr>
    `).join("");
}

document.getElementById("officerForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const errorBox = document.getElementById("formError");
    errorBox.textContent = "";

    const data = {
        name: document.getElementById("name").value,
        branch: document.getElementById("branch").value,
    };

    try {
        await createOfficer(data);
        e.target.reset();
        loadOfficers();
        // show success message
        errorBox.innerHTML = `<span class="success">Officer added successfully</span>`;
        setTimeout(() => { errorBox.innerHTML = ""; }, 3000);
    } catch (err) {
        errorBox.textContent = err.message;
    }
});

document.getElementById("officerRows").addEventListener("click", async (e) => {
    if (!e.target.matches("button.delete")) return;

    const id = e.target.dataset.id;
    const row = e.target.closest("tr");
    const name = row.children[1].textContent;

    if (!confirm(`Delete officer "${name}" (#${id})? This cannot be undone.`)) return;

    try {
        await deleteOfficer(id);
        loadOfficers();
    } catch (err) {
        alert(err.message);
    }
});

loadOfficers(); 