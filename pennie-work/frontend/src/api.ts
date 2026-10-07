// Adressen till FastAPI-backenden. Kan ändras med VITE_API_URL i en .env-fil
const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export type Permission = "Standard" | "Admin" | "Limited";

// Det som skickas till POST /api/employee/
export type EmployeeCreate = {
    name: string;
    permission: Permission;
    description: string | null;
    // Bilden som data-URL: "data:image/jpeg;base64,..."
    img: string;
};

// Det som backenden svarar med (EmployeeResponse)
export type Employee = {
    uuid: string;
    name: string;
    permission: Permission;
    description: string | null;
};

// En rad i personens logg (EmployeeLogResponse)
export type EmployeeLog = {
    uuid: string;
    employee_uuid: string;
    timestamp: string;
    approved: boolean;
};

// Det som GET /api/employee/{uuid} svarar med (EmployeeDetailResponse)
export type EmployeeDetail = Employee & {
    employee_logs: EmployeeLog[];
};

// Kastar ett Error med FastAPI:s felmeddelande om anropet misslyckades
async function checkResponse(response: Response): Promise<void> {
    if (!response.ok) {
        // FastAPI skickar felet i "detail"
        const error = await response.json().catch(() => null);
        const detail = typeof error?.detail === "string" ? error.detail : `Request failed (${response.status})`;
        throw new Error(detail);
    }
}

export async function getEmployees(): Promise<Employee[]> {
    const response = await fetch(`${API_URL}/api/employee/`);
    await checkResponse(response);
    return response.json();
}

export async function getEmployee(uuid: string): Promise<EmployeeDetail> {
    const response = await fetch(`${API_URL}/api/employee/${uuid}`);
    await checkResponse(response);
    return response.json();
}

// Adressen till personens bild, kan användas direkt i <img src="...">
export function employeeImageUrl(uuid: string): string {
    return `${API_URL}/api/employee/${uuid}/image`;
}

export async function deleteEmployee(uuid: string): Promise<void> {
    const response = await fetch(`${API_URL}/api/employee/${uuid}`, {
        method: "DELETE",
    });
    // Backenden svarar 204 utan innehåll, så det finns inget att läsa
    await checkResponse(response);
}

export async function createEmployee(employee: EmployeeCreate): Promise<Employee> {
    const response = await fetch(`${API_URL}/api/employee/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(employee),
    });
    await checkResponse(response);
    return response.json();
}

// Läser in en fil som data-URL (Base64) så att den kan skickas som JSON
export function fileToDataUrl(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result as string);
        reader.onerror = () => reject(reader.error);
        reader.readAsDataURL(file);
    });
}
