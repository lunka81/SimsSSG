import { BACKEND_URL, getToken, logout } from "../auth";

const API_URL = `${BACKEND_URL}/api/employee`;

export type Permission = "Standard" | "Admin" | "Limited";

// Det som skickas till backend när en ny person läggs till
export type EmployeeCreate = {
  name: string;
  permission: Permission;
  description: string | null;
  img: string; // bilden som data-URL: "data:image/jpeg;base64,..."
};

// Så som backend skickar tillbaka en person
export type Employee = {
  uuid: string;
  name: string;
  permission: Permission;
  description: string | null;
};

// En passage vid dörren, från loggtabellen
export type EmployeeLog = {
  uuid: string;
  employee_uuid: string;
  timestamp: string;
  approved: boolean;
};

// En person med alla sina passager
export type EmployeeDetails = Employee & {
  employee_logs: EmployeeLog[];
};

// Alla anrop till /api/employee kräver att token skickas med i headern Authorization
function authHeaders(): HeadersInit {
  return { Authorization: `Bearer ${getToken()}` };
}

// Kastar ett fel med ett begripligt meddelande om backend svarar med fel
async function checkResponse(response: Response, message: string) {
  // 401 betyder att token saknas eller har gått ut (den gäller i en timme)
  if (response.status === 401) {
    logout();
    throw new Error("Your session has expired. Please log in again.");
  }
  if (!response.ok) {
    throw new Error(`${message} (${response.status}).`);
  }
}

// GET /api/employee/ hämtar alla personer
export async function getEmployees(): Promise<Employee[]> {
  const response = await fetch(`${API_URL}/`, { headers: authHeaders() });
  await checkResponse(response, "Could not load persons");
  return response.json();
}

// GET /api/employee/{id} hämtar en person med alla passager
export async function getEmployeeDetails(id: string): Promise<EmployeeDetails> {
  const response = await fetch(`${API_URL}/${id}`, { headers: authHeaders() });
  await checkResponse(response, "Could not load the person");
  return response.json();
}

// GET /api/employee/{id}/image hämtar bilden.
// <img src> kan inte skicka med token, så bilden hämtas med fetch och görs om till
// en lokal adress (blob:...) som kan visas i <img>. Den ska tas bort med
// URL.revokeObjectURL när den inte behövs längre.
export async function getEmployeeImage(id: string): Promise<string> {
  const response = await fetch(`${API_URL}/${id}/image`, { headers: authHeaders() });
  await checkResponse(response, "Could not load the picture");
  const blob = await response.blob();
  return URL.createObjectURL(blob);
}

// POST /api/employee/ lägger till en person
export async function createEmployee(employee: EmployeeCreate): Promise<Employee> {
  const response = await fetch(`${API_URL}/`, {
    method: "POST",
    headers: { ...authHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify(employee),
  });

  // 422 betyder att backend inte kunde använda bilden, t.ex. inget ansikte
  if (response.status === 422) {
    throw new Error("No face was found in the picture. Please try another picture.");
  }
  await checkResponse(response, "Could not save the person");
  return response.json();
}

// DELETE /api/employee/{id} tar bort en person
export async function deleteEmployee(id: string): Promise<void> {
  const response = await fetch(`${API_URL}/${id}`, {
    method: "DELETE",
    headers: authHeaders(),
  });
  await checkResponse(response, "Could not remove the person");
}
