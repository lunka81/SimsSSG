import type { EmployeeCreate } from "./api/employees";

// Adressen till backend. Används av alla anrop i appen
export const BACKEND_URL = "http://localhost:8000";

// Namnet som token sparas under i sessionStorage
const TOKEN_KEY = "token";
type AdminCreate = EmployeeCreate & {
        username: string,
        plain_password: string,
};

// Skickar användarnamn och lösenord till backend.
// Returnerar true om inloggningen lyckades och false vid fel användarnamn eller lösenord.
// Kastar ett fel om backend inte går att nå eller svarar med något annat fel.
export async function login(username: string, password: string): Promise<boolean> {
    const response = await fetch(`${BACKEND_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
    });

    // 401 betyder fel användarnamn eller lösenord
    if (response.status === 401) {
        return false;
    }
    if (!response.ok) {
        throw new Error(`Could not log in (${response.status}).`);
    }

    // Backend svarar med { username, uuid, access_token }.
    // Token sparas och skickas sedan med i varje anrop till backend
    const data = await response.json();
    sessionStorage.setItem(TOKEN_KEY, data.access_token);
    return true;
}

export async function registerAdmin(admin: AdminCreate): Promise<void> {
    const response = await fetch(`${BACKEND_URL}/auth/register`, {
        method: "POST",
        headers: { Authorization: `Bearer ${getToken()}`, "Content-Type": "application/json" },
        body: JSON.stringify(admin),
    });
    if (response.status === 409) {
        throw new Error("This username is already taken. Please choose another one.");
    }
    if (response.status === 422) {
        throw new Error("No face was found in the picture. Please try another picture.");
    }
    if (!response.ok) {
        throw new Error(`Could not create admin (${response.status}).`);
    }
}

// Ger tillbaka den sparade token, eller null om man inte är inloggad
export function getToken(): string | null {
    return sessionStorage.getItem(TOKEN_KEY);
}

export function isLoggedIn(): boolean {
    return getToken() !== null;
}

export function logout(): void {
    sessionStorage.removeItem(TOKEN_KEY);
}