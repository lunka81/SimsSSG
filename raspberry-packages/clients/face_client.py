import time
from config.config import RECOGNITION_COOLDOWN, SEND_INTERVAL, USE_HARDWARE_LOCK
from camera.camera import Camera
from recognition.detector import FaceDetector
from recognition.extractor import FaceEmbedder
from models.models import ensure_models
from clients.uploader import recognize

if USE_HARDWARE_LOCK:
	from hardware.lock import Lock
else:
	from hardware.fake_lock import FakeLock as Lock

lock = Lock()

YUNET_MODEL, SFACE_MODEL = ensure_models()

print("Loading Models")
detector = FaceDetector(YUNET_MODEL)
embedder = FaceEmbedder(SFACE_MODEL)

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
