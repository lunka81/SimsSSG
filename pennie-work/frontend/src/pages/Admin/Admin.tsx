import { useCallback, useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { isLoggedIn } from "../../auth";
import { deleteEmployee, getEmployees, type Employee } from "../../api";
import Header from "./components/Header";
import Summary from "./components/Summary";
import AddPerson from "./components/AddPerson";
import Sidebar from "./components/Sidebar";
import StoredPersons, { type Person } from "./components/StoredPersons";
import EmployeeDetails from "./components/EmployeeDetails";
import { User, Check, X, ChartNoAxesColumn } from "lucide-react";
import "./Admin.css";

// Gör om en person från backenden till det format som tabellen använder
function toPerson(employee: Employee): Person {
  return {
    id: employee.uuid,
    name: employee.name,
    access: employee.permission,
    department: employee.description ?? "",
    // Finns inte i databasen än, så alla visas som aktiva
    active: true,
  };
}

function Admin() {
  // Admin äger listan och delar ut den till AddPerson och StoredPersons
  const [persons, setPersons] = useState<Person[]>([]);
  // uuid för personen vars detaljer visas, null när rutan är stängd
  const [selectedId, setSelectedId] = useState<string | null>(null);

  // Hämtar alla personer från databasen när sidan öppnas
  useEffect(() => {
    getEmployees()
      .then((employees) => setPersons(employees.map(toPerson)))
      .catch((err) => console.error("Could not load persons:", err));
  }, []);

  // useCallback så att EmployeeDetails inte lägger till sin Escape-lyssnare på nytt vid varje rendering
  const closeDetails = useCallback(() => setSelectedId(null), []);

  if (!isLoggedIn()) {
    return <Navigate to="/" replace />;
  }

  // Anropas av AddPerson när backenden har sparat personen
  function addPerson(employee: Employee) {
    // Skapar en ny lista med alla gamla personer och den nya sist
    setPersons([...persons, toPerson(employee)]);
  }

  // Anropas av StoredPersons när man har bekräftat borttagningen
  async function deletePerson(id: string) {
    try {
      // Tar bort personen i databasen först, så att listan bara ändras om det lyckades
      await deleteEmployee(id);
    } catch (err) {
      window.alert(err instanceof Error ? err.message : "Could not remove person");
      return;
    }
    // Behåller alla personer utom den med detta id.
    // prev används eftersom listan kan ha ändrats medan vi väntade på backenden
    setPersons((prev) => prev.filter((person) => person.id !== id));
  }

  return (
    <div className="admin-layout">
      <Sidebar />
      <main className="app">
        <div className="content">
          <Header />

          {/*De fyra korten ligger i ett rutnät*/}
          <div className="event-summary">
            <Summary
              icon={<User size={28} />}
              iconClass="summary-icon"
              value="24"
              label="Registered persons"
              sub="Total"
            />
            <Summary
              icon={<Check size={28} />}
              iconClass="summary-icon approved"
              value="18"
              label="Approved entries"
              sub="Today"
            />
            <Summary
              icon={<X size={28} />}
              iconClass="summary-icon"
              value="2"
              label="Denied entries"
              sub="Today"
            />
            <Summary
              icon={<ChartNoAxesColumn size={28} />}
              iconClass="summary-icon"
              value="96%"
              label="Average confidence"
              sub="Last 30 days"
            />
          </div>

          <div className="mid-content">
            <AddPerson onAdd={addPerson} />
            <StoredPersons persons={persons} onDelete={deletePerson} onSelect={setSelectedId} />
          </div>
        </div>
      </main>
      {selectedId && <EmployeeDetails uuid={selectedId} onClose={closeDetails} />}
    </div>
  );
}

export default Admin;