import "./AdminHeader.css";

// Texten som visas i rubriken. highlight är den orangea delen och kan utelämnas
type HeaderProps = {
  title: string;
  highlight?: string;
};

function AdminHeader({ title, highlight }: HeaderProps) {
  return (
    <header className="header">
      <h1>
        {title}{highlight && <span>{highlight}</span>}
      </h1>
      <div className="header-line"></div>
    </header>
  );
}

export default AdminHeader;
