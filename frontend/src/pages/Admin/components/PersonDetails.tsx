import { useEffect, useRef, useState } from "react";
import { X, Copy, Trash2 } from "lucide-react";
import type { Person } from "./PersonTable";
import {
  getEmployeeDetails,
  getEmployeeImage,
  type EmployeeLog,
} from "../../../api/employees";
import "./PersonDetails.css";

type PersonDetailsProps = {
  person: Person;
  onClose: () => void;
  /** Removes the person. Called after the admin has confirmed. */
  onDelete: (id: string) => Promise<void>;
};

// Shows date and time, e.g. "2026-10-12 14:44"
function formatDateTime(date: string) {
  return new Date(date).toLocaleString("sv-SE", { dateStyle: "short", timeStyle: "short" });
}

/**
 * Popup with details about one person: picture, ID, permission, department and
 * the latest entry. The person can also be removed from here.
 */
function PersonDetails({ person, onClose, onDelete }: PersonDetailsProps) {
  const dialogRef = useRef<HTMLDialogElement>(null);
  // The person's entries from the backend. null until the response has arrived
  const [logs, setLogs] = useState<EmployeeLog[] | null>(null);
  // Local address (blob:...) to the picture. null until the picture has been fetched
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  // Opens the dialog when the component is shown
  useEffect(() => {
    const dialog = dialogRef.current;
    if (dialog && !dialog.open) dialog.showModal();
    return () => dialog?.close();
  }, []);

  // Fetches the person's entries
  useEffect(() => {
    getEmployeeDetails(person.id)
      .then((details) => setLogs(details.employee_logs))
      .catch(console.error);
  }, [person.id]);

  // Fetches the picture with the token and removes the local address when the popup closes
  useEffect(() => {
    let url: string | null = null;
    getEmployeeImage(person.id)
      .then((objectUrl) => {
        url = objectUrl;
        setImageUrl(objectUrl);
      })
      .catch(console.error);
    return () => {
      if (url) URL.revokeObjectURL(url);
    };
  }, [person.id]);

  // The latest entry: the one with the largest timestamp in milliseconds
  const lastSeen = logs && logs.length > 0
    ? logs.reduce((latest, log) =>
        new Date(log.timestamp).getTime() > new Date(latest.timestamp).getTime() ? log : latest
      ).timestamp
    : null;

  // Asks for confirmation before the person is removed
  async function deletePerson() {
    if (!window.confirm(`Do you want to remove ${person.name}? This cannot be undone.`)) {
      return;
    }
    setSaving(true);
    try {
      await onDelete(person.id);
    } catch (error) {
      alert(error instanceof Error ? error.message : "Could not remove the person.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <dialog
      ref={dialogRef}
      className="person-details"
      // Esc closes the dialog
      onCancel={(e) => { e.preventDefault(); onClose(); }}
      // A click outside the dialog closes it
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="person-details-content">
        <div className="person-details-header">
          <h2>{person.name}</h2>
          <button type="button" className="icon-button" title="Close" onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        <div className="person-details-body">
          {imageUrl ? (
            <img src={imageUrl} alt={person.name} className="person-details-image" />
          ) : (
            <div className="person-details-image" />
          )}

          <dl className="person-details-info">
            <dt>ID</dt>
            <dd className="person-details-id">
              <code>{person.id}</code>
              <button
                type="button"
                className="icon-button"
                title="Copy ID"
                onClick={() => navigator.clipboard.writeText(person.id)}
              >
                <Copy size={14} />
              </button>
            </dd>

            <dt>Permission</dt>
            <dd>{person.permission}</dd>

            <dt>Department</dt>
            <dd>{person.department || "-"}</dd>

            <dt>Last seen</dt>
            <dd>{logs === null ? "Loading..." : lastSeen ? formatDateTime(lastSeen) : "Never"}</dd>
          </dl>
        </div>

        <div className="person-details-footer">
          <button type="button" className="button-danger" onClick={deletePerson} disabled={saving}>
            <Trash2 size={16} />
            {saving ? "Removing..." : "Delete"}
          </button>
        </div>
      </div>
    </dialog>
  );
}

export default PersonDetails;