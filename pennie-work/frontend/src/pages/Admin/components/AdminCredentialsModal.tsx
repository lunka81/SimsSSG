import { useEffect, useRef, useState } from "react";
import "./AdminCredentialsModal.css";
import type { SubmitEvent } from "react";

type AdminCredentialsModalProps = {
    personName: string;
    onConfirm: (username: string, password: string) => Promise<void>;
    onClose: () => void;
};

function AdminCredentialsModal({ personName, onConfirm, onClose }: AdminCredentialsModalProps) {
    const dialogRef = useRef<HTMLDialogElement>(null);
    const [error, setError] = useState<string | null>(null);
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        const dialog = dialogRef.current;

        if (dialog && !dialog.open) {
            dialog.showModal();
        }

        return () => {
            dialog?.close();
        };
    }, []);

    async function handleSubmit(e: SubmitEvent<HTMLFormElement>) {
        e.preventDefault();
        const form = e.currentTarget;
        const formData = new FormData(form);
        
        const username = String(formData.get("username") ?? "").trim();
        const password = String(formData.get("password") ?? "");
        const confirmPassword = String(formData.get("confirmPassword") ?? "");

        if (!username) {
            setError("Username is required.");
            return;
        }

        if (password.length < 8) {
            setError("Password must be at least 8 characters.");
            return;
        }

        if (password !== confirmPassword) {
            setError("Passwords do not match.");
            return;
        }

        setSaving(true);
        setError(null);

        try {
            await onConfirm(username, password);
        } catch (error) {
            setError(
                error instanceof Error ? error.message : "Could not create admin user.",
            );
        } finally {
            setSaving(false);
        }
    }

    return (
        <dialog
            ref={dialogRef}
            className="AdminPopUp"
            onCancel={(e) => {
                e.preventDefault();
                if (!saving) onClose();
            }}>
            <h2>Create login for {personName}</h2>
            <form onSubmit={handleSubmit}>
                <label>
                    Username
                    <input type="text" name="username" autoFocus />
                </label>
                <label>
                    Password
                    <input type="password" name="password" autoComplete="new-password" />
                </label>
                <label>
                    Confirm password
                    <input type="password" name="confirmPassword" autoComplete="new-password" />
                </label>
                {error && <p role="alert">{error}</p>}
                <div className="addAdmin-button">
                    <button
                        type="button"
                        className="button-secondary"
                        onClick={() => onClose()}
                        disabled={saving}
                    >
                        Cancel
                    </button>
                    <button
                        type="submit"
                        className="button-primary"
                        disabled={saving}
                    >
                        {saving ? "Saving..." : "Create admin user"}
                    </button>
                </div>
            </form>
        </dialog>

    )
}

export default AdminCredentialsModal;