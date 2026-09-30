"""Frame source: a USB/UVC camera."""

import time

import cv2

from config import (
    CAMERA_INDEX,
    CAPTURE_FOURCC,
    CAPTURE_HEIGHT,
    CAPTURE_WIDTH,
    READ_RETRIES,
    READ_RETRY_DELAY,
)


class Camera:
    def __init__(self, index=CAMERA_INDEX, width=CAPTURE_WIDTH, height=CAPTURE_HEIGHT, fourcc=CAPTURE_FOURCC):
        self.cap = cv2.VideoCapture(index, cv2.CAP_V4L2) if hasattr(cv2, "CAP_V4L2") else cv2.VideoCapture(index)
        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open camera {index}")
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*fourcc))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        # Keep the driver buffer small so read() returns a recent frame, not an old one
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    def read(self):
        """Return the next frame (BGR). Retries failed reads, raises RuntimeError if the camera stays silent."""
        for _ in range(READ_RETRIES):
            ok, frame = self.cap.read()
            if ok:
                return frame
            print("Couldn't read frame")
            time.sleep(READ_RETRY_DELAY)
        raise RuntimeError("Camera stopped delivering frames")

    def close(self):
        self.cap.release()
