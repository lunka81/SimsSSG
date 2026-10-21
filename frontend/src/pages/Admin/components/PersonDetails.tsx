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
  onDelete: (id: string) => Promise<void>;
};

// Visar datum och klockslag, t.ex. "2026-10-12 14:44"
function formatDateTime(date: string) {
  return new Date(date).toLocaleString("sv-SE", { dateStyle: "short", timeStyle: "short" });
}

function PersonDetails({ person, onClose, onDelete }: PersonDetailsProps) {
  const dialogRef = useRef<HTMLDialogElement>(null);
  // Personens passager från backend. null tills svaret har kommit
  const [logs, setLogs] = useState<EmployeeLog[] | null>(null);
  // Lokal adress (blob:...) till bilden. null tills bilden har hämtats
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  // Öppnar rutan när komponenten visas
  useEffect(() => {
    const dialog = dialogRef.current;
    if (dialog && !dialog.open) dialog.showModal();
    return () => dialog?.close();
  }, []);

  // Hämtar personens passager
  useEffect(() => {
    getEmployeeDetails(person.id)
      .then((details) => setLogs(details.employee_logs))
      .catch(console.error);
  }, [person.id]);

  // Hämtar bilden med token och tar bort den lokala adressen när popupen stängs
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

  // Den senaste passagen: störst tidpunkt i millisekunder
  const lastSeen = logs && logs.length > 0
    ? logs.reduce((latest, log) =>
        new Date(log.timestamp).getTime() > new Date(latest.timestamp).getTime() ? log : latest
      ).timestamp
    : null;

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
      // Esc stänger rutan
      onCancel={(e) => { e.preventDefault(); onClose(); }}
      // Klick utanför rutan stänger den
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
            <dd>{person.department || "–"}</dd>

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
