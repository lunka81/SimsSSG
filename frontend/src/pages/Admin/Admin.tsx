import Header from "./components/Header";
import Summary from "./components/Summary";
import AddPerson from "./components/AddPerson";
import { registerAdmin } from "../../auth";
import { User, Check, X, ChartNoAxesColumn } from "lucide-react";
import { createEmployee, getEmployees, getEmployeeDetails } from "../../api/employees";
import "./Admin.css";
import { useState, useEffect } from "react";

function Admin() {
  const [regPersons, setRegPersons] = useState<number | null>(null);
  const [approvedToday, setApprovedToday] = useState<number | null>(null);

  useEffect(() => {
    async function loadStatistics() {
      const employees = await getEmployees();
      setRegPersons(employees.length);
      const details = await Promise.all(employees.map((employee) => getEmployeeDetails(employee.uuid)));
      const logs = details.flatMap((detail) => detail.employee_logs);
      const startOfToday = new Date();
      startOfToday.setHours(0, 0, 0, 0);
      const approvedLogsToday = logs.filter(
        (log) => new Date(log.timestamp) >= startOfToday
      );
      setApprovedToday(approvedLogsToday.length);
    }
    loadStatistics().catch((error) => console.error(error));
  }, []);

  // Anropas av AddPerson när man klickar "Add person" och sparar personen i databasen
  async function handleAddPerson(
    name: string,
    access: string,
    description: string,
    image: string
  ): Promise<void> {
    if (
      access !== "Standard" &&
      access !== "Admin" &&
      access !== "Limited"
    ) {
      throw new Error("Invalid permission.");
    }

    await createEmployee({
      name,
      permission: access,
      description,
      img: image,
    });
    setRegPersons((previous) => (previous === null ? null : previous + 1));
  }

  async function handleAddAdmin(
    name: string,
    access: string,
    description: string,
    image: string,
    username: string,
    password: string,
  ): Promise<void> {
    if (
      access !== "Standard" &&
      access !== "Admin" &&
      access !== "Limited"
    ) {
      throw new Error("Invalid permission.");
    }

    await registerAdmin({
      name,
      permission: access,
      description,
      img: image,
      username,
      plain_password: password,
    });
    setRegPersons((previous) => (previous === null ? null : previous + 1));
  }

  return (
    <div className="content">
      <Header title="Admin " highlight="Panel" />

      {/*De fyra korten ligger i ett rutnät*/}
      <div className="event-summary">
        <Summary
          icon={<User size={28} />}
          iconClass="summary-icon"
          value={regPersons === null ? "-" : String(regPersons)}
          label="Registered persons"
          sub="Total"
        />
        <Summary
          icon={<Check size={28} />}
          iconClass="summary-icon approved"
          value={approvedToday === null ? "-" : String(approvedToday)}
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
        <AddPerson onAdd={handleAddPerson} onAddAdmin={handleAddAdmin} />
      </div>
    </div>
  );
}

export default Admin;