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

export type RecognitionResult =
    | null
    | {status: "granted"; person: Person}
    | {status: "denied"}

type Props = {
  onResult: (result: RecognitionResult) => void;
};

export default function RecognitionView({ onResult }: Props) {
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
        onResult({status: "granted", person: data.person});
      } else if (data.event === "person_not_recognized") {
        onResult({status: "denied"});
      }
    };

    return () => socket.close();
  }, [onResult]);

  return null;
}