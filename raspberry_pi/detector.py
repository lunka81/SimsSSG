"""Face detection with OpenCV YuNet."""

import cv2
import numpy as np

from config import DETECT_WIDTH, DETECTION_THRESHOLD, MIN_FACE_SIZE, NMS_THRESHOLD, TOP_K


class FaceDetector:
    def __init__(self, model_path):
        self.detector = cv2.FaceDetectorYN.create(
            str(model_path), "", (320, 320), DETECTION_THRESHOLD, NMS_THRESHOLD, TOP_K
        )

    def detect(self, image):
        """Return the face to use, or None if no usable face was found.

        The door is used by one person at a time, so a single face is returned: the largest one
        (the person closest to the camera). Faces smaller than MIN_FACE_SIZE are ignored.
        It is a YuNet row in full-resolution coordinates: x, y, w, h, 5 landmarks (x, y each), score.
        """
        height, width = image.shape[:2]
        scale = min(1.0, DETECT_WIDTH / width)
        if scale < 1.0:
            small = cv2.resize(image, (round(width * scale), round(height * scale)), interpolation=cv2.INTER_AREA)
        else:
            small = image
        self.detector.setInputSize((small.shape[1], small.shape[0]))
        _, faces = self.detector.detect(small)
        if faces is None:
            return None
        faces = faces.astype(np.float32)
        # Scale boxes and landmarks (the first 14 values) back to the full-resolution frame
        faces[:, :14] /= scale
        faces = [f for f in faces if f[2] >= MIN_FACE_SIZE and f[3] >= MIN_FACE_SIZE]
        if not faces:
            return None
        return max(faces, key=lambda f: f[2] * f[3])
