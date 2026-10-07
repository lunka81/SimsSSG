import "./AddPerson.css";
import type { SubmitEvent } from "react";
import { useState } from "react";
import { Camera } from "lucide-react";
import { createEmployee, fileToDataUrl, type Employee, type Permission } from "../../../api";

// Tar emot en funktion från Admin som lägger till den sparade personen i listan
type AddPersonProps = {
    onAdd: (employee: Employee) => void;
};

function AddPerson({ onAdd }: AddPersonProps) {
    const [imagePreview, setImagePreview] = useState<string | null>(null);
    const [error, setError] = useState("");
    const [saving, setSaving] = useState(false);
    function handleImageChange(e: React.ChangeEvent<HTMLInputElement>) {
        const file = e.target.files?.[0];

        if (file) {
            const imageUrl = URL.createObjectURL(file);
            setImagePreview(imageUrl);
        }
    }
    async function handleSubmit(e: SubmitEvent<HTMLFormElement>) {
        e.preventDefault();
        // Sparas innan await, eftersom e.currentTarget blir null efteråt
        const form = e.currentTarget;
        const formData = new FormData(form);
        const name = (formData.get("name") as string).trim();
        const permission = formData.get("access") as Permission;
        const description = (formData.get("description") as string).trim();
        const picture = formData.get("picture") as File;

        // Namn och bild är obligatoriska
        if (!name) {
            setError("Name is required");
            return;
        }
        if (!picture || picture.size === 0) {
            setError("Profile picture is required");
            return;
        }

        setError("");
        setSaving(true);
        try {
            const employee = await createEmployee({
                name: name,
                permission: permission,
                // Tom beskrivning skickas som null
                description: description || null,
                img: await fileToDataUrl(picture),
            });
            onAdd(employee);
            // Tömmer formuläret
            form.reset();
            setImagePreview(null);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Could not save person");
        } finally {
            setSaving(false);
        }
    }

    function handleCancel() {
        setImagePreview(null);
        setError("");
    }

    return (
        <section className="add-person">
            <h2>Add new person</h2>

            <form className="add-person-form" onSubmit={handleSubmit}>
                <div className="add-person-fields">
                    <label>
                        <span>Name <span className="required">*</span></span>
                        <input type="text" name="name" placeholder="Kalle Karlsson" />
                    </label>
                    <label>
                        <span>Access permissions <span className="required">*</span></span>
                        <select name="access">
                            <option value="Standard">Standard</option>
                            <option value="Admin">Admin</option>
                            <option value="Limited">Limited</option>
                        </select>
                    </label>
                    <label>
                        Description (optional)
                        <input type="text" name="description" placeholder="T.ex. avdelning, roll, företag" />
                    </label>
                </div>

                <div className="add-person-picture">
                    <p>Profile picture <span className="required">*</span></p>

                    <div className="picture-row">
                        <div className="picture-preview">
                            {imagePreview && (
                                <img src={imagePreview} alt="Profile preview" />
                            )}
                        </div>

                        <label className="picture-upload">
                            <Camera size={28} />
                            <span className="upload-title">Upload picture</span>
                            <span className="upload-hint">JPG, PNG (max 5 MB)</span>
                            <input type="file" name="picture" accept="image/png, image/jpeg" onChange={handleImageChange} hidden />
                        </label>
                    </div>
                </div>

                {error && <p className="login-error">{error}</p>}

                <div className="add-person-buttons">
                    <button type="reset" className="cancel-button" onClick={handleCancel}>Cancel</button>
                    <button type="submit" className="login-button" disabled={saving}>
                        {saving ? "Saving..." : "Add person"}
                    </button>
                </div>
            </form>
        </section>
    );
}

export default AddPerson;