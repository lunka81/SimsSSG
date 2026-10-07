"""Face embedding with OpenCV SFace."""

import cv2
import numpy as np


class FaceEmbedder:
    def __init__(self, model_path):
        self.recognizer = cv2.FaceRecognizerSF.create(str(model_path), "")

    def embed(self, image, face):
        """Align and crop the face from the full-resolution frame.

        Returns a unit-length 128-d embedding, or None if the embedding is all zeros."""
        aligned = self.recognizer.alignCrop(image, face)
        embedding = self.recognizer.feature(aligned).flatten().astype(np.float32)
        norm = np.linalg.norm(embedding)
        if norm == 0:
            return None
        return embedding / norm
