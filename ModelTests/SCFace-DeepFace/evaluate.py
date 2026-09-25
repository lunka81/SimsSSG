"""Evaluates DeepFace SFace on SCface (rank-1 identification).

Gallery: the frontal mugshots. Probes: surveillance images per distance and camera.
"""

import csv

import numpy as np
from tqdm import tqdm

from config import DISTANCES, CAMERAS, RESULTS_FILE
from dataset import load_gallery, load_probes
from embedding import get_embedding
from matching import cosine_similarity_matrix, rank1_accuracy


def embed_images(images, description):
    """Embed a list of (subject_id, path) pairs. Returns (ids, embeddings)."""
    ids = []
    embeddings = []
    for subject_id, path in tqdm(images, desc=description, leave=False):
        ids.append(subject_id)
        embeddings.append(get_embedding(path))
    return ids, embeddings


# 1. Embed the gallery
gallery_ids, gallery_embeddings = embed_images(load_gallery(), "Gallery")
print(f"Gallery: {len(gallery_ids)} subjects\n")

# 2. Test every distance and camera
results = []
for distance in DISTANCES:
    for camera in CAMERAS:
        probes = load_probes(distance, camera)
        probe_ids, probe_embeddings = embed_images(probes, f"Distance {distance}, cam {camera}")

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

# 4. Save results
with open(RESULTS_FILE, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)
print(f"\nResults saved to {RESULTS_FILE}")
