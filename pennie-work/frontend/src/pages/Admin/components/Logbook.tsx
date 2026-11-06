import { useState, useEffect } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import AdminHeader from "./AdminHeader";
import { getEmployees, getEmployeeLogs } from "../../../api/employees";
import "./PersonTable.css";
import "../Admin.css";
import "./Logbook.css";

type LogEntry = {
    id: string;
    timestamp: string;
    cameraId: string;
    name: string;
    permission: string;
}

const PAGE_SIZE = 10;
const MAX_ENTRIES = 40;

function formatDateTime(date: string) {
    return new Date(date).toLocaleString("sv-SE", { dateStyle: "short", timeStyle: "short" });
}

function Logbook() {
    const [entries, setEntries] = useState<LogEntry[]>([]);
    const [error, setError] = useState<string | null>(null);
    const [page, setPage] = useState(1);

    useEffect(() => {
        async function loadLogs() {
            const [employees, logs] = await Promise.all([getEmployees(), getEmployeeLogs(MAX_ENTRIES)]);
            const employeeById = new Map(employees.map((employee) => [employee.uuid, employee]));
            const latestEntries: LogEntry[] = logs.map((log) => {
                const employee = employeeById.get(log.employee_uuid);
                return {
                    id: log.uuid,
                    timestamp: log.timestamp,
                    cameraId: log.camera_id,
                    name: employee?.name ?? "Unknown person",
                    permission: employee?.permission ?? "-",
                };
            });
            setEntries(latestEntries);
        }

        loadLogs().catch((error) => setError(error.message));
    }, []);

    const totalPages = Math.max(1, Math.ceil(entries.length / PAGE_SIZE));
    const currentPage = Math.min(page, totalPages);
    const start = (currentPage - 1) * PAGE_SIZE;
    const visibleEntries = entries.slice(start, start + PAGE_SIZE);

    return (
        <div className="content logbook-page">
            <AdminHeader title="Log" highlight="book" />
            {error && <p role="alert">{error}</p>}
            <div className="person-table">
                <div className="person-table-card">
                    <h2>Latest {MAX_ENTRIES} entries</h2>
                    <div className="person-table-wrapper">
                        <table>
                            <thead>
                                <tr>
                                    <th>Time</th>
                                    <th>Name</th>
                                    <th>Permission</th>
                                    <th>Door</th>
                                </tr>
                            </thead>
                            <tbody>
                                {entries.length === 0 ? (<tr><td colSpan={4}>No entries yet</td></tr>) : (visibleEntries.map((entry) => (
                                    <tr key={entry.id}>
                                        <td>{formatDateTime(entry.timestamp)}</td>
                                        <td>{entry.name}</td>
                                        <td>{entry.permission}</td>
                                        <td>{entry.cameraId}</td>
                                    </tr>
                                )))}
                            </tbody>
                        </table>
                    </div>
                    <div className="person-table-pagination">
                        <span>
                            Showing {entries.length === 0 ? 0 : start + 1}-{start + visibleEntries.length} of {entries.length}
                        </span>

                        <div className="pagination-buttons">
                            <button
                                type="button"
                                className="icon-button"
                                title="Previous page"
                                disabled={currentPage === 1}
                                onClick={() => setPage(currentPage - 1)}
                            >
                                <ChevronLeft size={16} />
                            </button>

                            <span>Page {currentPage} of {totalPages}</span>

                            <button
                                type="button"
                                className="icon-button"
                                title="Next page"
                                disabled={currentPage === totalPages}
                                onClick={() => setPage(currentPage + 1)}
                            >
                                <ChevronRight size={16} />
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );

}

export default Logbook;