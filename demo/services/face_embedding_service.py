from functools import lru_cache
from pathlib import Path
from threading import Lock

import cv2
import numpy as np


MODEL_DIR = (
    Path(__file__).resolve().parents[1] / "model_weights"
)


class FaceEmbeddingService:
    def __init__(self):
        detector_path = MODEL_DIR / "face_detection_yunet_2023mar.onnx"
        recognizer_path = MODEL_DIR / "face_recognition_sface_2021dec.onnx"

        for path in (detector_path, recognizer_path):
            if not path.is_file():
                raise FileNotFoundError(f"Modellfil saknas: {path}")

        self.detector = cv2.FaceDetectorYN.create(
            str(detector_path),
            "",
            (320, 320),
            0.8,     # Detection threshold
            0.3,     # NMS threshold
            5000,    # Top K
        )

        self.recognizer = cv2.FaceRecognizerSF.create(
            str(recognizer_path),
            "",
        )

        # Modellerna delas mellan samtidiga registreringsanrop.
        self._lock = Lock()

    def create_embedding(self, image: np.ndarray) -> list[float]:
        height, width = image.shape[:2]

        # Samma detektionsskalning som i Raspberry-koden.
        scale = min(1.0, 640 / width)

        if scale < 1.0:
            detection_image = cv2.resize(
                image,
                (round(width * scale), round(height * scale)),
                interpolation=cv2.INTER_AREA,
            )
        else:
            detection_image = image

        with self._lock:
            self.detector.setInputSize(
                (
                    detection_image.shape[1],
                    detection_image.shape[0],
                )
            )

            _, faces = self.detector.detect(detection_image)

            if faces is None or len(faces) == 0:
                raise ValueError("Inget ansikte hittades i bilden.")

            # Vid registrering ska bilden innehålla en enda person.
            if len(faces) != 1:
                raise ValueError(
                    "Bilden måste innehålla exakt ett ansikte."
                )

            face = faces[0].astype(np.float32).copy()

            # Återställ koordinater till originalbildens storlek.
            face[:14] /= scale

            if face[2] < 100 or face[3] < 100:
                raise ValueError(
                    "Ansiktet är för litet. Ta bilden närmare kameran."
                )

            aligned = self.recognizer.alignCrop(image, face)

            embedding = (
                self.recognizer.feature(aligned)
                .flatten()
                .astype(np.float32)
            )

        if embedding.size != 128:
            raise ValueError("Modellen gav fel embedding-dimension.")

        if not np.isfinite(embedding).all():
            raise ValueError("Modellen gav ogiltiga embedding-värden.")

        norm = float(np.linalg.norm(embedding))

        if norm == 0:
            raise ValueError("Kunde inte skapa en användbar embedding.")

        return (embedding / norm).tolist()


@lru_cache(maxsize=1)
def get_face_embedding_service() -> FaceEmbeddingService:
    return FaceEmbeddingService()