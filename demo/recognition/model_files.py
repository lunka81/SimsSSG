"""Download the ONNX models used by the pipeline."""
from pathlib import Path
import urllib.request

MODELS_DIR = Path(__file__).resolve().parent / "model_weights"

ZOO_URL = "https://github.com/opencv/opencv_zoo/raw/main/models"
DETECTOR_FILE = MODELS_DIR / "face_detection_yunet_2023mar.onnx"
RECOGNIZER_FILE = MODELS_DIR / "face_recognition_sface_2021dec.onnx"

_DOWNLOADS = {
    DETECTOR_FILE: f"{ZOO_URL}/face_detection_yunet/face_detection_yunet_2023mar.onnx",
    RECOGNIZER_FILE: f"{ZOO_URL}/face_recognition_sface/face_recognition_sface_2021dec.onnx",
}

def ensure_models():
    """Download any missing model file and return (detector_path, recognizer_path)."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    for path, url in _DOWNLOADS.items():
        if not path.exists():
            print(f"Downloading {path.name}")
            tmp = path.with_suffix(".part")
            urllib.request.urlretrieve(url, tmp)
            tmp.rename(path)
    return DETECTOR_FILE, RECOGNIZER_FILE