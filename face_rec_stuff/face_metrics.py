from dataclasses import dataclass

import numpy as np


# Kalibrering för den kamera och bildstorlek du testade.
# Justera eller flytta till konfiguration om en annan kamera används.
DISTANCE_CALIBRATION = (
    40 * 0.389
    + 60 * 0.280
    + 80 * 0.212
) / 3


@dataclass
class FaceMetrics:
    image_width: int
    image_height: int
    face_width: int
    face_height: int
    face_width_ratio: float
    face_height_ratio: float
    estimated_distance_cm: float


def estimate_distance_cm(face_width_ratio: float) -> float:
    """Uppskattar kameraavstånd utifrån ansiktets andel av bildbredden."""
    if face_width_ratio <= 0:
        raise ValueError("Ansiktets andel måste vara större än noll")

    return DISTANCE_CALIBRATION / face_width_ratio


def calculate_face_metrics(
    result: list[dict],
    image: np.ndarray,
) -> FaceMetrics:
    """Beräknar bildstorlek, ansiktsstorlek och uppskattat avstånd."""
    face = result[0]["facial_area"]
    image_height, image_width = image.shape[:2]

    face_width_ratio = face["w"] / image_width
    face_height_ratio = face["h"] / image_height

    return FaceMetrics(
        image_width=image_width,
        image_height=image_height,
        face_width=face["w"],
        face_height=face["h"],
        face_width_ratio=face_width_ratio,
        face_height_ratio=face_height_ratio,
        estimated_distance_cm=estimate_distance_cm(face_width_ratio),
    )


def print_face_metrics(metrics: FaceMetrics) -> None:
    """Skriver måtten i backendens terminal för dina tester."""
    print(
        f"Bild: {metrics.image_width}x{metrics.image_height} px | "
        f"Ansikte: {metrics.face_width}x{metrics.face_height} px | "
        f"Andel av bredd: {metrics.face_width_ratio:.1%} | "
        f"Andel av höjd: {metrics.face_height_ratio:.1%} | "
        f"Uppskattat avstånd: {metrics.estimated_distance_cm:.0f} cm"
    )