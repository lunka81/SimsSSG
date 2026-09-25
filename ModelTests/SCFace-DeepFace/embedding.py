"""Turns a face image into an embedding vector using DeepFace."""

import os

# RetinaFace is built with the Keras 2 API, so use tf-keras instead of Keras 3.
# Must be set before TensorFlow is imported
os.environ.setdefault("TF_USE_LEGACY_KERAS", "1")

import cv2
import numpy as np
import tensorflow as tf
from deepface import DeepFace
from deepface.commons import weight_utils
from deepface.models.facial_recognition import SFace

from config import MODEL_NAME, DETECTOR_BACKEND, ENFORCE_DETECTION, USE_CUDA


class OnnxSFace:
    """Runs the SFace ONNX model with onnxruntime on the GPU.

    Drop-in replacement for cv2.FaceRecognizerSF: feature() takes a 112x112 BGR
    uint8 face and returns a (1, 128) embedding, with the same preprocessing as OpenCV.
    """

    def __init__(self, weights_file):
        import onnxruntime as ort

        # Load the CUDA/cuDNN libraries installed by pip (nvidia-* packages)
        ort.preload_dlls()
        options = ort.SessionOptions()
        options.log_severity_level = 3
        self.session = ort.InferenceSession(
            weights_file, options, providers=["CUDAExecutionProvider"]
        )
        if self.session.get_providers()[0] != "CUDAExecutionProvider":
            raise RuntimeError("onnxruntime could not use the GPU for SFace")
        self.input_name = self.session.get_inputs()[0].name

    def feature(self, face):
        blob = cv2.dnn.blobFromImage(face, 1.0, (112, 112), (0, 0, 0), swapRB=True)
        return self.session.run(None, {self.input_name: blob})[0]


def setup_gpu():
    """Make sure both heavy steps run on the GPU.

    RetinaFace (face detection) runs on TensorFlow. DeepFace always runs SFace through
    OpenCV on the CPU, so its cached SFace model is replaced with one that runs on the GPU.
    """
    gpus = tf.config.list_physical_devices("GPU")
    if not gpus:
        raise RuntimeError("TensorFlow cannot see a GPU, RetinaFace would run on the CPU")
    # Don't let TensorFlow take all GPU memory, onnxruntime needs some too
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)

    weights_file = weight_utils.download_weights_if_necessary(
        file_name="face_recognition_sface_2021dec.onnx", source_url=SFace.WEIGHTS_URL
    )
    sface = DeepFace.build_model(model_name="SFace")
    sface.model.model = OnnxSFace(weights_file)


if USE_CUDA:
    setup_gpu()


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
