"""The SimsSSG face models: YuNet detection, SFace embedding and MiniFASNet liveness.

Detection and face alignment use OpenCV exactly as in SimsSSG. The SFace and MiniFASNet
ONNX models run in onnxruntime, so they can use the GPU.
"""
import cv2
import numpy as np
import onnxruntime as ort

from config import (
    DETECT_WIDTH, DETECTION_THRESHOLD, EMBEDDING_DIM, INPUT_SIZE, LIVENESS_THRESHOLD,
    LIVENESS_V1SE_FILE, LIVENESS_V2_FILE, MIN_FACE_SIZE, NMS_THRESHOLD, TOP_K, USE_GPU,
)

# Only show onnxruntime errors, not its warnings about the model files
ort.set_default_logger_severity(3)
if USE_GPU:
    # Load the CUDA/cuDNN libraries installed by pip (onnxruntime-gpu[cuda,cudnn])
    ort.preload_dlls()


def create_session(model_path):
    providers = ["CPUExecutionProvider"]
    if USE_GPU:
        providers.insert(0, "CUDAExecutionProvider")
    return ort.InferenceSession(str(model_path), providers=providers)


class FaceDetector:
    def __init__(self, model_path):
        self.detector = cv2.FaceDetectorYN.create(
            str(model_path), "", (320, 320), DETECTION_THRESHOLD, NMS_THRESHOLD, TOP_K
        )

    def detect(self, image):
        """Return the largest face, or None if no usable face was found.

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
        # Scale boxes and landmarks (the first 14 values) back to the full-resolution image
        faces[:, :14] /= scale
        faces = [f for f in faces if f[2] >= MIN_FACE_SIZE and f[3] >= MIN_FACE_SIZE]
        if not faces:
            return None
        return max(faces, key=lambda f: f[2] * f[3])


class FaceEmbedder:
    def __init__(self, model_path):
        # OpenCV's SFace is only used for alignCrop, the model itself runs in onnxruntime
        self.aligner = cv2.FaceRecognizerSF.create(str(model_path), "")
        self.session = create_session(model_path)
        self.input_name = self.session.get_inputs()[0].name
        output_dim = self.session.get_outputs()[0].shape[-1]
        if output_dim != EMBEDDING_DIM:
            raise ValueError(
                f"{model_path.name} outputs {output_dim}-d embeddings, but EMBEDDING_DIM in config.py is {EMBEDDING_DIM}"
            )

    def embed(self, image, face):
        """Align and crop the face from the full-resolution image.

        Returns a unit-length embedding, or None if the embedding is all zeros."""
        aligned = self.aligner.alignCrop(image, face)
        # Same preprocessing as cv2.FaceRecognizerSF.feature: resize, BGR -> RGB, no scaling
        blob = cv2.dnn.blobFromImage(aligned, 1.0, INPUT_SIZE, (0, 0, 0), swapRB=True, crop=False)
        embedding = self.session.run(None, {self.input_name: blob})[0].flatten().astype(np.float32)
        norm = np.linalg.norm(embedding)
        if norm == 0:
            return None
        return embedding / norm


class LivenessChecker:
    """MiniFASNet ensemble, as in SimsSSG's recognition/liveness.py."""

    SIZE = 80
    LIVE_INDEX = 1
    # Model file and how much the face box is enlarged before cropping
    MODELS = [(LIVENESS_V2_FILE, 2.7), (LIVENESS_V1SE_FILE, 4.0)]

    def __init__(self):
        self.sessions = []
        for path, scale in self.MODELS:
            session = create_session(path)
            self.sessions.append((session, session.get_inputs()[0].name, scale))

    def _crop(self, image, face, scale):
        """Crop a box around the face enlarged by scale, shifted to stay inside the image."""
        h, w = image.shape[:2]
        x, y, box_w, box_h = [float(v) for v in face[:4]]
        if box_w <= 0 or box_h <= 0:
            return None

        scale = min((h - 1) / box_h, (w - 1) / box_w, scale)
        new_w = box_w * scale
        new_h = box_h * scale
        cx = x + box_w / 2
        cy = y + box_h / 2

        left = cx - new_w / 2
        top = cy - new_h / 2
        right = cx + new_w / 2
        bottom = cy + new_h / 2
        if left < 0:
            right -= left
            left = 0
        if top < 0:
            bottom -= top
            top = 0
        if right > w - 1:
            left -= right - (w - 1)
            right = w - 1
        if bottom > h - 1:
            top -= bottom - (h - 1)
            bottom = h - 1

        crop = image[int(top):int(bottom) + 1, int(left):int(right) + 1]
        if crop.size == 0:
            return None
        return cv2.resize(crop, (self.SIZE, self.SIZE))

    def check(self, image, face):
        """Return (live score 0-1, is_live)."""
        total = np.zeros(3)
        used = 0
        for session, input_name, scale in self.sessions:
            crop = self._crop(image, face, scale)
            if crop is None:
                continue
            blob = crop.astype(np.float32).transpose(2, 0, 1)[np.newaxis]
            logits = session.run(None, {input_name: blob})[0][0]
            exp = np.exp(logits - np.max(logits))
            total += exp / exp.sum()
            used += 1

        if used == 0:
            return 0.0, False
        live = float(total[self.LIVE_INDEX] / used)
        return live, live >= LIVENESS_THRESHOLD
