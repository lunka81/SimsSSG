import "./Header.css";

type HeaderProps = {
  firstname: string;
  surname: string;
};

function Header({ firstname, surname }: HeaderProps) {
  return (
    <header className="home-header">
      <div className="home-header-left">
        {/*span taggen används för att ge ett specifikt utseende till en del av texten */}
        <h1>Welcome <span>{firstname} {surname}</span>!</h1>
        <div className="home-header-line"></div>
      </div>
      <p className="home-header-company">SSG</p>
    </header>
  );
}

export default Header;