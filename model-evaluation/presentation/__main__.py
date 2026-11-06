"""Read results/results.csv and write plots and summary tables to report/.

Run from the FaceEval folder: python -m presentation
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

from config import MATCH_THRESHOLD, REPORT_DIR, RESULTS_CSV, SELF_REFERENCE

FACTORS = ["distance", "angle", "headwear", "glasses", "lighting"]
TESTS = {"included": "Person enrolled", "excluded": "Person unknown"}

# Outcome colors: good / warning / critical status colors, gray for no face
OUTCOME_COLORS = {
    "correct_accept": "#0ca30c",
    "true_reject": "#0ca30c",
    "false_reject": "#fab219",
    "false_accept": "#d03b3b",
    "no_face": "#9b9a96",
}
SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]
SURFACE = "#fcfcfb"
TEXT = "#0b0b0b"
TEXT_MUTED = "#52514e"
BLUES = LinearSegmentedColormap.from_list("blues", ["#cde2fb", "#6da7ec", "#256abf", "#0d366b"])

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "text.color": TEXT, "axes.labelcolor": TEXT_MUTED, "xtick.color": TEXT_MUTED, "ytick.color": TEXT_MUTED,
    "axes.edgecolor": "#d6d5d0", "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": "#ebeae6", "axes.axisbelow": True, "font.size": 10,
})


def label(value):
    """Short tick label: 'head-beanie' -> 'beanie'."""
    return value.split("-", 1)[-1]


def save(fig, name):
    fig.tight_layout()
    fig.savefig(REPORT_DIR / name, dpi=150)
    plt.close(fig)
    print("Wrote", REPORT_DIR / name)


def summary(df):
    """Outcome counts and rates per test."""
    counts = df.groupby(["test", "outcome"]).size().rename("count").reset_index()
    counts["rate"] = (counts["count"] / counts.groupby("test")["count"].transform("sum")).round(4)
    counts.to_csv(REPORT_DIR / "summary.csv", index=False)
    print(counts.to_string(index=False), "\n")


def outcomes_by_factor(df, test):
    """Stacked bars: share of each outcome for every value of every factor."""
    data = df[df["test"] == test]
    outcomes = [o for o in OUTCOME_COLORS if o in set(data["outcome"])]
    fig, axes = plt.subplots(1, len(FACTORS), figsize=(15, 4), sharey=True)
    for ax, factor in zip(axes, FACTORS):
        rates = pd.crosstab(data[factor], data["outcome"], normalize="index").reindex(columns=outcomes, fill_value=0)
        bottom = np.zeros(len(rates))
        for outcome in outcomes:
            ax.bar([label(v) for v in rates.index], rates[outcome], bottom=bottom, width=0.6,
                   color=OUTCOME_COLORS[outcome], edgecolor=SURFACE, linewidth=2, label=outcome.replace("_", " "))
            bottom += rates[outcome].to_numpy()
        ax.set_title(factor, color=TEXT)
        ax.grid(axis="x", visible=False)
    axes[0].set_ylabel("Share of images")
    axes[0].yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=len(outcomes), frameon=False, bbox_to_anchor=(0.5, 1.0))
    fig.suptitle(f"Outcome per condition: {TESTS[test].lower()}", y=1.07, color=TEXT)
    save(fig, f"outcomes_by_factor_{test}.png")


def similarity_distribution(df):
    """Similarity to my own reference vs. the best match among the other people."""
    genuine = df.loc[df["test"] == "included", "self_similarity"].dropna()
    impostor = df.loc[df["test"] == "excluded", "best_similarity"].dropna()
    bins = np.linspace(min(genuine.min(), impostor.min()), max(genuine.max(), impostor.max()), 40)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(genuine, bins=bins, color=SERIES[0], alpha=0.8, edgecolor=SURFACE, label="Similarity to my reference")
    ax.hist(impostor, bins=bins, color=SERIES[1], alpha=0.8, edgecolor=SURFACE,
            label="Best similarity to another person")
    ax.axvline(MATCH_THRESHOLD, color=TEXT, linestyle="--", linewidth=1.5)
    ax.annotate(f"threshold {MATCH_THRESHOLD}", (MATCH_THRESHOLD, ax.get_ylim()[1] * 0.95),
                xytext=(5, 0), textcoords="offset points", color=TEXT)
    ax.set_xlabel("Cosine similarity")
    ax.set_ylabel("Images")
    ax.legend(frameon=False, loc="upper left")
    ax.set_title("Similarity distributions", color=TEXT)
    save(fig, "similarity_distribution.png")


def threshold_sweep(df):
    """False reject rate (enrolled) and false accept rate (unknown) for every threshold.

    Only images with a detected face are counted; no_face images are shown in the other plots."""
    included = df[(df["test"] == "included") & df["face_detected"]]
    excluded = df[(df["test"] == "excluded") & df["face_detected"]]
    self_is_best = included["best_match"] == Path(SELF_REFERENCE).stem
    thresholds = np.linspace(0, 1, 201)
    frr = [1 - ((included["best_similarity"] >= t) & self_is_best).mean() for t in thresholds]
    far = [(excluded["best_similarity"] >= t).mean() for t in thresholds]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(thresholds, frr, color=SERIES[0], linewidth=2, label="False reject rate (enrolled)")
    ax.plot(thresholds, far, color=SERIES[1], linewidth=2, label="False accept rate (unknown)")
    ax.axvline(MATCH_THRESHOLD, color=TEXT, linestyle="--", linewidth=1.5)
    ax.annotate(f"threshold {MATCH_THRESHOLD}", (MATCH_THRESHOLD, 0.9), xytext=(5, 0),
                textcoords="offset points", color=TEXT)
    ax.set_xlabel("Similarity threshold")
    ax.set_ylabel("Rate")
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.legend(frameon=False, loc="center right")
    ax.set_title("Error rates for different thresholds", color=TEXT)
    save(fig, "threshold_sweep.png")


def acceptance_heatmap(df, rows, columns):
    """Share of images correctly accepted (enrolled test) for each combination of two factors.

    Images without a detected face count as not accepted."""
    data = df[df["test"] == "included"].assign(accepted=lambda d: d["outcome"] == "correct_accept")
    table = data.pivot_table(index=rows, columns=columns, values="accepted", aggfunc="mean")
    fig, ax = plt.subplots(figsize=(1.6 * len(table.columns) + 2, 0.8 * len(table) + 1.5))
    image = ax.imshow(table.to_numpy(), cmap=BLUES, vmin=0, vmax=1, aspect="auto")
    for (i, j), value in np.ndenumerate(table.to_numpy()):
        ax.text(j, i, f"{value:.0%}", ha="center", va="center", color="white" if value > 0.55 else TEXT)
    ax.set_xticks(range(len(table.columns)), [label(c) for c in table.columns])
    ax.set_yticks(range(len(table.index)), [label(r) for r in table.index])
    ax.set_xlabel(columns)
    ax.set_ylabel(rows)
    ax.grid(False)
    fig.colorbar(image, ax=ax, label="Acceptance rate",
                 format=matplotlib.ticker.PercentFormatter(1.0))
    ax.set_title("Acceptance rate, person enrolled", color=TEXT)
    save(fig, f"acceptance_{rows}_{columns}.png")


def similarity_vs_face_size(df, test):
    """Similarity against detected face width, colored by distance.

    Enrolled: similarity to my own reference. Unknown: best similarity to another person."""
    data = df[(df["test"] == test) & df["face_detected"]]
    column = "self_similarity" if test == "included" else "best_similarity"
    fig, ax = plt.subplots(figsize=(10, 4.5))
    for color, (distance, group) in zip(SERIES, data.groupby("distance")):
        ax.scatter(group["face_w"], group[column], s=22, color=color, edgecolor=SURFACE, linewidth=0.8,
                   label=f"{distance.lstrip('d').rstrip('m')} m")
    ax.axhline(MATCH_THRESHOLD, color=TEXT, linestyle="--", linewidth=1.5)
    ax.annotate(f"threshold {MATCH_THRESHOLD}", (1, MATCH_THRESHOLD), xycoords=("axes fraction", "data"),
                xytext=(0, 4), textcoords="offset points", ha="right", color=TEXT)
    ax.set_xlabel("Detected face width in the image (pixels)")
    ax.set_ylabel("Similarity to own reference" if test == "included" else "Best similarity to another person")
    ax.legend(title="Distance", frameon=False, loc="upper left", bbox_to_anchor=(1.01, 1))
    ax.set_title(f"Similarity vs face size: {TESTS[test].lower()}", color=TEXT, loc="left", fontweight="bold")
    save(fig, f"similarity_vs_face_size_{test}.png")


def detection_and_liveness(df):
    """Share of images where a face was found, and where that face passed the liveness check."""
    data = df[df["test"] == "included"]
    fig, axes = plt.subplots(1, len(FACTORS), figsize=(15, 4), sharey=True)
    for ax, factor in zip(axes, FACTORS):
        grouped = data.groupby(factor)
        detected = grouped["face_detected"].mean()
        # Images without a face count as not passing
        live = grouped["is_live"].apply(lambda s: s.fillna(False).astype(bool).mean())
        x = np.arange(len(detected))
        ax.bar(x - 0.18, detected, width=0.34, color=SERIES[0], label="Face detected")
        ax.bar(x + 0.18, live, width=0.34, color=SERIES[1], label="Passed liveness")
        ax.set_xticks(x, [label(v) for v in detected.index])
        ax.set_title(factor, color=TEXT)
        ax.grid(axis="x", visible=False)
    axes[0].set_ylabel("Share of images")
    axes[0].yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 1.0))
    fig.suptitle("Detection and liveness per condition", y=1.07, color=TEXT)
    save(fig, "detection_liveness_by_factor.png")


def false_accepts(df):
    """Every image approved as someone else, in either test."""
    rows = df[df["outcome"] == "false_accept"]
    rows = rows[["test", *FACTORS, "path", "best_match", "best_similarity", "is_live"]]
    rows.to_csv(REPORT_DIR / "false_accepts.csv", index=False)
    print(f"{len(rows)} false accepts written to {REPORT_DIR / 'false_accepts.csv'}")


def main():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(RESULTS_CSV)
    summary(df)
    for test in TESTS:
        outcomes_by_factor(df, test)
    similarity_distribution(df)
    threshold_sweep(df)
    for test in TESTS:
        similarity_vs_face_size(df, test)
    acceptance_heatmap(df, "distance", "lighting")
    acceptance_heatmap(df, "angle", "headwear")
    detection_and_liveness(df)
    false_accepts(df)


if __name__ == "__main__":
    main()
