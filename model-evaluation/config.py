"""Settings shared by the pipeline (python -m pipeline) and the presentation (python -m presentation)."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Input
DATASET_DIR = BASE_DIR / "dataset"
# One row per dataset image; its "path" column is relative to DATASET_DIR
METADATA_CSV = DATASET_DIR / "metadata.csv"
REFERENCE_DIR = BASE_DIR / "ReferenceImages"
# Reference image of the person in the dataset
SELF_REFERENCE = "001_frontal.JPG"

# Output
MODELS_DIR = BASE_DIR / "model_weights"
RESULTS_CSV = BASE_DIR / "results" / "results.csv"
REPORT_DIR = BASE_DIR / "report"

# Run the ONNX models (recognition and liveness) on the GPU. Falls back to the CPU if CUDA is unavailable
USE_GPU = True

# Face detection (OpenCV YuNet), same values as SimsSSG
DETECTOR_FILE = MODELS_DIR / "face_detection_yunet_2023mar.onnx"
# Detection runs on a copy of the image scaled down to this width
DETECT_WIDTH = 640
# Faces with a lower detection score (0-1) are ignored
DETECTION_THRESHOLD = 0.8
# Non-maximum suppression threshold and max number of candidates kept before suppression
NMS_THRESHOLD = 0.3
TOP_K = 5000
# Faces smaller than this many pixels (width or height) are ignored
MIN_FACE_SIZE = 100

# Face recognition (OpenCV SFace)
# To try another recognition model, change the file, the embedding length and the input size together.
# EMBEDDING_DIM is checked against the model's output when the pipeline starts
RECOGNIZER_FILE = MODELS_DIR / "face_recognition_sface_2021dec.onnx"
EMBEDDING_DIM = 128
# Width and height of the aligned face fed to the model
INPUT_SIZE = (112, 112)
# Cosine similarity needed for approval (same as SimsSSG's OPENCV_REC_THRESHHOLD)
MATCH_THRESHOLD = 0.363

# Liveness (MiniFASNet anti-spoofing). Recorded in the CSV but does not affect the recognition outcome
LIVENESS_V2_FILE = MODELS_DIR / "2.7_80x80_MiniFASNetV2.onnx"
LIVENESS_V1SE_FILE = MODELS_DIR / "4_0_0_80x80_MiniFASNetV1SE.onnx"
LIVENESS_THRESHOLD = 0.5
