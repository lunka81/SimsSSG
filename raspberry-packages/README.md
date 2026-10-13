# Raspberry Pi face recognition client

Runs at the door. It reads the camera, finds a face, checks that it is a live person, and sends
the face embedding to the backend. The backend answers approved or denied, and the Pi moves the
lock and LEDs accordingly. A small local API exposes the camera feed and the current status.

## Layout

| Folder | Contents |
|---|---|
| `main.py` | FastAPI app. Starts and stops the recognition loop. |
| `services/` | `RecognitionService`: the camera loop, run in a background thread. |
| `camera/` | USB camera frame source. |
| `recognition/` | Face detection (YuNet), embedding (SFace), liveness (MiniFASNet) and model download. |
| `clients/` | The request to the backend. |
| `hardware/` | The servo lock and LEDs, plus a fake lock for running on a PC. |
| `routes/` | `/camera/status` and `/camera/stream`. |
| `schemas/` | The request and response shape agreed with the backend. |
| `config/` | All settings. |
| `scripts/` | Manual checks for the camera and the backend connection. |

## Setup

```
py -3.12 -m venv .venv
.venv/Scripts/activate
pip install -r requirements.txt
```

Settings are read from `.env` in this folder:

| Key | Meaning |
|---|---|
| `DEVICE_ID` | Name sent with every request so the backend knows which device it came from. |
| `DEVICE_API_KEY` | Must be identical to `DEVICE_API_KEY` in the backend's `.env`. |
| `BACKEND_URL` | Base address of the backend, for example `http://127.0.0.1:8000`. |
| `USE_HARDWARE_LOCK` | Optional. Set to `true` on the Pi to drive the real servo and LEDs. |

The model files are downloaded to `model_weights/` on first start if they are missing.

## Run

Run everything from this folder.

```
uvicorn main:app --port 8001
```

The backend uses port 8000, so the Pi app needs another port when both run on the same machine.

- `GET /camera/status` shows whether the loop is running, the last liveness score and the last error.
- `GET /camera/stream` shows the camera feed.

## Scripts

```
python -m scripts.test_connection
python -m scripts.find_camera
```

`test_connection` calls the backend's `/device/ping` with the API key. `find_camera` shows the
camera feed in a window; press Q to close it.
