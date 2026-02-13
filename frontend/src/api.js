/**
 * API client for EKIP backend.
 */
const BASE = "http://localhost:8000/api";

export async function login(email) {
    const res = await fetch(`${BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Login failed");
    }
    return res.json();
}

export async function search(token, query, departmentFilter = null) {
    const body = { query };
    if (departmentFilter) body.department_filter = departmentFilter;

    const res = await fetch(`${BASE}/search`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(body),
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Search failed");
    }
    return res.json();
}
