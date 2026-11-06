import type { EmployeeCreate } from "./api/employees";

/** Address of the backend. Used by every request in the app. */
export const BACKEND_URL = "http://localhost:8000";

// Key that the token is stored under in sessionStorage
const TOKEN_KEY = "token";

/** Data sent to the backend when a new admin is created: a person plus login details. */
type AdminCreate = EmployeeCreate & {
        username: string,
        plain_password: string,
};

/**
 * Sends the username and password to the backend and saves the returned token.
 *
 * @param username The admin's username.
 * @param password The admin's password.
 * @returns true if the login succeeded, false if the username or password was wrong.
 * @throws Error if the backend cannot be reached or responds with another error.
 */
export async function login(username: string, password: string): Promise<boolean> {
    const response = await fetch(`${BACKEND_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
    });

    // 401 means wrong username or password
    if (response.status === 401) {
        return false;
    }
    if (!response.ok) {
        throw new Error(`Could not log in (${response.status}).`);
    }

    // The backend responds with { username, uuid, access_token }.
    // The token is saved and then sent with every request to the backend
    const data = await response.json();
    sessionStorage.setItem(TOKEN_KEY, data.access_token);
    return true;
}

/**
 * Creates a new admin user. Requires that the current user is logged in.
 *
 * @param admin The person's details together with a username and password.
 * @throws Error if the username is taken (409), no face was found in the picture (422)
 * or the backend responds with another error.
 */
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

/**
 * Returns the saved token.
 *
 * @returns The token, or null if no one is logged in.
 */
export function getToken(): string | null {
    return sessionStorage.getItem(TOKEN_KEY);
}

/** Returns true if a token is saved, which means that an admin is logged in. */
export function isLoggedIn(): boolean {
    return getToken() !== null;
}

/** Logs out by removing the saved token. */
export function logout(): void {
    sessionStorage.removeItem(TOKEN_KEY);
}
