# Frontend

The web interface of The Smart Access, a single-page app built with React 19, TypeScript and Vite.
It has two parts:

- **Access view** (`/`): meant for a screen at the gate. It shows each access attempt live:
  the person's name, photo, permission, department and match score when access is granted, or
  "access denied" when no match is found. It resets after 6 seconds.
- **Admin interface** (`/admin`): login-protected pages for managing the system.

The frontend only talks to the [backend](../backend/) and never to the database or the edge device.

## Setup and run

Requires Node.js (developed with Node 24) and a running backend on `http://localhost:8000`.

```bash
cd frontend
npm install
npm run dev        # development server on http://localhost:5173
```

## Using the app

1. Open <http://localhost:5173>. This is the access view.
2. Press **Ctrl + Alt + A** to open the admin login. It is hidden so it isn't visible to people
   passing the gate. The first admin account is created with the backend script, see
   [backend/README.md](../backend/README.md#create-the-first-admin).
3. After login the admin interface has three pages:
   - **Overview**: number of enrolled people and approved entries today.
   - **Persons**: list of everyone enrolled. Add a person with name, permission and department, and a
     photo, either uploaded (JPEG/PNG) or taken with the computer's webcam. Open a person to see
     their details and access history, or remove them. Choosing the **Admin** permission
     also asks for a username and password and creates an admin account.
   - **Logbook**: the latest approved access attempts.

If the backend can't find a face in the photo, the app asks for another one. Use a clear,
front-facing, well-lit photo for best recognition.

The login token is kept in `sessionStorage`. It disappears when the tab is closed and expires
after one hour. When the backend rejects the token, the user is logged out automatically.

## Connecting to a backend on another machine

The backend address is hardcoded in two places:

- `BACKEND_URL` in [src/auth.ts](src/auth.ts) (REST calls)
- the WebSocket URL `ws://localhost:8000/recognition/ws` in
  [src/pages/Home/components/Recognition.tsx](src/pages/Home/components/Recognition.tsx)

The backend also only accepts requests from `http://localhost:5173` (CORS). If you serve the
frontend from another address, add it to `allow_origins` in
[backend/app/app.py](../backend/app/app.py).

## Code layout

| Path | Contents |
|---|---|
| `src/main.tsx`, `src/App.tsx` | Entry point and routes (`/`, `/admin`, `/admin/persons`, `/admin/logbook`). |
| `src/auth.ts` | Login, token storage, admin registration, `BACKEND_URL`. |
| `src/api/employees.ts` | All calls for persons, images and logs. |
| `src/pages/Home/` | Access view: WebSocket listener (`Recognition.tsx`), result cards, hidden admin login. |
| `src/pages/Admin/` | Admin layout (redirects to `/` without a token), overview, persons, logbook, webcam capture. |
| `src/assets/` | Background images. |
