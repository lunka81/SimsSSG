export type EmployeeCreate = {
  name: string;
  role: "Standard" | "Admin" | "Limited" | "Guest";
  description: string | null;
  img: string;
};

export type EmployeeResponse = {
  uuid: string;
  name: string;
};

export async function createEmployee(
  employee: EmployeeCreate
): Promise<EmployeeResponse> {
  const response = await fetch("http://localhost:8000/api/employee/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(employee),
  });

  if (!response.ok) {
    throw new Error(
      `Kunde inte spara personen (${response.status}).`
    );
  }

  return response.json();
}