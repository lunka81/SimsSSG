const ADMIN_USERNAME = "admin";
const ADMIN_PASSWORD = "admin123";

export function login(username: string, password: string): boolean {
    if (username !== ADMIN_USERNAME || password !== ADMIN_PASSWORD) {
        return false;
    }
    sessionStorage.setItem("isAdmin", "true");
    return true;
}

export function isLoggedIn(): boolean {
    return sessionStorage.getItem("isAdmin") === "true";
}

export function logout(): void {
    sessionStorage.removeItem("isAdmin");
}