"""Run every dataset image through the SimsSSG models and write results/results.csv.

Two tests use the same image embeddings, only the reference gallery differs:
  included: all reference images, the person in the dataset is known
  excluded: all reference images except SELF_REFERENCE, the person is unknown (any approval is a false accept)

Run from the FaceEval folder: python -m pipeline
"""
import csv

import cv2
import numpy as np
from tqdm import tqdm

from config import (
    DATASET_DIR, DETECTOR_FILE, MATCH_THRESHOLD, METADATA_CSV, RECOGNIZER_FILE, REFERENCE_DIR,
    RESULTS_CSV, SELF_REFERENCE,
)
from pipeline.model_files import ensure_models
from pipeline.models import FaceDetector, FaceEmbedder, LivenessChecker

METADATA_COLUMNS = ["distance", "angle", "headwear", "glasses", "lighting", "case_folder", "image", "path"]
RESULT_COLUMNS = ["test", *METADATA_COLUMNS, "face_detected", "det_score", "face_w", "face_h",
                  "liveness_score", "is_live", "best_match", "best_similarity", "self_similarity",
                  "approved", "outcome"]


def embed_references(detector, embedder):
    """Return (reference ids, matrix with one embedding per row)."""
    ids, embeddings = [], []
    for path in tqdm(sorted(REFERENCE_DIR.glob("*.JPG")), desc="References"):
        image = cv2.imread(str(path))
        face = detector.detect(image)
        embedding = None if face is None else embedder.embed(image, face)
        if embedding is None:
            print(f"No face found in reference {path.name}, skipped")
            continue
        ids.append(path.stem)
        embeddings.append(embedding)
    return ids, np.stack(embeddings)


def process_image(path, detector, embedder, liveness):
    """Return detection and liveness columns, and the embedding (None if no usable face)."""
    image = cv2.imread(str(path))
    face = detector.detect(image)
    embedding = None if face is None else embedder.embed(image, face)
    if embedding is None:
        return {"face_detected": False}, None

    live_score, is_live = liveness.check(image, face)
    columns = {
        "face_detected": True,
        "det_score": round(float(face[14]), 4),
        "face_w": round(float(face[2])),
        "face_h": round(float(face[3])),
        "liveness_score": round(live_score, 4),
        "is_live": is_live,
    }
    return columns, embedding


def match(similarities, ref_ids, self_id, self_known):
    """Nearest-neighbour decision as in SimsSSG, plus the outcome of this test."""
    best = int(np.argmax(similarities))
    best_id = ref_ids[best]
    best_similarity = float(similarities[best])
    approved = best_similarity >= MATCH_THRESHOLD

    if not approved:
        outcome = "false_reject" if self_known else "true_reject"
    elif best_id == self_id:
        outcome = "correct_accept"
    else:
        outcome = "false_accept"

    return {
        "best_match": best_id,
        "best_similarity": round(best_similarity, 4),
        "approved": approved,
        "outcome": outcome,
    }


def main():
    ensure_models()
    detector = FaceDetector(DETECTOR_FILE)
    embedder = FaceEmbedder(RECOGNIZER_FILE)
    liveness = LivenessChecker()
    print("Recognition runs on:", embedder.session.get_providers()[0])

    ref_ids, ref_embeddings = embed_references(detector, embedder)
    self_id = SELF_REFERENCE.rsplit(".", 1)[0]
    if self_id not in ref_ids:
        raise SystemExit(f"No face found in {SELF_REFERENCE}, cannot run the tests")
    self_index = ref_ids.index(self_id)
    # The excluded test uses every reference except SELF_REFERENCE
    others = [i for i in range(len(ref_ids)) if i != self_index]
    other_ids = [ref_ids[i] for i in others]

    with open(METADATA_CSV, newline="") as f:
        metadata = list(csv.DictReader(f))

    rows = []
    for meta in tqdm(metadata, desc="Dataset"):
        base = {column: meta[column] for column in METADATA_COLUMNS}
        columns, embedding = process_image(DATASET_DIR / meta["path"], detector, embedder, liveness)

        if embedding is None:
            for test in ("included", "excluded"):
                rows.append({"test": test, **base, **columns, "approved": False, "outcome": "no_face"})
            continue

        # Embeddings are unit length, so the dot product is the cosine similarity
        similarities = ref_embeddings @ embedding
        self_similarity = round(float(similarities[self_index]), 4)
        rows.append({"test": "included", **base, **columns, "self_similarity": self_similarity,
                     **match(similarities, ref_ids, self_id, self_known=True)})
        rows.append({"test": "excluded", **base, **columns,
                     **match(similarities[others], other_ids, self_id, self_known=False)})

    RESULTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=RESULT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nWrote {len(rows)} rows to {RESULTS_CSV}")
    for test in ("included", "excluded"):
        outcomes = [row["outcome"] for row in rows if row["test"] == test]
        counts = ", ".join(f"{name} {outcomes.count(name)}" for name in sorted(set(outcomes)))
        print(f"{test}: {counts}")


if __name__ == "__main__":
    main()
