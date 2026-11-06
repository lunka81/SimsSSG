import "./AdminLogin.css";
import { login } from "../../../auth";
import { useState, type SubmitEvent } from "react";
import { useNavigate } from "react-router-dom";

type AdminLoginProps = {
    /** Closes the login window. */
    onClose: () => void;
};

/** Login window for admins. Opens the admin interface if the login succeeds. */
function AdminLogin({ onClose }: AdminLoginProps) {
    const [error, setError] = useState("");
    const navigate = useNavigate();
    async function handleSubmit(e: SubmitEvent<HTMLFormElement>) {
        // Stops the page from reloading
        e.preventDefault();
        // Collects the username and password from the form
        const formData = new FormData(e.currentTarget);
        // Tells TypeScript that the values from the form are strings
        const username = formData.get("username") as string;
        const password = formData.get("password") as string;
        // Sends the details to the backend, which answers whether they are correct
        try {
            if (!(await login(username, password))) {
                setError("Wrong username or password");
                return;
            }
        } catch {
            setError("Could not reach the server. Please try again.");
            return;
        }
        navigate("/admin");
    }
    return (
        <div className="admin-overlay">
            <div className="admin-modal">
                <h2>Admin login</h2>
                <div className="login-line"></div>
                <form onSubmit={handleSubmit}>
                    <label>
                        Username
                        <input type="text" name="username" autoFocus />
                    </label>
                    <label>
                        Password
                        <input type="password" name="password" />
                    </label>
                    {error && <p className="login-error">{error}</p>}
                    <div className="buttons">
                        <button type="submit" className="button-primary">
                            Login
                        </button>
                        {/* Closes the login window without logging in */}
                        <button type="button" onClick={onClose} className="button-secondary">
                            Cancel
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default AdminLogin;