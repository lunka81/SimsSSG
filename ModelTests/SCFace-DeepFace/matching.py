"""Compares probe embeddings against gallery embeddings."""

import numpy as np


def cosine_similarity_matrix(probe_embeddings, gallery_embeddings):
    """Embeddings are already normalized, so cosine similarity is just a dot product.

    Returns a matrix with one row per probe and one column per gallery image.
    """
    return np.array(probe_embeddings) @ np.array(gallery_embeddings).T


def rank1_accuracy(similarities, probe_ids, gallery_ids):
    """Fraction of probes whose most similar gallery image is the correct person."""
    best_match_index = np.argmax(similarities, axis=1)
    predicted_ids = [gallery_ids[i] for i in best_match_index]
    correct = [pred == true for pred, true in zip(predicted_ids, probe_ids)]
    return float(np.mean(correct))
