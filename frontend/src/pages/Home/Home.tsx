import { useEffect, useState } from "react";
import Header from "./components/Header";
import ImageCard from "./components/ImageCard";
import Confidence from "./components/Confidence";
import AccessRes from "./components/AccessRes";
import AdminLogin from "./components/AdminLogin";
import RecognitionView from "./components/Recognition";
import type { Person } from "./components/Recognition";
import "./Home.css";

const TRAININGS = ["Introduction Fire safety",
  "SSG Entre Contractor Safety",
  "Information security and data protection"]

function Home() {
  const confidence = 80;

  const [isAdminOpen, setIsAdminOpen] = useState(false);
  const [person, setPerson] = useState<Person | null>(null);

  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.code === "KeyA" && e.ctrlKey && e.altKey && !e.repeat) {
        e.preventDefault();
        setIsAdminOpen(true);
      }
    }

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  return (
    <main className="app">
      <RecognitionView onRecognized={setPerson} />

      <div className="content">
        <Header name={person?.name} />

        {isAdminOpen && <AdminLogin onClose={() => setIsAdminOpen(false)} />}

        <section className="recognition">
          <ImageCard title="Person information">
            {person ? (
              <>
                <dl className="person-info">
                  <dt>Name</dt>
                  <dd>{person.name}</dd>

                  <dt>Permission</dt>
                  <dd>{person.permission}</dd>

                  <dt>Description</dt>
                  <dd>{person.description || "-"}</dd>
                </dl>

                <div className="trainings">
                  <h3>Trainings</h3>
                  <ul className="training-list">
                    {TRAININGS.map((training) => (
                      <li key={training}>
                        <span className="training-check">✓</span>
                        {training}
                      </li>
                    ))}
                  </ul>
                </div>
              </>
            ) : (
              <p>Waiting for identification...</p>
            )}
          </ImageCard>

          <Confidence value={confidence} />

          <ImageCard
            title={person ? "Matching image found" : ""}
            image={person?.image ?? undefined}
          />
        </section>

        <section className="access-res">
          <AccessRes confidence={confidence} />
        </section>
      </div>
    </main>
  );
}

export default Home;