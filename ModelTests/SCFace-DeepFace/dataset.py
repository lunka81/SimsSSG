"""Finds the gallery and probe images in the SCface dataset."""

from config import DATASET_DIR


def subject_id_from_filename(path):
    """Filenames start with the subject number, e.g. '001_cam1_1.jpg' -> '001'."""
    return path.name[:3]


def load_gallery():
    """Return (subject_id, path) for every frontal mugshot."""
    folder = DATASET_DIR / "mugshot_frontal_cropped_all"
    paths = sorted(folder.glob("*.*"))
    return [(subject_id_from_filename(p), p) for p in paths]


def load_probes(distance, camera):
    """Return (subject_id, path) for every surveillance image at one distance and camera."""
    folder = DATASET_DIR / f"surveillance_cameras_distance_{distance}" / f"cam_{camera}"
    paths = sorted(folder.glob("*.*"))
    return [(subject_id_from_filename(p), p) for p in paths]
