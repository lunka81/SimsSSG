const API_URL = "http://localhost:8000/api/employee";

export type Permission = "Standard" | "Admin" | "Limited" | "Guest";

// Det som skickas till backend när en ny person läggs till
export type EmployeeCreate = {
  name: string;
  role: Permission;
  description: string | null;
  img: string; // bilden som data-URL: "data:image/jpeg;base64,..."
};

// Så som backend skickar tillbaka en person
export type Employee = {
  uuid: string;
  name: string;
  role: Permission;
  description: string | null;
  created_at: string;
  active: boolean;
};

// Kastar ett fel med ett begripligt meddelande om backend svarar med fel
async function checkResponse(response: Response, message: string) {
  if (!response.ok) {
    throw new Error(`${message} (${response.status}).`);
  }
}

// GET /api/employee/ hämtar alla personer
export async function getEmployees(): Promise<Employee[]> {
  const response = await fetch(`${API_URL}/`);
  await checkResponse(response, "Could not load persons");
  return response.json();
}

// GET /api/employee/{id} hämtar en person
export async function getEmployee(id: string): Promise<Employee> {
  const response = await fetch(`${API_URL}/${id}`);
  await checkResponse(response, "Could not load the person");
  return response.json();
}

// Adressen till personens bild, kan användas direkt i <img src={...} />
export function getEmployeeImageUrl(id: string): string {
  return `${API_URL}/${id}/image`;
}

// POST /api/employee/ lägger till en person
export async function createEmployee(employee: EmployeeCreate): Promise<Employee> {
  const response = await fetch(`${API_URL}/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(employee),
  });

  // 422 betyder att backend inte hittade något ansikte i bilden
  if (response.status === 422) {
    throw new Error("No face was found in the picture. Please try another picture.");
  }
  await checkResponse(response, "Could not save the person");
  return response.json();
}

// DELETE /api/employee/{id} tar bort en person
export async function deleteEmployee(id: string): Promise<void> {
  const response = await fetch(`${API_URL}/${id}`, { method: "DELETE" });
  await checkResponse(response, "Could not remove the person");
}

// En person med statistik från loggarna
export type EmployeeDetails = Employee & {
  last_seen: string | null;
  approved_count: number;
  denied_count: number;
};

// GET /api/employee/{id} hämtar en person med statistik
export async function getEmployeeDetails(id: string): Promise<EmployeeDetails> {
  const response = await fetch(`${API_URL}/${id}`);
  await checkResponse(response, "Could not load the person");
  return response.json();
}

// Det som kan ändras på en person. Alla fält är valfria
export type EmployeeUpdate = {
  name?: string;
  role?: Permission;
  description?: string | null;
  active?: boolean;
};

// PATCH /api/employee/{id} ändrar en eller flera uppgifter
export async function updateEmployee(id: string, changes: EmployeeUpdate): Promise<Employee> {
  const response = await fetch(`${API_URL}/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(changes),
  });
  await checkResponse(response, "Could not update the person");
  return response.json();
}
