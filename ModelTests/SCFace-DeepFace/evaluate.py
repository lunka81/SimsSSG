"""Evaluates DeepFace SFace on SCface.

Gallery: the frontal mugshots. Probes: surveillance images per distance and camera.

1. Rank-1 identification against all mugshots.
2. Security clearance test: only half of the people are enrolled. Every probe is
   granted or denied access based on DeepFace's confidence, giving one confusion
   matrix per confidence threshold (all cameras combined).
"""

import csv

import numpy as np
from tqdm import tqdm

from config import (DISTANCES, CAMERAS, RESULTS_FILE, MODEL_NAME, CLEARANCE_SEED,
                    CONFIDENCE_THRESHOLDS, CONFUSION_FILE, CONFUSION_PLOT)
from dataset import load_gallery, load_probes
from embedding import get_embedding
from matching import (cosine_similarity_matrix, rank1_accuracy, to_confidence,
                      access_confusion_matrix)
from plots import plot_confusion_matrices


def embed_images(images, description):
    """Embed a list of (subject_id, path) pairs. Returns (ids, embeddings)."""
    ids = []
    embeddings = []
    for subject_id, path in tqdm(images, desc=description, leave=False):
        ids.append(subject_id)
        embeddings.append(get_embedding(path))
    return ids, embeddings


def save_csv(rows, output_file):
    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


# 1. Embed the gallery
gallery_ids, gallery_embeddings = embed_images(load_gallery(), "Gallery")
print(f"Gallery: {len(gallery_ids)} subjects\n")

# 2. Test every distance and camera (rank-1 against the full gallery)
results = []
all_probe_ids = []
all_probe_embeddings = []
for distance in DISTANCES:
    for camera in CAMERAS:
        probes = load_probes(distance, camera)
        probe_ids, probe_embeddings = embed_images(probes, f"Distance {distance}, cam {camera}")
        all_probe_ids += probe_ids
        all_probe_embeddings += probe_embeddings

        similarities = cosine_similarity_matrix(probe_embeddings, gallery_embeddings)
        accuracy = rank1_accuracy(similarities, probe_ids, gallery_ids)

        print(f"Distance {distance}, cam {camera}: rank-1 = {accuracy:.2%} ({len(probes)} probes)")
        results.append({"distance": distance, "camera": camera,
                        "num_probes": len(probes), "rank1_accuracy": accuracy})

# 3. Summaries
print()
for distance in DISTANCES:
    accuracies = [r["rank1_accuracy"] for r in results if r["distance"] == distance]
    print(f"Distance {distance} mean rank-1: {np.mean(accuracies):.2%}")
print(f"Overall mean rank-1: {np.mean([r['rank1_accuracy'] for r in results]):.2%}")

save_csv(results, RESULTS_FILE)
print(f"\nResults saved to {RESULTS_FILE}")

# 4. Security clearance test: enroll a random half of the people
rng = np.random.default_rng(CLEARANCE_SEED)
cleared_ids = set(rng.choice(sorted(gallery_ids), size=len(gallery_ids) // 2, replace=False))
enrolled = [i for i, gid in enumerate(gallery_ids) if gid in cleared_ids]
enrolled_ids = [gallery_ids[i] for i in enrolled]
enrolled_embeddings = [gallery_embeddings[i] for i in enrolled]

# Each probe is compared with every enrolled person, the best match decides access
similarities = cosine_similarity_matrix(all_probe_embeddings, enrolled_embeddings)
best_match = np.argmax(similarities, axis=1)
predicted_ids = [enrolled_ids[i] for i in best_match]
confidences = to_confidence(similarities.max(axis=1), MODEL_NAME)

num_cleared_probes = sum(pid in cleared_ids for pid in all_probe_ids)
print(f"\nClearance test: {len(cleared_ids)} of {len(gallery_ids)} people enrolled, "
      f"{len(all_probe_ids)} probes ({num_cleared_probes} cleared, "
      f"{len(all_probe_ids) - num_cleared_probes} not cleared)")

matrices = [access_confusion_matrix(confidences, predicted_ids, all_probe_ids, cleared_ids, t)
            for t in CONFIDENCE_THRESHOLDS]
for m in matrices:
    print(f"Confidence >= {m['threshold']}: TP {m['TP']:3d}  FN {m['FN']:3d}  "
          f"FP {m['FP']:3d}  TN {m['TN']:3d}  FAR {m['FAR']:6.2%}  FRR {m['FRR']:6.2%}  "
          f"(wrong identity among TP: {m['TP_wrong_identity']})")

save_csv(matrices, CONFUSION_FILE)
distances = ", ".join(str(d) for d in DISTANCES)
cameras = ", ".join(str(c) for c in CAMERAS)
plot_confusion_matrices(
    matrices,
    f"Deepface using {MODEL_NAME} model, 130 identities, 65 with clearance, 65 without.\n"
    #f"{len(cleared_ids)}/{len(gallery_ids)} people enrolled, {len(all_probe_ids)} probes",
    f"{len(all_probe_ids)} total images, weighted equally in terms of identities.",
    CONFUSION_PLOT,
)
print(f"\nConfusion matrices saved to {CONFUSION_FILE} and {CONFUSION_PLOT}")
