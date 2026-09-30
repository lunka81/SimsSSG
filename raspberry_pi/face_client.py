import cv2
import numpy as np
import requests
import time
#from gpiozero import LED
from gpiozero import AngularServo, LED
servo = AngularServo(18, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000, frame_width=3/1000)
servo.value = 0
GREEN_LED = LED(17)
RED_LED = LED(16)
UNLOCKED = False
CAM_WIDTH = 1980
CAM_HEIGHT = 1200
RECOGNITION_COOLDOWN = 5
FAIL_COOLDOWN = 2
CAMERA_ID = 0
SERVER_URL = "http://......:8000/recognize"
YUNET_MODEL = "models/face_detection_yunet_2023mar.onnx"
SFACE_MODEL = "models/face_recognition_sface_2021dec.onnx"

DETECTION_THREASHOLD = 0.8

SEND_INTERVAL = 1.0

print("Loading Models")
detector = cv2.FaceDetectorYN.create(
YUNET_MODEL,
"",
(320,320),
DETECTION_THREASHOLD,
0.3,
5000)
print("Loading Sface")

recognizer = cv2.FaceRecognizerSF.create(
SFACE_MODEL,
""
)

print("Models Loaded")

camera = cv2.VideoCapture(CAMERA_ID)

if not camera.isOpened():
	raise RuntimeError("Error Opening Camera")

camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)

print("Camera opened")

last_sent = 0
last_recognition_time = 0

while True:

	ret, frame = camera.read()
	if not ret:
		print("Couldn't read frame")
		#time.sleep(0.1)
		continue
	if time.time() - last_sent > FAIL_COOLDOWN:
		RED_LED.off()
	if time.time() - last_recognition_time < RECOGNITION_COOLDOWN:
		continue
	else:
		if UNLOCKED:
			servo.angle=0
			GREEN_LED.off()
			UNLOCKED = False
		
	height, width = frame.shape[:2]
	detector.setInputSize((width,height))
	_, faces = detector.detect(frame)
	if faces is None:
		continue
	for face in faces:

		confidence = float(face[-1])
		if confidence < DETECTION_THREASHOLD:
			continue
		x,y,w,h = map(int, face[:4])
		
		if w<100 or h < 100:
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
			"camera_id":"raspberry-pi-01",
			"timestamp":float(time.time()),
			"detection_confidence":float(confidence),
			"face_width":int(w),
			"face_height":int(h),
			"embedding":[float(v) for v in embedding]
		}
		if time.time() - last_recognition_time < RECOGNITION_COOLDOWN:
			continue
		try:
			response = requests.post(SERVER_URL, json=payload,timeout=5)
			if response.status_code == 200:
				result = response.json()
				print(result)
				last_recognition_time = time.time()
				if result.get("recognized"):
					name = result.get("name")
					similarity = result.get("similarity")
					print(f"RECOGNIZED: {name}" f"{similarity:.4f}")
					GREEN_LED.on()
					servo.angle=90
					UNLOCKED = True
				else:
					RED_LED.blink(on_time=0.25,off_time=0.25)
			last_sent = now
		except requests.RequestException as e:
			print("Couldn't contact server:",e)
		break
camera.release()

