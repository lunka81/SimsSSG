import { useEffect } from "react";
import Header from "./components/Header";
import ImageCard from "./components/ImageCard";
import Confidence from "./components/Confidence";
import AccessRes from "./components/AccessRes";
/*Importerar bilder som används på sidan*/
import cameraImage from "../../assets/background3.jpg";
import databaseImage from "../../assets/background2.jpg";
import "./Home.css";

function Home() {
  const confidence = 80;
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if(e.code == "KeyA" && e.ctrlKey && e.altKey) {
        e.preventDefault();
        console.log("Admin");
      }
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, []);
  /*Detta är vad som syns på sidan*/
  return (
    <main className="app">
      <div className="content">
        <Header firstname="Saga" surname="Jonsson" />

        <section className="recognition">
          <ImageCard title="Camera Image" image={cameraImage} showCorners />
          <Confidence value={confidence} />
          <ImageCard title="Database Image" image={databaseImage} />
        </section>

        <section className="access-res">
          <AccessRes confidence={confidence} />
        </section>
      </div>
    </main>
  );
}

export default Home;