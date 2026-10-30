import { BACKEND_URL, getToken, logout } from "../auth";

const API_URL = `${BACKEND_URL}/api/employee`;

/** The access levels a person can have. */
export type Permission = "Standard" | "Admin" | "Limited";

/** Data sent to the backend when a new person is added. */
export type EmployeeCreate = {
  name: string;
  permission: Permission;
  /** Shown as "Department" in the interface. */
  description: string | null;
  /** The picture as a data URL: "data:image/jpeg;base64,..." */
  img: string;
};

/** A person as the backend sends it back. */
export type Employee = {
  uuid: string;
  name: string;
  permission: Permission;
  description: string | null;
};

/** One entry at the door, from the log table. */
export type EmployeeLog = {
  uuid: string;
  employee_uuid: string;
  timestamp: string;
  camera_id: string;
  detection_confidence: number;
  face_width: number;
  face_height: number;
};

/** A person together with all their entries. */
type EmployeeDetails = Employee & {
  employee_logs: EmployeeLog[];
};

// Every request to /api/employee must send the token in the Authorization header
function authHeaders(): HeadersInit {
  return { Authorization: `Bearer ${getToken()}` };
}

// Throws an error with a readable message if the backend responds with an error
async function checkResponse(response: Response, message: string) {
  // 401 means that the token is missing or has expired (it is valid for one hour)
  if (response.status === 401) {
    logout();
    throw new Error("Your session has expired. Please log in again.");
  }
  if (!response.ok) {
    throw new Error(`${message} (${response.status}).`);
  }
}

/**
 * Fetches all registered persons (GET /api/employee/).
 *
 * @returns A list of all persons.
 */
export async function getEmployees(): Promise<Employee[]> {
  const response = await fetch(`${API_URL}/`, { headers: authHeaders() });
  await checkResponse(response, "Could not load persons");
  return response.json();
}

/**
 * Fetches one person together with all their entries (GET /api/employee/{id}).
 *
 * @param id The person's uuid.
 */
export async function getEmployeeDetails(id: string): Promise<EmployeeDetails> {
  const response = await fetch(`${API_URL}/${id}`, { headers: authHeaders() });
  await checkResponse(response, "Could not load the person");
  return response.json();
}

/**
 * Fetches a person's picture (GET /api/employee/{id}/image).
 *
 * An <img> tag cannot send the token, so the picture is fetched with fetch and
 * turned into a local address (blob:...) that can be shown in <img>.
 * Remove the address with URL.revokeObjectURL when it is no longer needed.
 *
 * @param id The person's uuid.
 * @returns A local address to the picture.
 */
export async function getEmployeeImage(id: string): Promise<string> {
  const response = await fetch(`${API_URL}/${id}/image`, { headers: authHeaders() });
  await checkResponse(response, "Could not load the picture");
  const blob = await response.blob();
  return URL.createObjectURL(blob);
}

/**
 * Adds a new person (POST /api/employee/).
 *
 * @param employee The person's details and picture.
 * @returns The saved person.
 * @throws Error if no face was found in the picture (422) or the backend responds with another error.
 */
export async function createEmployee(employee: EmployeeCreate): Promise<Employee> {
  const response = await fetch(`${API_URL}/`, {
    method: "POST",
    headers: { ...authHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify(employee),
  });

  // 422 means that the backend could not use the picture, e.g. no face was found
  if (response.status === 422) {
    throw new Error("No face was found in the picture. Please try another picture.");
  }
  await checkResponse(response, "Could not save the person");
  return response.json();
}

/**
 * Removes a person (DELETE /api/employee/{id}).
 *
 * @param id The person's uuid.
 */
export async function deleteEmployee(id: string): Promise<void> {
  const response = await fetch(`${API_URL}/${id}`, {
    method: "DELETE",
    headers: authHeaders(),
  });
  await checkResponse(response, "Could not remove the person");
}

/**
 * Fetches the latest entries from the log (GET /api/employee_logs/).
 *
 * @param limit The maximum number of entries to fetch.
 * @returns The log entries.
 */
export async function getEmployeeLogs(limit = 30): Promise<EmployeeLog[]> {
  const response = await fetch(`${BACKEND_URL}/api/employee_logs/?limit=${limit}`, { headers: authHeaders() });
  await checkResponse(response, "Could not load logs");
  return response.json();
}
