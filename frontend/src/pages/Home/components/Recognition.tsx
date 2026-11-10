import { useEffect } from "react";

export type Person = {
  uuid: string;
  name: string;
  permission: string;
  description: string | null;
  image: string | null;

};

type RecognitionMessage = {
  event: "person_recognized" | "person_not_recognized";
  match_score: number | null;
  person: Person | null;
  approved: boolean;
};

type Props = {
  onRecognized: (person: Person | null) => void;
  onMatchScore: (score: number | null) => void;
  onApproved: (approved: boolean) => void;
};

export default function RecognitionView({ onRecognized, onMatchScore, onApproved }: Props) {
  useEffect(() => {
    const socket = new WebSocket(
      "ws://localhost:8000/recognition/ws"
    );

    socket.onmessage = (event) => {
      const data: RecognitionMessage = JSON.parse(event.data);
      console.log("Resultat från backend:", data);

      // Both events update the view; person is null on a denied attempt,
      // which also clears any previously shown person.
      if (data.event === "person_recognized" || data.event === "person_not_recognized") {
        onRecognized(data.person);
        onMatchScore(data.match_score);
        onApproved(data.approved);
      }
    };

    return () => socket.close();
  }, [onRecognized, onMatchScore, onApproved]);

  return null;
}