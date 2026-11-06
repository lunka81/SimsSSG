"""Download the ONNX models used by the pipeline (same sources as SimsSSG)."""
import urllib.request

from config import DETECTOR_FILE, LIVENESS_V1SE_FILE, LIVENESS_V2_FILE, MODELS_DIR, RECOGNIZER_FILE

ZOO_URL = "https://github.com/opencv/opencv_zoo/raw/main/models"
# MiniFASNet anti-spoofing models, converted to ONNX from Silent-Face-Anti-Spoofing
LIVENESS_URL = "https://github.com/QingHeYang/Silent-Face-Anti-Spoofing-onnx/raw/main/onnx"

DOWNLOADS = {
    DETECTOR_FILE: f"{ZOO_URL}/face_detection_yunet/face_detection_yunet_2023mar.onnx",
    RECOGNIZER_FILE: f"{ZOO_URL}/face_recognition_sface/face_recognition_sface_2021dec.onnx",
    LIVENESS_V2_FILE: f"{LIVENESS_URL}/{LIVENESS_V2_FILE.name}",
    LIVENESS_V1SE_FILE: f"{LIVENESS_URL}/{LIVENESS_V1SE_FILE.name}",
}


def ensure_models():
    """Download any missing model file. A model that is not in DOWNLOADS must be placed in MODELS_DIR by hand."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    for path, url in DOWNLOADS.items():
        if not path.exists():
            print(f"Downloading {path.name}")
            tmp = path.with_suffix(".part")
            urllib.request.urlretrieve(url, tmp)
            tmp.rename(path)
