import requests
import time
#from gpiozero import LED
from gpiozero import AngularServo, LED

from config import (
	DEVICE_ID, FAIL_COOLDOWN, GREEN_LED_PIN, RECOGNITION_COOLDOWN, RED_LED_PIN, SEND_INTERVAL,
	SERVER_TIMEOUT, SERVER_URL, SERVO_LOCKED_ANGLE, SERVO_PIN, SERVO_UNLOCKED_ANGLE,
)
from camera import Camera
from detector import FaceDetector
from extractor import FaceEmbedder
from models import ensure_models

servo = AngularServo(SERVO_PIN, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000, frame_width=3/1000)
servo.value = 0
GREEN_LED = LED(GREEN_LED_PIN)
RED_LED = LED(RED_LED_PIN)
UNLOCKED = False

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
	if time.time() - last_sent > FAIL_COOLDOWN:
		RED_LED.off()
	if time.time() - last_recognition_time < RECOGNITION_COOLDOWN:
		continue
	else:
		if UNLOCKED:
			servo.angle=SERVO_LOCKED_ANGLE
			GREEN_LED.off()
			UNLOCKED = False
		
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
				GREEN_LED.on()
				servo.angle=SERVO_UNLOCKED_ANGLE
				UNLOCKED = True
			else:
				RED_LED.blink(on_time=0.25,off_time=0.25)
		last_sent = now
	except requests.RequestException as e:
		print("Couldn't contact server:",e)
camera.close()
