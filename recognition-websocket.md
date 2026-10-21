# Recognition WebSocket (live updates for the start page)

Every time the Raspberry Pi sends a face to the backend, the backend pushes an event over a WebSocket to every logged-in admin page that is connected. The start page uses it to show who just walked up to the camera.

## Before you start

1. **Install the new requirement.** `websockets` was added to `requirements.txt`. Without it the backend can't accept WebSocket connections at all, and every connection attempt fails. Run `pip install -r requirements.txt` and restart the backend.
2. **You must be logged in.** The socket requires the same admin token as the other admin endpoints.

## Connecting

```
ws://localhost:8000/recognition/ws?token=<admin token>
```

A browser WebSocket can't send an `Authorization` header, so the token goes in the query string instead. Encode it with `encodeURIComponent`.

```ts
import { BACKEND_URL, getToken } from "../auth";

const WS_URL = BACKEND_URL.replace(/^http/, "ws") + "/recognition/ws";

export function connectRecognition(onEvent: (event: RecognitionEvent) => void): WebSocket {
  const ws = new WebSocket(`${WS_URL}?token=${encodeURIComponent(getToken() ?? "")}`);
  ws.onmessage = (msg) => onEvent(JSON.parse(msg.data));
  return ws;
}
```

Building the URL from `BACKEND_URL` means `http://` becomes `ws://` now, and `https://` becomes `wss://` automatically if the backend moves to HTTPS.

The frontend never has to send anything over the socket. It only listens.

## Events

Each message is a JSON object with an `event` field. There are two kinds.

**Someone was recognized and let in:**
```json
{
  "event": "person_recognized",
  "person": {
    "uuid": "337b982f-ad2c-44ad-8a67-919cf8e1a7cd",
    "name": "Anna Andersson",
    "permission": "Standard",
    "description": null,
    "image": "data:image/jpeg;base64,/9j/4AAQ..."
  }
}
```

**Someone was not recognized (access denied):**
```json
{
  "event": "person_not_recognized",
  "person": null
}
```

The denied event carries no information about who it was or how close the match was. Ask the backend team if the page needs to show more.

```ts
export type RecognitionEvent =
  | {
      event: "person_recognized";
      person: {
        uuid: string;
        name: string;
        permission: Permission; // "Standard" | "Admin" | "Limited", from api/employees.ts
        description: string | null;
        image: string | null; // data URL, works directly in <img src={...}>
      };
    }
  | { event: "person_not_recognized"; person: null };
```

`image` is already a complete data URL (JPEG or PNG), so it can be used as `<img src={person.image} />` without any extra request.

## Things to know

- **No history.** The socket only sends events that happen *after* you connect. When the start page loads, it shows nothing until the next person walks up to the camera.
- **Every connected tab gets every event.** Two admins with the start page open both see the same updates.
- **A wrong or expired token makes the connection fail.** The backend rejects the handshake with 403. The browser doesn't let you read that status code: you only get `onerror` followed by `onclose` with code `1006`, which looks the same as the backend being down. If the socket closes without ever opening, check the token with a normal request. For example, if `GET /api/employee_logs/?limit=1` answers 401, call `logout()` and send the admin to the login.
- **The token is only checked when connecting.** Tokens expire after 1 hour, but a socket that's already open stays open. After a new login, close the old socket and connect again with the new token.
- **Close the socket on logout** (`ws.close()`), so a logged-out page stops receiving names and photos.
- **No automatic reconnect.** If the backend restarts or the network drops, `onclose` fires and the socket is gone. To recover, reconnect after a short delay, for example 2 seconds. Stop reconnecting if the token is no longer valid (see above).
- **React:** open the socket in a `useEffect` and close it in the cleanup function. In development, React's StrictMode runs effects twice, and without the cleanup you get two connections and every event twice.

```tsx
useEffect(() => {
  const ws = connectRecognition((event) => {
    if (event.event === "person_recognized") setPerson(event.person);
    else setPerson(null); // or show an "access denied" state
  });
  return () => ws.close();
}, []);
```

## Summary of failure cases

| Situation | What the frontend sees |
|---|---|
| No token, wrong token, expired token, or the admin was deleted | `onerror`, then `onclose` (code 1006), and the socket never opens |
| Backend not running, or `websockets` not installed | Same as above |
| Backend restarts while connected | `onclose`. Reconnect. |
| Token expires while connected | Nothing. The socket keeps working until it is closed. |
