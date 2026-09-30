import requests
import time
from config import (
	DEVICE_ID, RECOGNITION_COOLDOWN, SEND_INTERVAL, SERVER_TIMEOUT, SERVER_URL,
)
from camera import Camera
from detector import FaceDetector
from extractor import FaceEmbedder
from lock import Lock
from models import ensure_models

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
	payload = {
		"camera_id":DEVICE_ID,
		"timestamp":now,
		"detection_confidence":float(face[-1]),
		"face_width":int(face[2]),
		"face_height":int(face[3]),
		"embedding":[float(v) for v in embedding]
	}
	try:
		response = requests.post(SERVER_URL, json=payload,timeout=SERVER_TIMEOUT)
		if response.status_code == 200:
			result = response.json()
			print(result)
			last_recognition_time = time.time()
			if result.get("recognized"):
				name = result.get("name")
				similarity = result.get("similarity")
				print(f"RECOGNIZED: {name}" f"{similarity:.4f}")
				lock.unlock()
			else:
				lock.deny()
		last_sent = now
	except requests.RequestException as e:
		print("Couldn't contact server:",e)
camera.close()
lock.close()
