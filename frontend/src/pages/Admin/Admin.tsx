/*import "./Admin.css";

function Admin() {
  return (
    <main>
      <h1>Admin</h1>
    </main>
  );
}

export default Admin;
*/

import { useEffect, useState } from "react";
import ImageCard from "../Home/components/ImageCard";
import "./Admin.css";

// Mirrors EmployeeOut in app.py: the shape of the JSON the backend returns
type Employee = {
  id: number;
  name: string;
  approved: boolean;
  logs: string[];
  timestamp: string;
};

// Mirrors EmployeeOutWithPic: same fields plus the picture as base64 text
type EmployeeWithPic = Employee & {
  picture: string;
};

const API_URL = "http://localhost:8000";

function Admin() {
  const [employees, setEmployees] = useState<Employee[]>([]);   // 1. starts as an empty list
  const [selected, setSelected] = useState<EmployeeWithPic | null>(null); // null = show the list
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {                                              // 2. runs once on page load
    fetch(`${API_URL}/employees`)                                // 3. GET /employees
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data: Employee[]) => setEmployees(data))            // 4. store it, so the page redraws
      .catch((err) => setError(err.message));
  }, []);

  // Runs when an <li> is clicked: fetches that employee, including the picture
  function showEmployee(id: number) {
    fetch(`${API_URL}/employees/${id}/`)                         // GET /employees/{emp_id}/
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data: EmployeeWithPic) => setSelected(data))        // page redraws showing only this employee
      .catch((err) => setError(err.message));
  }

  return (
    <main className="admin">
      <div className="admin-content">
        <header className="admin-header">
          <h1>Admin <span>Panel</span></h1>
          <div className="admin-header-line"></div>
        </header>

        {error && <p className="admin-error">Could not reach backend: {error}</p>}

        {selected ? (
          // One employee selected: show all its attributes
          <section className="employee-detail">
            <button className="back-button" onClick={() => setSelected(null)}>
              ← Back to list
            </button>

            <div className="detail-grid">
              <ImageCard
                title="Database Image"
                image={`data:image/jpeg;base64,${selected.picture}`}  // the browser decodes the base64
                showCorners
              />

              <div className="detail-panel">
                <h2>{selected.name}</h2>
                <StatusBadge approved={selected.approved} />

                <dl className="detail-fields">
                  <dt>ID</dt>
                  <dd>#{selected.id}</dd>

                  <dt>Registered</dt>
                  <dd>{new Date(selected.timestamp).toLocaleString()}</dd>

                  <dt>Logs</dt>
                  <dd>
                    {selected.logs.length === 0 ? (
                      <span className="muted">No logs</span>
                    ) : (
                      <ul className="log-list">
                        {selected.logs.map((log, i) => (
                          <li key={i}>{log}</li>
                        ))}
                      </ul>
                    )}
                  </dd>
                </dl>
              </div>
            </div>
          </section>
        ) : (
          // Nothing selected: show the list
          <section className="employee-panel">
            <div className="panel-title">
              <span>Employees</span>
              <span className="muted">{employees.length}</span>
            </div>

            {employees.length === 0 && !error && <p className="muted">No employees yet.</p>}

            <ul className="employee-list">
              {employees.map((emp) => (
                <li
                  key={emp.id}
                  className="employee-item"
                  onClick={() => showEmployee(emp.id)}
                  // lets keyboard users select with Tab + Enter
                  tabIndex={0}
                  onKeyDown={(e) => e.key === "Enter" && showEmployee(emp.id)}
                >
                  <span className="employee-avatar">{emp.name.charAt(0).toUpperCase()}</span>
                  <span className="employee-name">{emp.name}</span>
                  <span className="employee-id">#{emp.id}</span>
                  <StatusBadge approved={emp.approved} />
                </li>
              ))}
            </ul>
          </section>
        )}
      </div>
    </main>
  );
}

// Orange "Approved" or red "Denied" pill, same colors as AccessRes on the Home page
function StatusBadge({ approved }: { approved: boolean }) {
  return (
    <span className={`status-badge ${approved ? "approved" : "denied"}`}>
      {approved ? "✓ Approved" : "✕ Denied"}
    </span>
  );
}

export default Admin;