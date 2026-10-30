import { useEffect, useState } from "react";
import HomeHeader from "./components/HomeHeader";
import ImageCard from "./components/ImageCard";
import Confidence from "./components/Confidence";
import AccessRes from "./components/AccessRes";
import AdminLogin from "./components/AdminLogin";
import RecognitionView from "./components/Recognition";
import type { RecognitionResult } from "./components/Recognition";
import "./Home.css";

// Example trainings shown for every recognised person.
// Not fetched from the backend yet
const TRAININGS = ["Introduction Fire safety",
  "SSG Entre Contractor Safety",
  "Information security and data protection"]

// Time in milliseconds before the result is cleared and the view waits for the next person
const RESET_DELAY_MS = 6000;

/**
 * The access view. Shows the result from the camera in real time: who the person is,
 * their picture and whether access is granted or denied.
 * Ctrl + Alt + A opens the admin login.
 */
function Home() {
  // Fixed example value. The real confidence is not sent to the frontend yet
  const confidence = 80;

  const [isAdminOpen, setIsAdminOpen] = useState(false);
  // The latest result from the backend. null while waiting for a person
  const [result, setResult] = useState<RecognitionResult>(null);

  const person = result !== null && result.status === "granted" ? result.person : null;
  const denied = result !== null && result.status === "denied";

  // Opens the admin login with the keyboard shortcut Ctrl + Alt + A
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

  // Clears the result after RESET_DELAY_MS. A new result restarts the timer
  useEffect(() => {
    if (result === null) return;

    const timer = setTimeout(() => setResult(null), RESET_DELAY_MS);

    return () => clearTimeout(timer);
  }, [result]);

  return (
    <main className="app">
      <RecognitionView onResult={setResult} />

      <div className="content">
        <HomeHeader name={person?.name} />

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

                  <dt>Department</dt>
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
            title={person ? "Matching image found" : denied ? "No match found" : ""}
            image={person?.image ?? undefined}>
            {denied ? (
              <div className="no-match" role="alert">
                <h3>No match found</h3>
                <p>No person in the database matches the person in front of the camera.</p>
              </div>
            ) : undefined}
          </ImageCard>
        </section>

        <section className="access-res">
          {result !== null && <AccessRes approved={person !== null} />}
        </section>
      </div>
    </main>
  );
}

export default Home;