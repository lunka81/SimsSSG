"""Turns a face image into an embedding vector using DeepFace."""

import numpy as np
from deepface import DeepFace

from config import MODEL_NAME, DETECTOR_BACKEND, ENFORCE_DETECTION


def get_embedding(image_path):
    """Return the L2-normalized embedding of the first face found in the image."""
    faces = DeepFace.represent(
        img_path=str(image_path),
        model_name=MODEL_NAME,
        detector_backend=DETECTOR_BACKEND,
        enforce_detection=ENFORCE_DETECTION,
    )
    embedding = np.array(faces[0]["embedding"])
    return embedding / np.linalg.norm(embedding)
