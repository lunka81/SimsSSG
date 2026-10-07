import "./EmployeeDetails.css";
import { useEffect, useState } from "react";
import { X } from "lucide-react";
import { employeeImageUrl, getEmployee, type EmployeeDetail } from "../../../api";

// Tar emot vilken person som ska visas och en funktion som stänger rutan
type EmployeeDetailsProps = {
    uuid: string;
    onClose: () => void;
};

function EmployeeDetails({ uuid, onClose }: EmployeeDetailsProps) {
    const [employee, setEmployee] = useState<EmployeeDetail | null>(null);
    const [error, setError] = useState("");

    // Hämtar personen från backenden varje gång en ny person väljs
    useEffect(() => {
        getEmployee(uuid)
            .then(setEmployee)
            .catch((err) => setError(err instanceof Error ? err.message : "Could not load person"));
    }, [uuid]);

    // Stänger rutan med Escape
    useEffect(() => {
        function handleKeyDown(e: KeyboardEvent) {
            if (e.key === "Escape") {
                onClose();
            }
        }
        window.addEventListener("keydown", handleKeyDown);
        return () => {
            window.removeEventListener("keydown", handleKeyDown);
        };
    }, [onClose]);

    // Senaste inpasseringarna först
    const logs = [...(employee?.employee_logs ?? [])].sort(
        (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    );

    return (
        // Klick på den mörka bakgrunden stänger rutan, men inte klick i själva rutan
        <div className="details-overlay" onClick={onClose}>
            <div className="details-modal" onClick={(e) => e.stopPropagation()}>
                <div className="details-header">
                    <h2>Person details</h2>
                    <button type="button" className="icon-button" title="Close" onClick={onClose}>
                        <X size={16} />
                    </button>
                </div>
                <div className="details-line"></div>

                {error && <p className="login-error">{error}</p>}
                {!employee && !error && <p className="details-muted">Loading...</p>}

                {employee && (
                    <>
                        <div className="details-content">
                            <img className="details-picture" src={employeeImageUrl(employee.uuid)} alt={employee.name} />

                            <dl className="details-fields">
                                <dt>Name</dt>
                                <dd>{employee.name}</dd>
                                <dt>Permission</dt>
                                <dd>{employee.permission}</dd>
                                <dt>Description</dt>
                                <dd>{employee.description || <span className="details-muted">None</span>}</dd>
                                <dt>ID</dt>
                                <dd className="details-id">{employee.uuid}</dd>
                            </dl>
                        </div>

                        <h3>Entry log</h3>
                        {logs.length === 0 ? (
                            <p className="details-muted">No entries yet</p>
                        ) : (
                            <ul className="details-logs">
                                {logs.map((log) => (
                                    <li key={log.uuid}>
                                        <span>{new Date(log.timestamp).toLocaleString("sv-SE")}</span>
                                        <span className={log.approved ? "log-approved" : "log-denied"}>
                                            {log.approved ? "Approved" : "Denied"}
                                        </span>
                                    </li>
                                ))}
                            </ul>
                        )}
                    </>
                )}
            </div>
        </div>
    );
}

export default EmployeeDetails;
