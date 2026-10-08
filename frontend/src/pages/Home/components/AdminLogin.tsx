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
    {/*Hindrar sidan från att ladda om*/ }
    function handleSubmit(e: SubmitEvent<HTMLFormElement>) {
        e.preventDefault();
        //samlar ihop användarnamn och lösenord från formuläret i en lista
        const formData = new FormData(e.currentTarget);
        //talar om för typescript att det är en sträng som hämtas från formuläret
        const username = formData.get("username") as string;
        const password = formData.get("password") as string;
        //funktionsanrop till login-funktionen i auth.ts som returnerar true eller false beroende på om användarnamn och lösenord är korrekt
        if (!login(username, password)) {
            setError("Wrong username or password");
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
                        <button type="submit" className="login-button">
                            Login
                        </button>
                        {/*När någon trycker på knappen anropas onClose-funktionen*/}
                        <button type="button" onClick={onClose} className="cancel-button">
                            Cancel
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default AdminLogin;