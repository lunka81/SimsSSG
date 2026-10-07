"""Settings for the face recognition client (runs on a Raspberry Pi)."""
import os
from pathlib import Path

from dotenv import load_dotenv

#BASE_DIR = Path(__file__).parent
# Downloaded ONNX models
BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

# Modellfiler hålls separat från Python-package models.
MODELS_DIR = BASE_DIR / "model_weights"

DEVICE_ID = os.environ["DEVICE_ID"]
DEVICE_API_KEY = os.environ["DEVICE_API_KEY"]

BACKEND_URL = os.environ["BACKEND_URL"].rstrip("/")
SERVER_URL = f"{BACKEND_URL}/recognition/identify"
SERVER_TIMEOUT = 5

# Name sent along with every request so the server knows which device it came from
#DEVICE_ID = "raspberry-pi-01"

# Recognition server
#SERVER_URL = "http://......:8000/recognize"
# Seconds to wait for the server before giving up
#SERVER_TIMEOUT = 5

# Camera
# Index of the camera, /dev/video<index> on Linux
CAMERA_INDEX = 0
#CAPTURE_WIDTH = 640
#CAPTURE_HEIGHT = 480
CAPTURE_WIDTH = 1980
CAPTURE_HEIGHT = 1200

# Face detection (OpenCV YuNet)
# Detection runs on a copy of the frame scaled down to this width, which keeps large frames fast.
# The face is then cropped from the full resolution frame for the embedding
DETECT_WIDTH = 640
# Faces with a lower detection score (0-1) are ignored
DETECTION_THRESHOLD = 0.8
# Non-maximum suppression threshold and max number of candidates kept before suppression
NMS_THRESHOLD = 0.3
TOP_K = 5000
# Faces smaller than this many pixels (width or height) are ignored
MIN_FACE_SIZE = 100

# Timing, in seconds
# Minimum time between two requests to the server
SEND_INTERVAL = 1.0
# Pause after a successful server response before scanning again
RECOGNITION_COOLDOWN = 5
# How long the red LED stays on after a failed recognition
FAIL_COOLDOWN = 2

# Set to False to run without the Pi hardware (e.g. on a PC): the lock is replaced by
# FakeLock, which only prints what the servo and LEDs would do
USE_HARDWARE_LOCK = False

# GPIO (BCM pin numbers)
SERVO_PIN = 18
GREEN_LED_PIN = 17
RED_LED_PIN = 16
# Servo pulse widths in seconds and the frame width of its PWM signal
SERVO_MIN_PULSE = 0.5 / 1000
SERVO_MAX_PULSE = 2.5 / 1000
SERVO_FRAME_WIDTH = 3 / 1000
# Servo angles for the locked and unlocked positions
SERVO_LOCKED_ANGLE = 0
SERVO_UNLOCKED_ANGLE = 90

# Pixel format asked from the camera. Most USB cameras only reach high resolutions with MJPG
CAPTURE_FOURCC = "MJPG"
# A failed frame read is retried this many times (waiting READ_RETRY_DELAY seconds between
# tries) before the camera is considered lost
READ_RETRIES = 50
READ_RETRY_DELAY = 0.1
