import "./Header.css";

type HeaderProps = {
  firstname: string;
  surname: string;
};

function Header({ firstname, surname }: HeaderProps) {
  return (
    <header className="header">
      {/*span taggen används för att ge ett specifikt utseende till en del av texten */}
      <h1>Välkommen <span>{firstname} {surname}</span>!</h1>
      <div className="header-line"></div>
    </header>
  );
}

export default Header;