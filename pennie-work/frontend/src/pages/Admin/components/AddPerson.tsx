import "./AddPerson.css";
import type { SubmitEvent } from "react";
import { useState } from "react";
import { Camera } from "lucide-react";

// Tar emot en funktion från Admin som lägger till personen i listan
type AddPersonProps = {
    onAdd: (name: string, access: string, department: string) => void;
};

function AddPerson({ onAdd }: AddPersonProps) {
    const [imagePreview, setImagePreview] = useState<string | null>(null);
    function handleImageChange(e: React.ChangeEvent<HTMLInputElement>) {
        const file = e.target.files?.[0];

        if (file) {
            const imageUrl = URL.createObjectURL(file);
            setImagePreview(imageUrl);
        }
    }
    function handleSubmit(e: SubmitEvent<HTMLFormElement>) {
        e.preventDefault();
        const formData = new FormData(e.currentTarget);
        const name = formData.get("name") as string;
        const access = formData.get("access") as string;
        const description = formData.get("description") as string;

        // Namn är obligatoriskt
        if (!name) {
            return;
        }

        onAdd(name, access, description);
        // Tömmer formuläret
        e.currentTarget.reset();
    }

    function handleCancel() {
        setImagePreview(null);
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

                <div className="add-person-buttons">
                    <button type="reset" className="cancel-button" onClick={handleCancel}>Cancel</button>
                    <button type="submit" className="login-button">Add person</button>
                </div>
            </form>
        </section>
    );
}

export default AddPerson;