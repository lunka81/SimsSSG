import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Header from "./Header";
import PersonTable, { type Person } from "./PersonTable";
import { getEmployees, deleteEmployee, type Employee } from "../../../api/employees";
import { Plus } from "lucide-react";
import "../Admin.css";
import "./Persons.css";

// Översätter backendens fältnamn till de som Person-typen använder
function toPerson(employee: Employee): Person {
  return {
    id: employee.uuid,
    name: employee.name,
    access: employee.permission,
    department: employee.description ?? "",
  };
}

function Persons() {
  const [persons, setPersons] = useState<Person[]>([]);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  // Hämtar alla personer från databasen när sidan öppnas
  useEffect(() => {
    getEmployees()
      .then((employees) => setPersons(employees.map(toPerson)))
      .catch((error) => setError(error.message));
  }, []);

  // Tar bort personen ur databasen och ur listan
  async function deletePerson(id: string) {
    await deleteEmployee(id);
    setPersons((previous) => previous.filter((person) => person.id !== id));
  }

  return (
    <div className="content persons-page">
      <div className="person-table-header">
        <Header title="Person " highlight="Register" />
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
