import "./HomeHeader.css";

type HeaderProps = {
  name?: string;
};

function HomeHeader({ name }: HeaderProps) {
  return (
    <header className="home-header">
      <div className="home-header-left">
        <h1>
          Welcome{name ? <> <span>{name}</span></> : null}!
        </h1>

        <div className="home-header-line"></div>
      </div>

      <p className="home-header-company">SSG</p>
    </header>
  );
}

export default HomeHeader;