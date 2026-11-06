import { Navigate, Outlet } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import { isLoggedIn } from "../../auth";

/**
 * Shared layout for all admin pages: the sidebar and the current page.
 * Sends the user back to the access view if no admin is logged in.
 */
function AdminLayout() {
    if (!isLoggedIn()) {
        return <Navigate to="/" replace />;
    }
    return (
        <div className="admin-layout">
            <Sidebar />

            {/* Outlet shows the admin page that matches the address */}
            <main className="admin-main">
                <Outlet />
            </main>
        </div>
    );
}

export default AdminLayout;
