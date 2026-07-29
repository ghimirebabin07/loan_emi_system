const BASE_URL = "http://127.0.0.1:8002";

async function apiGet(path) {
    const res = await fetch(`${BASE_URL}${path}`);
    if (!res.ok) throw new Error(`GET ${path} failed: ${res.status}`);
    return res.json();
}

async function apiPost(path, data) {
    const res = await fetch(`${BASE_URL}${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });
    if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `POST ${path} failed: ${res.status}`);
    }
    return res.json();
}

// ---- Customers ----
const getCustomers = () => apiGet("/customers/");
const createCustomer = (data) => apiPost("/customers/", data);

// ---- Officers ----
const getOfficers = () => apiGet("/officers/");

// ---- Loans ----
const getLoan = (id) => apiGet(`/loans/${id}`);
const createLoan = (data) => apiPost("/loans/", data);
const getBalance = (id) => apiGet(`/loans/${id}/balance`);

// ---- Payments ----
const recordPayment = (data) => apiPost("/payments/", data);

// ---- Dashboard ----
const getSummary = () => apiGet("/dashboard/summary");