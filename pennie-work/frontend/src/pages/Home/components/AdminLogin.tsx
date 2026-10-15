import "./AdminLogin.css";
import { login } from "../../../auth";
import { useState, type SubmitEvent } from "react";
import { useNavigate } from "react-router-dom";

//Tar emot en prop som heter onClose
type AdminLoginProps = {
    onClose: () => void;
};

function AdminLogin({ onClose }: AdminLoginProps) {
    const [error, setError] = useState("");
    const navigate = useNavigate();
    async function handleSubmit(e: SubmitEvent<HTMLFormElement>) {
        //Hindrar sidan från att ladda om
        e.preventDefault();
        //samlar ihop användarnamn och lösenord från formuläret i en lista
        const formData = new FormData(e.currentTarget);
        //talar om för typescript att det är en sträng som hämtas från formuläret
        const username = formData.get("username") as string;
        const password = formData.get("password") as string;
        //skickar uppgifterna till backend, som svarar om de stämmer
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
                        {/*När någon trycker på knappen anropas onClose-funktionen*/}
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