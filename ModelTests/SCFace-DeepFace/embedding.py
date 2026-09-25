"""Turns a face image into an embedding vector using DeepFace."""

import cv2
import numpy as np
from deepface import DeepFace
from deepface.commons import weight_utils
from deepface.models.facial_recognition import SFace

from config import MODEL_NAME, DETECTOR_BACKEND, ENFORCE_DETECTION, USE_CUDA


def move_sface_to_gpu():
    """DeepFace always runs SFace through OpenCV on the CPU.

    This replaces DeepFace's cached SFace model with one that runs on the GPU.
    """
    weights_file = weight_utils.download_weights_if_necessary(
        file_name="face_recognition_sface_2021dec.onnx", source_url=SFace.WEIGHTS_URL
    )
    sface = DeepFace.build_model(model_name="SFace")
    sface.model.model = cv2.FaceRecognizerSF.create(
        model=weights_file,
        config="",
        backend_id=cv2.dnn.DNN_BACKEND_CUDA,
        target_id=cv2.dnn.DNN_TARGET_CUDA,
    )


if USE_CUDA:
    move_sface_to_gpu()


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
