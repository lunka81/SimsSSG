import cv2
import numpy as np
import requests
import time
#from gpiozero import LED
from gpiozero import AngularServo, LED

from config import (
	DETECTION_THRESHOLD, DEVICE_ID, FAIL_COOLDOWN, GREEN_LED_PIN, MIN_FACE_SIZE, NMS_THRESHOLD,
	RECOGNITION_COOLDOWN, RED_LED_PIN, SEND_INTERVAL, SERVER_TIMEOUT,
	SERVER_URL, SERVO_LOCKED_ANGLE, SERVO_PIN, SERVO_UNLOCKED_ANGLE, TOP_K,
)
from camera import Camera
from models import ensure_models

servo = AngularServo(SERVO_PIN, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000, frame_width=3/1000)
servo.value = 0
GREEN_LED = LED(GREEN_LED_PIN)
RED_LED = LED(RED_LED_PIN)
UNLOCKED = False

YUNET_MODEL, SFACE_MODEL = ensure_models()

print("Loading Models")
detector = cv2.FaceDetectorYN.create(
str(YUNET_MODEL),
"",
(320,320),
DETECTION_THRESHOLD,
NMS_THRESHOLD,
TOP_K)
print("Loading Sface")

recognizer = cv2.FaceRecognizerSF.create(
str(SFACE_MODEL),
""
)

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
		
	height, width = frame.shape[:2]
	detector.setInputSize((width,height))
	_, faces = detector.detect(frame)
	if faces is None:
		continue
	for face in faces:

		confidence = float(face[-1])
		if confidence < DETECTION_THRESHOLD:
			continue
		x,y,w,h = map(int, face[:4])
		
		if w < MIN_FACE_SIZE or h < MIN_FACE_SIZE:
			continue
		now = time.time()
		if now - last_sent < SEND_INTERVAL:
			continue
		aligned_face = recognizer.alignCrop(frame, face)
		feature = recognizer.feature(aligned_face)
		embedding = feature.flatten().astype(np.float32)
		norm = np.linalg.norm(embedding)

		if norm==0:
			continue
		embedding = embedding / norm
		embedding = embedding.tolist()
		payload = {
			"camera_id":DEVICE_ID,
			"timestamp":float(time.time()),
			"detection_confidence":float(confidence),
			"face_width":int(w),
			"face_height":int(h),
			"embedding":[float(v) for v in embedding]
		}
		if time.time() - last_recognition_time < RECOGNITION_COOLDOWN:
			continue
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
		break
camera.close()

