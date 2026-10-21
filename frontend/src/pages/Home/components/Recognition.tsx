import { useEffect } from "react";
import { BACKEND_URL, getToken } from "../../../auth";

export type Person = {
  uuid: string;
  name: string;
  permission: string;
  description: string | null;
  image: string | null;
};

type RecognitionMessage =
  | { event: "person_recognized"; person: Person }
  | { event: "person_not_recognized"; person: null };

type Props = {
  onRecognized: (person: Person) => void;
};

export default function RecognitionView({ onRecognized }: Props) {
  useEffect(() => {
    const token = getToken();
    if (token === null) return;

    const wsUrl = BACKEND_URL.replace("http", "ws");

    const socket = new WebSocket(
      `${wsUrl}/recognition/ws?token=${encodeURIComponent(token)}`
    );

    socket.onmessage = (event) => {
      const data: RecognitionMessage = JSON.parse(event.data);

      if (data.event === "person_recognized") {
        onRecognized(data.person);
      }
    };

    return () => socket.close();
  }, [onRecognized]);

  return null;
}