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

            <main className="app">
                <Outlet />
            </main>
        </div>
    );
}

export default AdminLayout;