# Admin login with token verification

This is the flow for a real admin login, using a signed token (JWT), which is the most common setup with FastAPI.

## 1. One-time setup

- Add an `admins` table with a username and a **hashed** password. Use bcrypt or argon2, never store the plain password.
- Put a `SECRET_KEY` in `.env` for signing tokens.

## 2. Login

- The frontend sends the username and password to a new `POST /api/auth/login`.
- The backend looks up the admin and checks the password against the hash.
  - If it's wrong, it answers **401**.
  - If it's right, it creates a token holding the admin's id and an expiry time (e.g. 1 hour), signs it with `SECRET_KEY`, and sends it back.

## 3. Every admin request after that

- The frontend stores the token (e.g. in `sessionStorage`) and sends it with each request as `Authorization: Bearer <token>`. `api.ts` adds the header in one place.
- A backend dependency, `get_current_admin`, checks the signature and expiry on every request. If either is wrong, it answers **401**.
- It is attached once to the whole employee router, so every endpoint is protected:

  ```python
  employee_router = APIRouter(prefix="/api/employee", dependencies=[Depends(get_current_admin)])
  ```

## 4. Expiry and logout

- When the token expires, requests get 401. The frontend catches that and sends the admin back to the login.
- Logging out just means the frontend deletes the token.

## What stays the same

The Pi keeps using `X-API-Key` on `/recognition/identify`. Admins and devices authenticate separately.

## One snag to plan for

The face images are loaded with `<img src="...">`, and the browser can't add an `Authorization` header to those requests. There are two options:

- **Use a cookie instead of the header.** The backend sets the token in an `httpOnly` cookie, and the browser then sends it automatically, including for images. This works here because `localhost:5173` and `localhost:8000` count as the same site for cookies. The frontend has to use `credentials: "include"` in `fetch`, which the CORS setup (`allow_credentials=True`) already allows.
- **Keep the header and load images with `fetch`.** Fetch the image with the header attached, turn it into a blob URL with `URL.createObjectURL`, and set that as the `src`.

For this project the cookie option is less code, and it also keeps the token away from JavaScript.
