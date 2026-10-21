import "./Header.css";

type HeaderProps = {
  name?: string;
};

function Header({ name }: HeaderProps) {
  return (
    <header className="home-header">
      <div className="home-header-left">
        {/*span taggen används för att ge ett specifikt utseende till en del av texten */}
        <h1>Welcome {name && <span>{name}</span>}!</h1>
        <div className="home-header-line"></div>
      </div>
      <p className="home-header-company">SSG</p>
    </header>
  );
}

export default Header;