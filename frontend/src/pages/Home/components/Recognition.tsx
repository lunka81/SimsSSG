import { useEffect } from "react";
import { BACKEND_URL } from "../../../auth";

/** A recognised person as the backend sends it over the WebSocket. */
export type Person = {
  uuid: string;
  name: string;
  permission: string;
  description: string | null;
  /** The person's picture, or null if there is none. */
  image: string | null;
};

// A message from the backend about one recognition attempt
type RecognitionMessage =
  | { event: "person_recognized"; person: Person }
  | { event: "person_not_recognized"; person: null };

/** The result shown in the access view. null while waiting for a person. */
export type RecognitionResult =
    | null
    | {status: "granted"; person: Person}
    | {status: "denied"}

type Props = {
  /** Called every time the backend sends a new result. */
  onResult: (result: RecognitionResult) => void;
};

/**
 * Opens a WebSocket to the backend and listens for recognition results from the camera.
 * Shows nothing itself. The connection is closed when the component is removed.
 */
export default function RecognitionView({ onResult }: Props) {
  useEffect(() => {
    // Changes http://... to ws://...
    const wsUrl = BACKEND_URL.replace("http", "ws");

    const socket = new WebSocket(`${wsUrl}/recognition/ws`);

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