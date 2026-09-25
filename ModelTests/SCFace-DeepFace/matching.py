"""Compares probe embeddings against gallery embeddings."""

import numpy as np
from deepface.modules.verification import find_confidence, find_threshold


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


def to_confidence(similarities, model_name):
    """Convert cosine similarities to DeepFace's confidence score (0-100).

    Uses DeepFace's own calibration, so confidence >= 51 means DeepFace.verify
    would say "same person" with its default threshold.
    """
    threshold = find_threshold(model_name, "cosine")
    confidences = []
    for similarity in similarities:
        distance = 1 - similarity
        confidences.append(find_confidence(distance, model_name, distance <= threshold, "cosine"))
    return np.array(confidences)


def access_confusion_matrix(confidences, predicted_ids, probe_ids, cleared_ids, threshold):
    """Count access decisions for one confidence threshold.

    A probe is granted access if its best match among the enrolled (cleared) people
    reaches the threshold. Positive = the person really has clearance.
    """
    granted = confidences >= threshold
    cleared = np.array([pid in cleared_ids for pid in probe_ids])
    wrong_person = np.array([pred != true for pred, true in zip(predicted_ids, probe_ids)])

    tp = int(np.sum(granted & cleared))
    fn = int(np.sum(~granted & cleared))
    fp = int(np.sum(granted & ~cleared))
    tn = int(np.sum(~granted & ~cleared))
    return {
        "threshold": threshold,
        "TP": tp, "FN": fn, "FP": fp, "TN": tn,
        # Cleared people let in, but matched to the wrong enrolled person
        "TP_wrong_identity": int(np.sum(granted & cleared & wrong_person)),
        # Share of uncleared people let in / cleared people turned away
        "FAR": fp / (fp + tn),
        "FRR": fn / (tp + fn),
        "accuracy": (tp + tn) / len(probe_ids),
    }
