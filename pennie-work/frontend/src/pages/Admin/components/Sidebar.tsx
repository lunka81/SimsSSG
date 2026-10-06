import {
    House,
    Users,
    ClipboardList,
    ChartNoAxesColumn,
} from "lucide-react";

import "./Sidebar.css";

function Sidebar() {
    return (
        <aside className="sidebar">
            <div className="sidebar-logo">
                SSG<span>•</span>
            </div>

            <nav className="sidebar-nav">
                <button className="sidebar-item active">
                    <House size={20} />
                    <span>Översikt</span>
                </button>

                <button className="sidebar-item">
                    <Users size={20} />
                    <span>Personer</span>
                </button>

                <button className="sidebar-item">
                    <ClipboardList size={20} />
                    <span>Loggbok</span>
                </button>

                <button className="sidebar-item">
                    <ChartNoAxesColumn size={20} />
                    <span>Statistik</span>
                </button>
            </nav>
        </aside>
    );
}

export default Sidebar;