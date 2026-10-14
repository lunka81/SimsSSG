import { useEffect, useRef, useState } from "react";
import { X, Copy, Pencil, Trash2 } from "lucide-react";
import type { Person } from "./PersonTable";
import {
  getEmployeeDetails,
  getEmployeeImageUrl,
  type EmployeeDetails,
  type EmployeeUpdate,
  type Permission,
} from "../../../api/employees";
import "./PersonDetails.css";

type PersonDetailsProps = {
  person: Person;
  onClose: () => void;
  onUpdate: (id: string, changes: EmployeeUpdate) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
};

// Visar datum och klockslag, t.ex. "2026-10-12 14:44"
function formatDateTime(date: string) {
  return new Date(date).toLocaleString("sv-SE", { dateStyle: "short", timeStyle: "short" });
}

function PersonDetails({ person, onClose, onUpdate, onDelete }: PersonDetailsProps) {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const [details, setDetails] = useState<EmployeeDetails | null>(null);
  const [saving, setSaving] = useState(false);

  // true när man redigerar, false när man bara tittar
  const [editing, setEditing] = useState(false);

  // Värdena i redigeringsfälten. Börjar med personens nuvarande värden
  const [name, setName] = useState(person.name);
  const [access, setAccess] = useState(person.access);
  const [department, setDepartment] = useState(person.department);

  // Öppnar rutan när komponenten visas
  useEffect(() => {
    const dialog = dialogRef.current;
    if (dialog && !dialog.open) dialog.showModal();
    return () => dialog?.close();
  }, []);

  // Hämtar statistiken för personen
  useEffect(() => {
    getEmployeeDetails(person.id).then(setDetails).catch(console.error);
  }, [person.id]);

  // Gemensam hjälpfunktion: visar att något sparas och fångar fel
  async function run(action: () => Promise<void>) {
    setSaving(true);
    try {
      await action();
    } catch (error) {
      alert(error instanceof Error ? error.message : "Something went wrong.");
    } finally {
      setSaving(false);
    }
  }

  function toggleStatus() {
    run(() => onUpdate(person.id, { active: !person.active }));
  }

  // Fyller fälten med de senaste värdena och går till redigeringsläget
  function startEditing() {
    setName(person.name);
    setAccess(person.access);
    setDepartment(person.department);
    setEditing(true);
  }

  function saveChanges() {
    if (!name.trim()) {
      alert("Name is required.");
      return;
    }
    run(async () => {
      await onUpdate(person.id, {
        name: name.trim(),
        role: access as Permission,
        description: department.trim(),
      });
      setEditing(false);
    });
  }

  function deletePerson() {
    if (!window.confirm(`Do you want to remove ${person.name}? This cannot be undone.`)) {
      return;
    }
    run(() => onDelete(person.id));
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
          {editing ? (
            <input
              className="person-details-input"
              value={name}
              onChange={(e) => setName(e.target.value)}
              aria-label="Name"
            />
          ) : (
            <h2>{person.name}</h2>
          )}
          <button type="button" className="icon-button" title="Close" onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        <div className="person-details-body">
          <img src={getEmployeeImageUrl(person.id)} alt={person.name} className="person-details-image" />

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
            <dd>
              {editing ? (
                <select
                  className="person-details-input"
                  value={access}
                  onChange={(e) => setAccess(e.target.value)}
                  aria-label="Permission"
                >
                  <option value="Standard">Standard</option>
                  <option value="Admin">Admin</option>
                  <option value="Limited">Limited</option>
                  <option value="Guest">Guest</option>
                </select>
              ) : (
                person.access
              )}
            </dd>

            <dt>Department</dt>
            <dd>
              {editing ? (
                <input
                  className="person-details-input"
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                  aria-label="Department"
                />
              ) : (
                person.department || "–"
              )}
            </dd>

            <dt>Added</dt>
            <dd>{formatDateTime(person.createdAt)}</dd>

            <dt>Status</dt>
            <dd>
              <label className="status-toggle">
                <input type="checkbox" checked={person.active} onChange={toggleStatus} disabled={saving} />
                <span className="status-toggle-slider" />
                {person.active ? "Active" : "Inactive"}
              </label>
            </dd>

            <dt>Last seen</dt>
            <dd>{details?.last_seen ? formatDateTime(details.last_seen) : "Never"}</dd>

            <dt>Entries</dt>
            <dd>
              {details ? `${details.approved_count} approved, ${details.denied_count} denied` : "Loading..."}
            </dd>
          </dl>
        </div>

        {/*Knapparna längst ner. Olika knappar beroende på om man redigerar eller inte*/}
        <div className="person-details-footer">
          {editing ? (
            <>
              <button type="button" className="button-secondary" onClick={() => setEditing(false)} disabled={saving}>
                Cancel
              </button>
              <button type="button" className="button-primary" onClick={saveChanges} disabled={saving}>
                {saving ? "Saving..." : "Save changes"}
              </button>
            </>
          ) : (
            <>
              <button type="button" className="button-danger" onClick={deletePerson} disabled={saving}>
                <Trash2 size={16} />
                Delete
              </button>
              <button type="button" className="button-primary" onClick={startEditing} disabled={saving}>
                <Pencil size={16} />
                Edit
              </button>
            </>
          )}
        </div>
      </div>
    </dialog>
  );
}

export default PersonDetails;
