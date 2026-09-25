"""Settings for the SFace evaluation on SCface."""

from pathlib import Path

# Folder that contains the SCface dataset
DATASET_DIR = Path(__file__).parent / "SCface_database"

# DeepFace settings
MODEL_NAME = "SFace"
DETECTOR_BACKEND = "retinaface"
# If no face is found (common for the small distance-1 images),
# use the whole image instead of raising an error
ENFORCE_DETECTION = False
# Run RetinaFace (TensorFlow) and SFace (onnxruntime-gpu) on the GPU.
# Raises an error at startup if the GPU cannot be used
USE_CUDA = True

# Probe images to test: distance 1 = 4.2 m, 2 = 2.6 m, 3 = 1.0 m
# Only distance 3 is used, it best matches the intended use case
DISTANCES = [3]
# Cameras 1-5 are visible light; add 6 and 7 to include the IR cameras
CAMERAS = [1, 2, 3, 4, 5]

# Security clearance test: half of the subjects are enrolled (have clearance),
# the other half are not. The seed makes the same people get picked every run
CLEARANCE_SEED = 0
# DeepFace confidence thresholds (0-100) for granting access.
# 50 is the same decision as DeepFace.verify with its default threshold
CONFIDENCE_THRESHOLDS = list(range(50, 70, 5))

# Where the results are saved
RESULTS_FILE = Path(__file__).parent / "results.csv"
CONFUSION_FILE = Path(__file__).parent / "confusion_matrices.csv"
CONFUSION_PLOT = Path(__file__).parent / "confusion_matrices.png"
