import { BACKEND_URL, getToken, logout } from "../auth";

const API_URL = `${BACKEND_URL}/api/employee`;

export type Permission = "Standard" | "Admin" | "Limited";

export const PERMISSIONS: readonly Permission[] = [
  "Standard",
  "Admin",
  "Limited",
];

// Data för att skapa en person.
export type EmployeeCreate = {
  name: string;
  permission: Permission;
  description: string | null;
  img: string;
};

// Data för att uppdatera en person.
// Bara fälten som skickas ändras.
export type EmployeeUpdate = {
  name?: string;
  permission?: Permission;
  description?: string | null;
  img?: string;
};

// Personuppgifter från backend.
export type Employee = {
  uuid: string;
  name: string;
  permission: Permission;
  description: string | null;
};

// En passage vid dörren.
export type EmployeeLog = {
  uuid: string;
  employee_uuid: string;
  timestamp: string;
  camera_id: string;
  detection_confidence: number;
  face_width: number;
  face_height: number;
};

export type EmployeeDetails = Employee & {
  employee_logs: EmployeeLog[];
};

function authHeaders(): Record<string, string> {
  return {
    Authorization: `Bearer ${getToken()}`,
  };
}

async function checkResponse(
  response: Response,
  message: string
): Promise<void> {
  if (response.status === 401) {
    logout();
    throw new Error(
      "Your session has expired. Please log in again."
    );
  }

  if (response.ok) {
    return;
  }

  // Försök visa backendens förklaring.
  let detailMessage = "";

  try {
    const body = await response.json();
    const detail: unknown = body.detail;

    if (typeof detail === "string") {
      detailMessage = detail;
    } else if (Array.isArray(detail)) {
      // FastAPI:s valideringsfel.
      detailMessage = detail
        .map((item: unknown) => {
          if (
            typeof item === "object" &&
            item !== null &&
            "msg" in item &&
            typeof item.msg === "string"
          ) {
            return item.msg;
          }

          return "";
        })
        .filter(Boolean)
        .join("; ");
    }
  } catch {
    // Använd standardmeddelandet om svaret inte är JSON.
  }

  throw new Error(
    detailMessage || `${message} (${response.status}).`
  );
}

// GET /api/employee/
export async function getEmployees(): Promise<Employee[]> {
  const response = await fetch(`${API_URL}/`, {
    headers: authHeaders(),
  });

  await checkResponse(response, "Could not load persons");
  return response.json();
}

// GET /api/employee/{id}
export async function getEmployeeDetails(
  id: string
): Promise<EmployeeDetails> {
  const response = await fetch(`${API_URL}/${id}`, {
    headers: authHeaders(),
  });

  await checkResponse(response, "Could not load the person");
  return response.json();
}

// GET /api/employee/{id}/image
// Anroparen ansvarar för URL.revokeObjectURL när bilden inte behövs.
export async function getEmployeeImage(
  id: string
): Promise<string> {
  const response = await fetch(`${API_URL}/${id}/image`, {
    headers: authHeaders(),
  });

  await checkResponse(response, "Could not load the picture");

  const blob = await response.blob();
  return URL.createObjectURL(blob);
}

// POST /api/employee/
export async function createEmployee(
  employee: EmployeeCreate
): Promise<Employee> {
  const response = await fetch(`${API_URL}/`, {
    method: "POST",
    headers: {
      ...authHeaders(),
      "Content-Type": "application/json",
    },
    body: JSON.stringify(employee),
  });

  await checkResponse(response, "Could not save the person");
  return response.json();
}

// PATCH /api/employee/{id}
export async function updateEmployee(
  id: string,
  changes: EmployeeUpdate
): Promise<Employee> {
  const response = await fetch(`${API_URL}/${id}`, {
    method: "PATCH",
    headers: {
      ...authHeaders(),
      "Content-Type": "application/json",
    },
    body: JSON.stringify(changes),
  });

  await checkResponse(response, "Could not update the person");
  return response.json();
}

// DELETE /api/employee/{id}
export async function deleteEmployee(id: string): Promise<void> {
  const response = await fetch(`${API_URL}/${id}`, {
    method: "DELETE",
    headers: authHeaders(),
  });

  await checkResponse(response, "Could not remove the person");
}

export async function getEmployeeLogs(limit = 30): Promise<EmployeeLog[]> {
  const response = await fetch(`${BACKEND_URL}/api/employee_logs/?limit=${limit}`, { headers: authHeaders() });
  await checkResponse(response, "Could not load logs");
  return response.json();
}