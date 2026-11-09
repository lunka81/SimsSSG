# Model evaluation

Offline tool that measures how well the face recognition pipeline works. It uses the same models
and settings as the [edge device](../edge-device/) and [backend](../backend/): YuNet face detection,
MiniFASNet liveness, SFace embeddings and nearest-neighbour matching with cosine similarity ≥ 0.363.
The recognition results in the project report were produced with this tool. All settings are in
[config.py](config.py).

It consists of two parts:

1. **Pipeline** ([pipeline/](pipeline/)) runs every image through the models and writes `results/results.csv`.
2. **Presentation** ([presentation/](presentation/)) reads that CSV and writes plots and tables to `report/`.

## Input data (not included)

The images aren't part of the repository, because they show real people (the test subject and the
Color FERET dataset, which has its own license). To run the evaluation, add them like this:

```
model-evaluation/
├── ReferenceImages/        # the gallery: one front-facing *.JPG per enrolled person
│   ├── 001_frontal.JPG     # the test subject (SELF_REFERENCE in config.py)
│   └── ...                 # everyone else; filename = identity
└── dataset/
    ├── metadata.csv        # one row per test image
    └── ...                 # the test images, in any folder structure
```

`metadata.csv` needs the columns `distance, angle, headwear, glasses, lighting, case_folder, image, path`,
where `path` is relative to `dataset/`. The condition columns are free text and are used to group
the plots. Every test image should show the person in `SELF_REFERENCE`.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

The model files are downloaded to `model_weights/` on the first run.

## Running

From this folder:

```bash
source .venv/bin/activate
python -m pipeline        # writes results/results.csv
python -m presentation    # writes report/
```

## GPU

SFace and the liveness models run in `onnxruntime-gpu` on CUDA. The pipeline prints which device is
used. Set `USE_GPU = False` in `config.py` to run on the CPU. Without an NVIDIA GPU you can
replace `onnxruntime-gpu[cuda,cudnn]` with `onnxruntime` in `requirements.txt`. The device only
affects running time, not the results.

## Another recognition model

Change `RECOGNIZER_FILE`, `EMBEDDING_DIM` and `INPUT_SIZE` in `config.py` and put the model in
`model_weights/`. The pipeline stops with an error if the model's output length is not `EMBEDDING_DIM`.
`MATCH_THRESHOLD` is model-specific and probably needs changing as well.

## The two tests

Every image is embedded once, then compared against two reference galleries:

| test | gallery | question |
|---|---|---|
| `included` | all references | Am I recognised as myself? |
| `excluded` | all references but without the test subject | Am I mistaken for someone else when I am unknown? |

## results.csv

One row per image and test.

| column | meaning |
|---|---|
| `test` | `included` or `excluded` |
| `distance`, `angle`, `headwear`, `glasses`, `lighting`, `case_folder`, `image`, `path` | from `metadata.csv` |
| `face_detected` | a usable face was found (and embedded) |
| `det_score`, `face_w`, `face_h` | YuNet score and face size in pixels |
| `liveness_score`, `is_live` | MiniFASNet live score and whether it passes the threshold |
| `best_match`, `best_similarity` | nearest reference and its cosine similarity |
| `self_similarity` | similarity to `001_frontal` (`included` only) |
| `approved` | `best_similarity` ≥ threshold |
| `outcome` | see below |

`outcome`:

- `no_face`: no usable face was found
- `correct_accept`: nearest reference is me and it is approved (`included`)
- `false_reject`: best similarity is below the threshold (`included`)
- `false_accept`: approved as someone else (both tests)
- `true_reject`: best similarity is below the threshold (`excluded`)

Liveness is recorded but does not change the outcome. On the Pi, a face that fails liveness is
never sent to the backend, so `is_live = False` means the Pi would not even try.

## report/

- `summary.csv`: outcome counts and rates per test
- `outcomes_by_factor_included.png`, `outcomes_by_factor_excluded.png`: outcomes per condition
- `similarity_distribution.png`: similarity to me vs. best similarity to someone else
- `threshold_sweep.png`: false reject and false accept rates for every threshold
- `similarity_vs_face_size_included.png`, `similarity_vs_face_size_excluded.png`: similarity against
  detected face width, colored by distance (similarity to me when enrolled, best similarity to someone else when unknown)
- `acceptance_distance_lighting.png`, `acceptance_angle_headwear.png`: share of images correctly
  accepted per condition pair, enrolled test (no face counts as not accepted)
- `detection_liveness_by_factor.png`: face detection and liveness pass rates per condition
- `false_accepts.csv`: every image approved as someone else
