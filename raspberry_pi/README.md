# Face recognition client (Raspberry Pi)

Runs next to the door. It watches a USB camera, checks that the face belongs to a real person,
asks the recognition server who it is, and unlocks the door with a servo if the person is recognized.

```
camera -> detect (YuNet) -> liveness (MiniFASNet) -> embed (SFace) -> server -> unlock / deny
```

## Setup

Tested with Python 3.12. Very new Python versions may not have `onnxruntime` wheels yet.

```bash
cd raspberry_pi
python3 -m venv .venv
source .venv/bin/activate          # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

`gpiozero` is only installed on Linux, since it drives the Pi's GPIO pins.

## Configuration

All settings are in [config.py](config.py). Things to consider:

- The `SERVER_URL` is currently just a temporary value.
- Set `USE_HARDWARE_LOCK = False` when running on a PC without the servo and LEDs.
  The real lock is then replaced by `FakeLock`, which only prints what it would do.
- Change `CAMERA_INDEX` if the wrong camera is opened.

## Running

```bash
python face_client.py
```

The ONNX models are downloaded into `models/` on the first run.

## Files

| File | Purpose |
| --- | --- |
| `face_client.py` | Main loop |
| `config.py` | All settings |
| `camera.py` | Opens the camera and reads frames |
| `detector.py` | Finds the largest face in the frame (YuNet) |
| `liveness.py` | Rejects photos and screens (MiniFASNet) |
| `extractor.py` | Turns the face into an embedding (SFace) |
| `uploader.py` | Sends the embedding to the server |
| `lock.py` | Servo and LEDs on the Pi |
| `fake_lock.py` | Stand-in for `lock.py` without hardware |
| `models.py` | Downloads the models |

## Server request

`uploader.py` sends a POST to `SERVER_URL` with:

```json
{
  "camera_id": "raspberry-pi-01",
  "timestamp": 1759830000.0,
  "detection_confidence": 0.93,
  "face_width": 312,
  "face_height": 398,
  "embedding": [0.012, -0.034, ...]
}
```

It expects `{"recognized": true, "name": "...", "similarity": 0.71}`, or `{"recognized": false}`.

## Hardware (BCM pins)

| Part | Pin |
| --- | --- |
| Servo | 18 |
| Green LED | 17 |
| Red LED | 16 |
