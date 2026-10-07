"""Download the ONNX models used by the pipeline."""

import urllib.request

from config import MODELS_DIR

ZOO_URL = "https://github.com/opencv/opencv_zoo/raw/main/models"
# MiniFASNet anti-spoofing models, converted to ONNX from Silent-Face-Anti-Spoofing
LIVENESS_URL = "https://github.com/QingHeYang/Silent-Face-Anti-Spoofing-onnx/raw/main/onnx"

DETECTOR_FILE = MODELS_DIR / "face_detection_yunet_2023mar.onnx"
RECOGNIZER_FILE = MODELS_DIR / "face_recognition_sface_2021dec.onnx"
LIVENESS_V2_FILE = MODELS_DIR / "2.7_80x80_MiniFASNetV2.onnx"
LIVENESS_V1SE_FILE = MODELS_DIR / "4_0_0_80x80_MiniFASNetV1SE.onnx"

_DOWNLOADS = {
    DETECTOR_FILE: f"{ZOO_URL}/face_detection_yunet/face_detection_yunet_2023mar.onnx",
    RECOGNIZER_FILE: f"{ZOO_URL}/face_recognition_sface/face_recognition_sface_2021dec.onnx",
    LIVENESS_V2_FILE: f"{LIVENESS_URL}/{LIVENESS_V2_FILE.name}",
    LIVENESS_V1SE_FILE: f"{LIVENESS_URL}/{LIVENESS_V1SE_FILE.name}",
}


def ensure_models():
    """Download any missing model file and return (detector_path, recognizer_path).

    The liveness models are downloaded too; LivenessChecker finds them on its own.
    """
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    for path, url in _DOWNLOADS.items():
        if not path.exists():
            print(f"Downloading {path.name}")
            tmp = path.with_suffix(".part")
            urllib.request.urlretrieve(url, tmp)
            tmp.rename(path)
    return DETECTOR_FILE, RECOGNIZER_FILE
