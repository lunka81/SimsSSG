import time
from config import RECOGNITION_COOLDOWN, SEND_INTERVAL
from camera import Camera
from detector import FaceDetector
from extractor import FaceEmbedder
from lock import Lock
from models import ensure_models
from uploader import recognize
from liveness import LivenessChecker

lock = Lock()

YUNET_MODEL, SFACE_MODEL = ensure_models()

print("Loading models")
detector = FaceDetector(YUNET_MODEL)
embedder = FaceEmbedder(SFACE_MODEL)
liveness = LivenessChecker(threshold=0.5)
print("Models loaded")

camera = Camera()
print("Camera opened")

last_sent = 0
last_recognition_time = 0


def yunet_to_bbox(face):
    x, y, w, h = face[0:4]
    return int(x), int(y), int(x + w), int(y + h)


while True:
    frame = camera.read()
    lock.update()

    if time.time() - last_recognition_time < RECOGNITION_COOLDOWN:
        continue

    face = detector.detect(frame)
    if face is None:
        continue

    now = time.time()
    if now - last_sent < SEND_INTERVAL:
        continue

    embedding = embedder.embed(frame, face)
    if embedding is None:
        continue
    last_sent = now

    result = recognize(face, embedding, now)
    if result is None:
        continue

    bbox = yunet_to_bbox(face)
    live = liveness.check(frame, bbox)

    last_recognition_time = time.time()

    name = result.get("name")
    similarity = result.get("similarity")
    recognised = result.get("recognized")

    print(f"recognised={recognised} name={name} "
          f"live={live['live']:.4f} scores={live['scores']}")

    if recognised and live["is_live"]:
        print(f"GRANTED: {name} {similarity:.4f} live {live['live']:.2f}")
        lock.unlock()
    elif recognised and not live["is_live"]:
        print(f"SPOOF ATTEMPT: someone presented a fake of {name}, "
              f"live {live['live']:.2f}")
        lock.deny()
    else:
        print(f"DENIED: not recognised, live {live['live']:.2f}")
        lock.deny()

camera.close()
lock.close()