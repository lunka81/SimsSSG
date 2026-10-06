import "./Header.css";
import { logout } from "../../../auth";
import { useNavigate } from "react-router-dom";

function Header() {
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/");
  }
  return (
    <header className="header">
      <div className="header-content">
        <h1>Admin <span>side</span></h1>
        <button type="button" className="logout-button" onClick={handleLogout}>
          Log out
        </button>
      </div>
      <div className="header-line"></div>
    </header>
  );
}

export default Header;