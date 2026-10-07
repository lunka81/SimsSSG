import time
from config import RECOGNITION_COOLDOWN, SEND_INTERVAL, USE_HARDWARE_LOCK
from camera import Camera
from detector import FaceDetector
from extractor import FaceEmbedder
from liveness import LivenessChecker
from models import ensure_models
from uploader import recognize

if USE_HARDWARE_LOCK:
	from lock import Lock
else:
	from fake_lock import FakeLock as Lock

lock = Lock()

YUNET_MODEL, SFACE_MODEL = ensure_models()

print("Loading Models")
detector = FaceDetector(YUNET_MODEL)
embedder = FaceEmbedder(SFACE_MODEL)
liveness = LivenessChecker()

print("Models Loaded")

camera = Camera()

print("Camera opened")

last_sent = 0
last_recognition_time = 0

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

	# Check that it is a real person and not a photo or screen
	x, y, w, h = face[:4]
	live = liveness.check(frame, (x, y, x + w, y + h))
	if not live["is_live"]:
		print(f"Spoof suspected, live score {live['live']:.2f}")
		last_sent = now
		continue

	embedding = embedder.embed(frame, face)
	if embedding is None:
		continue
	last_sent = now

	# Send face embedding to server
	result = recognize(face, embedding, now)
	if result is None:
		continue
	print(result)

	# Unlock or lock door
	last_recognition_time = time.time()
	if result.get("recognized"):
		name = result.get("name")
		similarity = result.get("similarity")
		print(f"RECOGNIZED: {name}" f"{similarity:.4f}")
		lock.unlock()
	else:
		lock.deny()
camera.close()
lock.close()
