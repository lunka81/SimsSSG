"""Draws the access-control confusion matrices."""

import math

import matplotlib

matplotlib.use("Agg")  # Save to file, no window needed
import matplotlib.pyplot as plt
import numpy as np


def plot_confusion_matrices(matrices, title, output_file):
    """Draw one 2x2 confusion matrix per confidence threshold in a grid and save it."""
    columns = min(5, len(matrices))
    rows = math.ceil(len(matrices) / columns)
    fig, axes = plt.subplots(rows, columns, figsize=(3.4 * columns, 3.4 * rows), squeeze=False)

    for ax, m in zip(axes.flat, matrices):
        # Rows: actual clearance. Columns: access decision
        counts = np.array([[m["TP"], m["FN"]], [m["FP"], m["TN"]]])
        labels = np.array([["TP", "FN"], ["FP", "TN"]])
        ax.imshow(counts, cmap="Blues", vmin=0, vmax=counts.sum() / 2)

        for i in range(2):
            for j in range(2):
                color = "white" if counts[i, j] > counts.sum() / 4 else "black"
                ax.text(j, i, f"{labels[i, j]}\n{counts[i, j]}", ha="center", va="center",
                        color=color, fontsize=11)

        ax.set_title(f"Confidence ≥ {m['threshold']}\n"
                     f"FP-rate {m['FAR']:.1%} · FN-rate {m['FRR']:.1%}", fontsize=10)
        ax.set_xticks([0, 1], ["Granted", "Denied"])
        ax.set_yticks([0, 1], ["Cleared", "Not cleared"])
        ax.set_xlabel("Access decision")
        ax.set_ylabel("Actual")

    # Hide unused grid cells
    for ax in list(axes.flat)[len(matrices):]:
        ax.axis("off")

    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(output_file, dpi=150)
    plt.close(fig)
