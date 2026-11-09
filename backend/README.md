# Backend

The central FastAPI server. It:

- stores enrolled people, admin accounts and access logs in PostgreSQL,
- receives face embeddings from the edge device and decides whether to grant access,
- pushes every recognition result to the frontend over a WebSocket,
- provides the API the admin interface uses to log in and manage people.

Stack: Python 3.13, FastAPI, SQLAlchemy 2, PostgreSQL with pgvector, OpenCV (YuNet + SFace for
enrollment), Argon2id password hashing (pwdlib), JWT (PyJWT, HS256).

## Layout

The backend is a Python package (`backend`) and is always run from the **repository root**.

| Folder | Contents |
|---|---|
| `app/app.py` | Creates the FastAPI app, registers routers, CORS, `/device/ping`. Creates the `vector` extension and tables on startup. |
| `db/` | Database engine and session (reads `DATABASE_URL`). |
| `models/` | SQLAlchemy tables: `Employee`, `Admin`, `EmployeeLog`. |
| `schemas/` | Pydantic request and response models. |
| `routes/` | HTTP and WebSocket endpoints. |
| `services/` | Logic: matching, employees, logs, auth, image decoding, WebSocket broadcast. |
| `recognition/` | YuNet face detector and SFace embedder used when enrolling. Model files are downloaded to `recognition/model_weights/` on first start. |
| `scripts/admin_init.py` | Creates the first admin account from the command line. |
| `camera/` | Early development scripts, not used by the running system. |

## Setup

### 1. Database

The backend needs PostgreSQL with the [pgvector](https://github.com/pgvector/pgvector) extension.
The simplest option is the official Docker image:

```bash
docker run -d --name smartaccess-db \
  -e POSTGRES_USER=smartaccess -e POSTGRES_PASSWORD=change-me -e POSTGRES_DB=smartaccess \
  -p 5432:5432 pgvector/pgvector:pg17
```

You don't need to create any tables. On startup the backend runs `CREATE EXTENSION IF NOT EXISTS vector`
and creates all tables, so the database user needs permission to do that. There are no
migrations. If you change a model, you have to alter or recreate the table yourself.

### 2. Python environment

From the repository root:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    Linux/macOS: source .venv/bin/activate
pip install -r backend/requirements.txt
```

### 3. `.env`

Copy [`.env.example`](.env.example) to `backend/.env` and fill it in:

| Key | Meaning |
|---|---|
| `DATABASE_URL` | SQLAlchemy URL, e.g. `postgresql+psycopg2://smartaccess:change-me@localhost:5432/smartaccess`. |
| `SECRET_KEY` | Signs admin login tokens. Use a long random string. Changing it invalidates all tokens. |
| `DEVICE_API_KEY` | Shared secret the edge device sends in the `X-API-Key` header. Must match `edge-device/.env`. |
| `DEBUG` | `true` for detailed error responses during development. |

Generate secrets with `python -c "import secrets; print(secrets.token_urlsafe(32))"`.

## Run

From the repository root:

```bash
uvicorn backend.app.app:app --port 8000
```

Add `--host 0.0.0.0` if the edge device runs on another machine. Interactive API docs are at
<http://localhost:8000/docs>. On the first start the YuNet and SFace models are downloaded from
the OpenCV model zoo, so internet access is needed once.

### Create the first admin

Admins can only be created from the web app by a logged-in admin, so the first one is created
with a script. The image must contain a clearly visible face, since the admin is also enrolled as
a person:

```bash
python -m backend.scripts.admin_init --name "Jane Doe" --username jane --image path/to/face.jpg [--description "Maintenance"]
```

The script asks for the password twice.

## API

| Method and path | Auth | Purpose |
|---|---|---|
| `POST /auth/login` | none | Username and password → JWT (valid 1 hour). |
| `POST /auth/register` | none (see note) | Create an admin together with its employee record. |
| `GET /api/employee/` | JWT | List all enrolled people. |
| `GET /api/employee/{id}` | JWT | One person including their access logs. |
| `GET /api/employee/{id}/image` | JWT | The person's enrollment image (JPEG or PNG). |
| `POST /api/employee/` | JWT | Enroll a person. The image is sent as a data URL; the embedding is computed here. Returns 422 if no face is found. |
| `PATCH /api/employee/{id}` | JWT | Update name, permission, description or image (a new image also updates the embedding). |
| `DELETE /api/employee/{id}` | JWT | Remove a person and their logs. |
| `GET /api/employee_logs/?limit=30&before=<timestamp>` | JWT | Latest approved access attempts, newest first (limit 1–100). |
| `POST /recognition/identify` | `X-API-Key` | Called by the edge device with an embedding. Returns `{approved, employee_uuid, name}`. |
| `WS /recognition/ws` | none | Pushes `person_recognized` / `person_not_recognized` events to the access view. |
| `GET /device/ping` | `X-API-Key` | Lets the edge device test its connection and key. |
| `GET /camera/stream` | none | Leftover from development, streams the server's own webcam. Not used. |

JWT endpoints expect `Authorization: Bearer <token>`.

> **Note:** `/auth/register` should require a JWT, and the frontend already sends one, but the
> route does not check it. Add `dependencies=[Depends(verify_access_token)]` to the route in
> [routes/admin_login_routes.py](routes/admin_login_routes.py) before any real use.

### Request from the edge device

```json
POST /recognition/identify
X-API-Key: <DEVICE_API_KEY>

{
  "camera_id": "gate-1",
  "detection_confidence": 0.93,
  "face_width": 212,
  "face_height": 260,
  "embedding": [0.012, -0.087, "... 128 values, normalized to unit length"]
}
```

## Data model

- **employees**: `uuid`, `name`, `permission` (`Standard`, `Admin`, `Limited`), `description`
  (shown as department in the frontend), `image` (the enrollment photo), `embedding` (`vector(128)`).
- **admin**: one-to-one with an employee (`uuid` is also the foreign key), `username`, `password_hash` (Argon2id).
- **employee_log**: one row per **approved** attempt: employee, `match_score`, `timestamp`,
  `camera_id`, detection confidence and face size. Denied attempts are not stored.

## Matching

[services/comparison_services.py](services/comparison_services.py) runs a nearest-neighbour search in
the database with pgvector's cosine distance and converts it to similarity (`1 - distance`). Access
is approved if the similarity is at least `OPENCV_REC_THRESHHOLD = 0.363`, the recommended
threshold for SFace. Raising it lowers false accepts and raises false rejects. The threshold sweep
in [model-evaluation](../model-evaluation/) shows the trade-off.

The `match_score` shown in the frontend is a 0–100 display value: below the threshold it scales
linearly from 0 to 50, and above it from 50 to 100. It is not a probability.

Embeddings must come from the same model (SFace, 128 values) on both the edge device and the
backend. If you change the recognition model, change it in both places and re-enroll everyone.
