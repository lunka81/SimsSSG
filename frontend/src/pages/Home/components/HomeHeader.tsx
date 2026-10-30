import "./HomeHeader.css";

type HeaderProps = {
  /** Name of the recognised person. Left out while waiting for a person. */
  name?: string;
};

/** Heading of the access view that welcomes the recognised person. */
function HomeHeader({ name }: HeaderProps) {
  return (
    <header className="home-header">
      <div className="home-header-left">
        {/* The span tag gives the name its own style */}
        <h1>Welcome {name && <span>{name}</span>}!</h1>
        <div className="home-header-line"></div>
      </div>
      <p className="home-header-company">SSG</p>
    </header>
  );
}

export default HomeHeader;