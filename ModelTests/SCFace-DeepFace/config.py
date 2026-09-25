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
# Run SFace on the GPU (e.g. a Jetson). Requires OpenCV built with CUDA support
USE_CUDA = False

# Probe images to test: distance 1 = 4.2 m, 2 = 2.6 m, 3 = 1.0 m
DISTANCES = [1, 2, 3]
# Cameras 1-5 are visible light; add 6 and 7 to include the IR cameras
CAMERAS = [1, 2, 3, 4, 5]

# Where the results table is saved
RESULTS_FILE = Path(__file__).parent / "results.csv"
