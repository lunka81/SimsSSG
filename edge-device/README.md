# Edge device (Raspberry Pi client)

This runs at the gate. It reads the camera, finds a face, checks that it is a live person, and sends
the face embedding to the [backend](../backend/). The backend answers approved or denied, and the Pi
moves the lock and LEDs accordingly. A small local API exposes the camera feed and the current status.

Only the embedding (128 numbers) and some metadata leave the device. Camera images are never sent.

Stack: Python 3.12, FastAPI, OpenCV (YuNet detection, SFace embedding), ONNX Runtime
(MiniFASNet liveness), gpiozero (servo and LEDs), requests.

## How the loop works

`RecognitionService` ([services/recognition_service.py](services/recognition_service.py)) starts
in a background thread when the app starts. For each camera frame:

1. **Detect**: YuNet on a copy scaled to 640 px wide. Faces scoring below 0.8 or smaller than
   100×100 px are ignored. If there are several faces, the largest one is used.
2. **Liveness**: two MiniFASNet models check that the face is real and not a photo or screen.
   The face goes on only if the average live score is at least 0.5.
3. **Embed**: SFace aligns the face to 112×112 and produces a 128-dimensional embedding,
   normalized to unit length.
4. **Ask the backend**: POST to `/recognition/identify` with the `X-API-Key` header, at most once
   per second, with a 5 s timeout.
5. **Act**: if approved, the servo unlocks and the green LED turns on for 6 s, then the gate locks again.
   If denied, the red LED blinks for 2 s and scanning resumes after 1.5 s. If there is no
   answer, or the answer is invalid, the gate stays locked.

All of these values are in [config/config.py](config/config.py).

## Hardware

| Part | Connection |
|---|---|
| Raspberry Pi 5 | |
| USB camera | Any USB port (`CAMERA_INDEX = 0`, MJPG) |
| Servo (Waveshare WP5335) | Signal on **GPIO18** (physical pin 12). Powered from an external 6.2–7.0 V supply. |
| Green LED (access granted) | **GPIO17** (physical pin 11), with a current-limiting resistor |
| Red LED (access denied) | **GPIO16** (physical pin 36), with a current-limiting resistor |

The Pi, the servo and the external supply must share a **common ground**. Don't power the servo
from the Pi's 5 V pin.

Without this hardware, for example on a PC, the app uses `FakeLock`, which only prints what the lock
would do. Which one is used is controlled by the `USE_HARDWARE_LOCK` constant in
[config/config.py](config/config.py). It is `False` by default, so **set it to `True` on the Pi**.

## Setup

Run from this folder (`edge-device/`).

On a Raspberry Pi (Raspberry Pi OS):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows for testing without the hardware:

```bash
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copy [`.env.example`](.env.example) to `.env` in this folder and fill it in:

| Key | Meaning |
|---|---|
| `DEVICE_ID` | Name of this device. Sent with every request and stored in the access log. |
| `DEVICE_API_KEY` | Must be identical to `DEVICE_API_KEY` in `backend/.env`. |
| `BACKEND_URL` | Base address of the backend as seen from the Pi, e.g. `http://192.168.1.20:8000`. |

On first start the four model files (YuNet, SFace and two MiniFASNet models) are downloaded to
`model_weights/`, so internet access is needed once.

## Run

```bash
uvicorn main:app --port 8001
```

The backend uses port 8000, so the edge app needs another port when both run on the same machine.
Recognition starts immediately and runs until the app stops.

- `GET /camera/status`: whether the loop is running, the last liveness score and the last error.
- `GET /camera/stream`: the live camera feed in a browser (MJPEG).

## Check scripts

```bash
python -m scripts.test_connection   # calls the backend's /device/ping with the API key
python -m scripts.find_camera       # shows the camera feed in a window, press Q to close
```

Run `test_connection` first when setting up a new device. It confirms both the address and the key.

## Layout

| Path | Contents |
|---|---|
| `main.py` | FastAPI app. Starts and stops the recognition loop. |
| `services/` | `RecognitionService`: the camera loop, run in a background thread. |
| `camera/` | USB camera frame source. |
| `recognition/` | Face detection (YuNet), embedding (SFace), liveness (MiniFASNet) and model download. |
| `clients/` | The request to the backend. |
| `hardware/` | The servo lock and LEDs, plus `FakeLock` for running on a PC. |
| `routes/` | `/camera/status` and `/camera/stream`. |
| `schemas/` | The request and response shape agreed with the backend. |
| `config/` | All settings. |
| `scripts/` | Manual checks for the camera and the backend connection. |
