import "./AdminHeader.css";

type HeaderProps = {
  /** The text shown in the heading. */
  title: string;
  /** Optional part of the heading that is shown in orange after the title. */
  highlight?: string;
};

/** Heading at the top of each admin page. */
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
