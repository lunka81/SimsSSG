import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import AdminHeader from "./AdminHeader";
import PersonTable, { type Person } from "./PersonTable";
import { getEmployees, deleteEmployee, type Employee } from "../../../api/employees";
import { Plus } from "lucide-react";
import "../Admin.css";
import "./Persons.css";

// Converts the backend's field names to the ones the Person type uses
function toPerson(employee: Employee): Person {
  return {
    id: employee.uuid,
    name: employee.name,
    permission: employee.permission,
    // Called description in the backend
    department: employee.description ?? "",
  };
}

/** Admin page that lists all registered persons. */
function Persons() {
  const [persons, setPersons] = useState<Person[]>([]);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  // Fetches all persons from the database when the page opens
  useEffect(() => {
    getEmployees()
      .then((employees) => setPersons(employees.map(toPerson)))
      .catch((error) => setError(error.message));
  }, []);

  // Removes the person from the database and from the list
  async function deletePerson(id: string) {
    await deleteEmployee(id);
    setPersons((previous) => previous.filter((person) => person.id !== id));
  }

  return (
    <div className="content persons-page">
      <div className="person-table-header">
        <AdminHeader title="Person " highlight="Register" />
        <button type="button" className="button-primary button-large" onClick={() => navigate("/admin")}>
          <Plus size={18} />
          Add person
        </button>
      </div>
      {error && <p role="alert">{error}</p>}
      <PersonTable persons={persons} onDelete={deletePerson} />
    </div>
  );
}

export default Persons;