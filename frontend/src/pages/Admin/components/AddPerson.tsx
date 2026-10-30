import "./AddPerson.css";
import AdminCredentialsModal from "./AdminCredentialsModal";
import type { SubmitEvent } from "react";
import { useState, useRef } from "react";
import { Camera } from "lucide-react";
import CameraModal from "./CameraModal";


type AddPersonProps = {
    /** Saves a person with the Standard or Limited permission. */
    onAdd: (
        name: string,
        permission: string,
        department: string,
        image: string,
    ) => Promise<void>;

    /** Saves a person with the Admin permission together with a username and password. */
    onAddAdmin: (
        name: string,
        permission: string,
        department: string,
        image: string,
        username: string,
        password: string,
    ) => Promise<void>;
};

// A new admin whose details are saved while the login details are entered in a popup
type PendingAdmin = {
    name: string;
    permission: string;
    department: string;
    image: string;
};

/**
 * Form for adding a new person. The picture can be uploaded as a file or taken with the webcam.
 * If the Admin permission is chosen, a popup asks for a username and password before saving.
 */
function AddPerson({ onAdd, onAddAdmin }: AddPersonProps) {
    // The chosen picture as a data URL, shown as a preview and sent to the backend
    const [imagePreview, setImagePreview] = useState<string | null>(null);
    const [cameraOpen, setCameraOpen] = useState(false);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [pendingAdmin, setPendingAdmin] = useState<PendingAdmin | null>(null);
    const formRef = useRef<HTMLFormElement>(null);

    // Reads the uploaded file and converts it to a data URL
    function handleImageChange(e: React.ChangeEvent<HTMLInputElement>) {
        const file = e.target.files?.[0];
        if (!file) return;

        const reader = new FileReader();

        reader.onload = () => {
            if (typeof reader.result === "string") {
                setImagePreview(reader.result);
            }
        };

        reader.readAsDataURL(file);
    }
    async function handleSubmit(e: SubmitEvent<HTMLFormElement>) {
        e.preventDefault();
        if (saving) return;

        // Save the reference before await, since e.currentTarget is null afterwards
        const form = e.currentTarget;
        const formData = new FormData(form);

        const name = String(formData.get("name") ?? "").trim();
        const permission = String(formData.get("permission") ?? "");
        const department = String(formData.get("department") ?? "");

        if (!name || !imagePreview) {
            setError("Name and profile picture are required.");
            return;
        }

        // An admin also needs login details, so open the popup instead of saving directly
        if (permission === "Admin") {
            setError(null);
            setPendingAdmin({ name, permission, department, image: imagePreview });
            return;
        }

        setSaving(true);
        setError(null);

        try {
            await onAdd(name, permission, department, imagePreview);

            // Clear the form only after the backend has saved the person
            form.reset();
            setImagePreview(null);
        } catch (error) {
            setError(
                error instanceof Error ? error.message : "Could not save the person.",
            );
        } finally {
            setSaving(false);
        }
    }

    // Called by the popup when the login details have been entered. Saves the admin
    async function handleAdminConfirm(username: string, password: string): Promise<void> {
        if (pendingAdmin === null) return;
        await onAddAdmin(
            pendingAdmin.name,
            pendingAdmin.permission,
            pendingAdmin.department,
            pendingAdmin.image,
            username,
            password
        );

        formRef.current?.reset();
        setImagePreview(null);
        setPendingAdmin(null);
    }

    function handleAdminClose() {
        setPendingAdmin(null);
    }

    function handleCancel() {
        setImagePreview(null);
        setError(null);
        setCameraOpen(false);
    }

    return (
        <section className="add-person">
            <h2>Add new person</h2>

            <form className="add-person-form" ref={formRef} onSubmit={handleSubmit} autoComplete="off">
                <div className="add-person-fields">
                    <label>
                        <span>
                            Name <span className="required">*</span>
                        </span>
                        <input type="text" name="name" placeholder="John Smith" />
                    </label>
                    <label>
                        <span>
                            Access permissions <span className="required">*</span>
                        </span>
                        <select name="permission">
                            <option value="Standard">Standard</option>
                            <option value="Admin">Admin</option>
                            <option value="Limited">Limited</option>
                        </select>
                    </label>
                    <label>
                        Department (optional)
                        <input
                            type="text"
                            name="department"
                            placeholder="IT, Admin, HR..."
                        />
                    </label>
                </div>

                <div className="add-person-picture">
                    <p>
                        Profile picture <span className="required">*</span>
                    </p>

                    <div className="picture-row">
                        <div className="picture-preview">
                            {imagePreview && <img src={imagePreview} alt="Profile preview" />}
                        </div>

                        <label className="picture-upload">
                            <Camera size={28} />
                            <span className="upload-title">Upload picture</span>
                            <span className="upload-hint">JPG, PNG (max 5 MB)</span>
                            <input
                                type="file"
                                name="picture"
                                accept="image/png, image/jpeg"
                                onChange={handleImageChange}
                                hidden
                            />
                        </label>
                    </div>
                </div>

                <div className="add-person-buttons">
                    <button type="reset" className="button-secondary" onClick={handleCancel}>
                        Cancel
                    </button>
                    <button type="submit" className="button-primary" disabled={saving}>
                        {" "}
                        {saving ? "Saving..." : "Add person"}
                    </button>
                    <button
                        type="button"
                        className="button-primary"
                        onClick={() => setCameraOpen(true)}
                        disabled={saving}
                    >
                        Camera
                    </button>
                </div>
            </form>
            {error && <p role="alert">{error}</p>}

            {cameraOpen && (
                <CameraModal
                    onCapture={(image) => {
                        setImagePreview(image);
                        setError(null);
                        setCameraOpen(false);
                    }}
                    onClose={() => setCameraOpen(false)}
                />
            )}
            {pendingAdmin && (
                <AdminCredentialsModal
                    personName={pendingAdmin.name}
                    onConfirm={handleAdminConfirm}
                    onClose={handleAdminClose}
                />)}
        </section>
    );
}

export default AddPerson;
