import { useEffect, useRef, useState } from "react";
import { X, Copy, Trash2, Pencil, Camera, Check } from "lucide-react";
import type { Person } from "./PersonTable";
import {
  getEmployeeDetails,
  getEmployeeImage,
  type EmployeeLog,
} from "../../../api/employees";
import CameraModal from "./CameraModal";
import "./PersonDetails.css";

type EditablePersonField = "name" | "access" | "department";

type PersonDraft = {
  name: string;
  access: string;
  department: string;
};

export type PersonDetailsUpdate = PersonDraft & {
  // Ny bild som data-URL. Utelämnas när bilden inte har ändrats.
  image?: string;
};

type PersonDetailsProps = {
  person: Person;
  onClose: () => void;
  onDelete: (id: string) => Promise<void>;
  permissionOptions?: readonly string[];
  onSave?: (id: string, changes: PersonDetailsUpdate) => Promise<void>;
};

function makeDraft(person: Person): PersonDraft {
  return {
    name: person.name,
    access: person.access,
    department: person.department ?? "",
  };
}

function formatDateTime(date: string) {
  return new Date(date).toLocaleString("sv-SE", {
    dateStyle: "short",
    timeStyle: "short",
  });
}

function PersonDetails({
  person,
  onClose,
  onDelete,
  permissionOptions = [],
  onSave,
}: PersonDetailsProps) {
  const dialogRef = useRef<HTMLDialogElement>(null);

  const [logs, setLogs] = useState<EmployeeLog[] | null>(null);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [newImage, setNewImage] = useState<string | null>(null);
  const [isCameraOpen, setIsCameraOpen] = useState(false);
  const [editingField, setEditingField] =
    useState<EditablePersonField | null>(null);
  const [draft, setDraft] = useState<PersonDraft>(() => makeDraft(person));
  const [original, setOriginal] =
    useState<PersonDraft>(() => makeDraft(person));
  const [fieldBeforeEdit, setFieldBeforeEdit] = useState("");
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [logsError, setLogsError] = useState<string | null>(null);

  const busy = saving || deleting;
  const displayedImage = newImage ?? imageUrl;

  const hasChanges =
    draft.name !== original.name ||
    draft.access !== original.access ||
    draft.department !== original.department ||
    newImage !== null;

  const roles = Array.from(
    new Set([original.access, ...permissionOptions].filter(Boolean))
  );

  useEffect(() => {
    const dialog = dialogRef.current;

    if (dialog && !dialog.open) {
      dialog.showModal();
    }

    return () => dialog?.close();
  }, []);

  useEffect(() => {
    const values = makeDraft(person);

    setDraft(values);
    setOriginal(values);
    setNewImage(null);
    setEditingField(null);
    setIsCameraOpen(false);
    setError(null);
  }, [person.id, person.name, person.access, person.department]);

  useEffect(() => {
    let cancelled = false;

    setLogs(null);
    setLogsError(null);

    getEmployeeDetails(person.id)
      .then((details) => {
        if (!cancelled) {
          setLogs(details.employee_logs);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setLogsError("Could not load entries.");
        }
      });

    return () => {
      cancelled = true;
    };
  }, [person.id]);

  useEffect(() => {
    let cancelled = false;
    let objectUrl: string | null = null;

    setImageUrl(null);

    getEmployeeImage(person.id)
      .then((url) => {
        if (cancelled) {
          URL.revokeObjectURL(url);
          return;
        }

        objectUrl = url;
        setImageUrl(url);
      })
      .catch(console.error);

    return () => {
      cancelled = true;

      if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
      }
    };
  }, [person.id]);

  const approvedCount =
    logs?.filter((log) => log.approved).length ?? 0;

  const deniedCount =
    logs?.filter((log) => !log.approved).length ?? 0;

  const lastSeen =
    logs && logs.length > 0
      ? logs.reduce((latest, log) =>
          new Date(log.timestamp).getTime() >
          new Date(latest.timestamp).getTime()
            ? log
            : latest
        ).timestamp
      : null;

  function requestClose() {
    if (busy || isCameraOpen) return;

    if (
      hasChanges &&
      !window.confirm("Discard unsaved changes?")
    ) {
      return;
    }

    onClose();
  }

  function beginEditing(field: EditablePersonField) {
    setFieldBeforeEdit(draft[field]);
    setEditingField(field);
  }

  function cancelFieldEditing() {
    if (editingField !== null) {
      const field = editingField;

      setDraft((current) => ({
        ...current,
        [field]: fieldBeforeEdit,
      }));
    }

    setEditingField(null);
  }

  function cancelChanges() {
    setDraft({ ...original });
    setNewImage(null);
    setEditingField(null);
    setError(null);
  }

  async function copyId() {
    try {
      await navigator.clipboard.writeText(person.id);
    } catch {
      setError("Could not copy the ID.");
    }
  }

  async function saveChanges() {
    if (!onSave || busy) return;

    const name = draft.name.trim();

    if (!name) {
      setError("Name cannot be empty.");
      setEditingField("name");
      return;
    }

    setSaving(true);
    setError(null);
    setEditingField(null);

    try {
      await onSave(person.id, {
        name,
        access: draft.access,
        department: draft.department.trim(),
        ...(newImage !== null ? { image: newImage } : {}),
      });

      onClose();
    } catch (saveError) {
      setError(
        saveError instanceof Error
          ? saveError.message
          : "Could not save the changes."
      );
    } finally {
      setSaving(false);
    }
  }

  async function deletePerson() {
    if (
      !window.confirm(
        `Do you want to remove ${person.name}? This cannot be undone.`
      )
    ) {
      return;
    }

    setDeleting(true);
    setError(null);

    try {
      await onDelete(person.id);
    } catch (deleteError) {
      setError(
        deleteError instanceof Error
          ? deleteError.message
          : "Could not remove the person."
      );
    } finally {
      setDeleting(false);
    }
  }

  function renderEditableField(
    field: EditablePersonField,
    label: string
  ) {
    const editing = editingField === field;

    return (
      <dd className="person-details-editable">
        {editing ? (
          field === "access" ? (
            <select
              className="person-details-input"
              aria-label={label}
              value={draft.access}
              autoFocus
              onChange={(event) => {
                const value = event.target.value;

                setDraft((current) => ({
                  ...current,
                  access: value,
                }));
              }}
              onKeyDown={(event) => {
                if (event.key === "Escape") {
                  event.preventDefault();
                  event.stopPropagation();
                  cancelFieldEditing();
                }
              }}
            >
              {roles.map((role) => (
                <option key={role} value={role}>
                  {role}
                </option>
              ))}
            </select>
          ) : (
            <input
              className="person-details-input"
              aria-label={label}
              value={draft[field]}
              autoFocus
              onChange={(event) => {
                const value = event.target.value;

                setDraft((current) => ({
                  ...current,
                  [field]: value,
                }));
              }}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  event.preventDefault();
                  setEditingField(null);
                }

                if (event.key === "Escape") {
                  event.preventDefault();
                  event.stopPropagation();
                  cancelFieldEditing();
                }
              }}
            />
          )
        ) : (
          <span>{draft[field] || "–"}</span>
        )}

        <button
          type="button"
          className="icon-button"
          title={editing ? `Finish editing ${label}` : `Edit ${label}`}
          aria-label={
            editing ? `Finish editing ${label}` : `Edit ${label}`
          }
          disabled={busy}
          onClick={() => {
            if (editing) {
              setEditingField(null);
            } else {
              beginEditing(field);
            }
          }}
        >
          {editing ? <Check size={14} /> : <Pencil size={14} />}
        </button>
      </dd>
    );
  }

  return (
    <dialog
      ref={dialogRef}
      className="person-details"
      onCancel={(event) => {
        if (event.target !== event.currentTarget) return;

        event.preventDefault();

        if (editingField !== null) {
          cancelFieldEditing();
          return;
        }

        requestClose();
      }}
      onClick={(event) => {
        if (event.target === event.currentTarget) {
          requestClose();
        }
      }}
    >
      <div className="person-details-content">
        <div className="person-details-header">
          <div className="person-details-heading">
            <h2>ID</h2>

            <div className="person-details-id">
              <code>{person.id}</code>

              <button
                type="button"
                className="icon-button"
                title="Copy ID"
                aria-label="Copy ID"
                onClick={copyId}
              >
                <Copy size={14} />
              </button>
            </div>
          </div>

          <button
            type="button"
            className="icon-button"
            title="Close"
            aria-label="Close"
            disabled={busy}
            onClick={requestClose}
          >
            <X size={16} />
          </button>
        </div>

        <div className="person-details-body">
          <div>
            <button
              type="button"
              className="person-details-image-button"
              title="Change photo"
              aria-label={`Change photo of ${draft.name}`}
              disabled={busy}
              onClick={() => setIsCameraOpen(true)}
            >
              {displayedImage ? (
                <img
                  src={displayedImage}
                  alt={draft.name}
                  className="person-details-image"
                />
              ) : (
                <div className="person-details-image" />
              )}

              <span className="person-details-camera-icon">
                <Camera size={16} />
              </span>
            </button>

            {newImage && (
              <p className="person-details-note">
                New photo — not saved yet.
              </p>
            )}
          </div>

          <dl className="person-details-info">
            <dt>Name</dt>
            {renderEditableField("name", "name")}

            <dt>Permission</dt>
            {renderEditableField("access", "permission")}

            <dt>Department</dt>
            {renderEditableField("department", "department")}

            <dt>Last seen</dt>
            <dd>
              {logsError
                ? "Unavailable"
                : logs === null
                  ? "Loading..."
                  : lastSeen
                    ? formatDateTime(lastSeen)
                    : "Never"}
            </dd>

            <dt>Entries</dt>
            <dd>
              {logsError
                ? "Unavailable"
                : logs === null
                  ? "Loading..."
                  : `${approvedCount} approved, ${deniedCount} denied`}
            </dd>
          </dl>
        </div>

        {logsError && (
          <p className="person-details-error" role="alert">
            {logsError}
          </p>
        )}

        {error && (
          <p className="person-details-error" role="alert">
            {error}
          </p>
        )}

        {!onSave && (
          <p className="person-details-note">
            Preview only. Saving is not connected yet.
          </p>
        )}

        <div className="person-details-footer">
          <button
            type="button"
            className="button-danger"
            disabled={busy}
            onClick={deletePerson}
          >
            <Trash2 size={16} />
            {deleting ? "Removing..." : "Delete"}
          </button>

          <button
            type="button"
            className="button-secondary"
            disabled={busy || !hasChanges}
            onClick={cancelChanges}
          >
            Cancel changes
          </button>

          <button
            type="button"
            className="button-primary"
            disabled={busy || !hasChanges || !onSave}
            onClick={saveChanges}
          >
            {saving ? "Saving..." : "Save changes"}
          </button>
        </div>
      </div>

      {isCameraOpen && (
        <CameraModal
          onCapture={(image) => {
            setNewImage(image);
            setIsCameraOpen(false);
          }}
          onClose={() => setIsCameraOpen(false)}
        />
      )}
    </dialog>
  );
}

export default PersonDetails;