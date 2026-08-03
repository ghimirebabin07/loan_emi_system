const BASE_URL = "https://loan-emi-system.onrender.com";

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

async function apiDelete(path) {
    const res = await fetch(`${BASE_URL}${path}`, { method: "DELETE" });
    if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `DELETE ${path} failed: ${res.status}`);
    }
    // a successful DELETE often returns no body (204 No Content) — guard against parsing nothing as JSON
    return res.status === 204 ? null : res.json().catch(() => null);
}

// ---- Customers ----
const getCustomers = () => apiGet("/customers/");
const createCustomer = (data) => apiPost("/customers/", data);
const deleteCustomer = (id) => apiDelete(`/customers/${id}`);

// ---- Officers ----
const getOfficers = () => apiGet("/officers/");
const createOfficer = (data) => apiPost("/officers/", data);
const deleteOfficer = (id) => apiDelete(`/officers/${id}`);

// ---- Loans ----
const getLoan = (id) => apiGet(`/loans/${id}`);
const getLoans = (params = {}) => {
    const query = new URLSearchParams();
    if (params.status) query.set("status", params.status);
    const suffix = query.toString() ? `?${query.toString()}` : "";
    return apiGet(`/loans/${suffix}`);
};
const createLoan = (data) => apiPost("/loans/", data);
const getBalance = (id) => apiGet(`/loans/${id}/balance`);
const getCustomerLoanHistory = (customerId) => apiGet(`/customers/${customerId}/loans`);

// ---- Payments ----
const recordPayment = (data) => apiPost("/payments/", data);

// ---- Dashboard ----
const getSummary = () => apiGet("/dashboard/summary");