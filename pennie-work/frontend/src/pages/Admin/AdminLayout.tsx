import { Navigate, Outlet } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import { isLoggedIn } from "../../auth";

function AdminLayout() {
    if (!isLoggedIn()) {
        return <Navigate to="/" replace />;
    }
    return (
        <div className="admin-layout">
            <Sidebar />

            <main className="admin-main">
                <Outlet />
            </main>
        </div>
    );
}

export default AdminLayout;