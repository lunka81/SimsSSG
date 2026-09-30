"""Settings for the face recognition client (runs on a Raspberry Pi)."""

from pathlib import Path

BASE_DIR = Path(__file__).parent
# Downloaded ONNX models
MODELS_DIR = BASE_DIR / "models"
