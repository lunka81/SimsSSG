import "./Sidebar.css";
import { logout } from "../../../auth";
import { useNavigate, NavLink } from "react-router-dom";
import { LogOut } from "lucide-react";
import {
    House,
    Users,
    ClipboardList,
} from "lucide-react";

/** Menu on the left side of the admin pages, with links to each page and a logout button. */
function Sidebar() {
    const navigate = useNavigate();

    // Removes the token and goes back to the access view
    function handleLogout() {
        logout();
        navigate("/");
    }
    return (
        <aside className="sidebar">
            <div className="sidebar-logo">
                SSG
            </div>

            <nav className="sidebar-nav">
                <NavLink
                    to="/admin"
                    end
                    className="sidebar-item"
                >
                    <House size={20} />
                    <span>Overview</span>
                </NavLink>

                <NavLink
                    to="/admin/persons"
                    className="sidebar-item"
                >
                    <Users size={20} />
                    <span>Persons</span>
                </NavLink>

                <NavLink
                    to="/admin/logbook"
                    className="sidebar-item"
                >
                    <ClipboardList size={20} />
                    <span>Logbook</span>
                </NavLink>
            </nav>
            <button type="button" className="sidebar-item logout-button" onClick={handleLogout}>
                <LogOut size={20} />
                <span>Log out</span>
            </button>
        </aside >
    );
}

export default Sidebar;