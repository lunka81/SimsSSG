import os
import csv
import json
import time
import random
import cv2
import numpy as np
import onnxruntime as ort
from insightface.app import FaceAnalysis

ROOT = "P:/celeba-test/CelebA_Spoof/CelebA_Spoof"
LABELS = ROOT + "/metas/intra_test/test_label.json"
OUTPUT = "data/dataset_results.csv"

SAMPLE_PER_CLASS = 1000

SIZE = 80
LIVE_INDEX = 1

MODELS = [
    ("v2",   "models/2.7_80x80_MiniFASNetV2.onnx",      2.7),
    ("v1se", "models/4_0_0_80x80_MiniFASNetV1SE.onnx",  4.0),
]

app = FaceAnalysis(name="buffalo_l", allowed_modules=["detection"])
app.prepare(ctx_id=-1, det_size=(640, 640))

sessions = []
for tag, path, scale in MODELS:
    sess = ort.InferenceSession(path, providers=["CPUExecutionProvider"])
    sessions.append((tag, sess, sess.get_inputs()[0].name, scale))


def softmax(x):
    e = np.exp(x - np.max(x))
    return e / e.sum()


def crop_face(frame, bbox, scale):
    h, w = frame.shape[:2]
    x1, y1, x2, y2 = bbox
    box_w = x2 - x1
    box_h = y2 - y1

    scale = min((h - 1) / box_h, (w - 1) / box_w, scale)

    new_w = box_w * scale
    new_h = box_h * scale
    cx = x1 + box_w / 2
    cy = y1 + box_h / 2

    left = cx - new_w / 2
    top = cy - new_h / 2
    right = cx + new_w / 2
    bottom = cy + new_h / 2

    if left < 0:
        right -= left
        left = 0
    if top < 0:
        bottom -= top
        top = 0
    if right > w - 1:
        left -= right - (w - 1)
        right = w - 1
    if bottom > h - 1:
        top -= bottom - (h - 1)
        bottom = h - 1

    crop = frame[int(top):int(bottom) + 1, int(left):int(right) + 1]
    return cv2.resize(crop, (SIZE, SIZE)), scale


def analyse(frame, bbox):
    results = {}
    total = np.zeros(3)

    for tag, sess, name, want in sessions:
        crop, used = crop_face(frame, bbox, want)
        blob = crop.astype(np.float32).transpose(2, 0, 1)[np.newaxis]
        scores = softmax(sess.run(None, {name: blob})[0][0])
        total += scores
        results[tag] = (scores, used)

    return results, total / len(sessions)


with open(LABELS) as f:
    data = json.load(f)

items = []
for rel_path, values in data.items():
    items.append({
        "path": os.path.join(ROOT, rel_path),
        "rel": rel_path,
        "spoof_type": values[40],
        "illumination": values[41],
        "environment": values[42],
        "is_spoof": values[43],
    })

live = [i for i in items if i["is_spoof"] == 0]
spoof = [i for i in items if i["is_spoof"] == 1]

print("Total live:", len(live), " total spoof:", len(spoof))

random.seed(42)
random.shuffle(live)
random.shuffle(spoof)

sample = live[:SAMPLE_PER_CLASS] + spoof[:SAMPLE_PER_CLASS]
random.shuffle(sample)

print("Testing", len(sample), "images")

file = open(OUTPUT, "w", newline="")
writer = csv.writer(file)
writer.writerow([
    "path", "is_spoof", "spoof_type", "illumination", "environment",
    "status", "det_score", "face_width_px",
    "v2_live", "v1se_live", "ens_live", "v1se_scale"
])

counts = {t: {"TP": 0, "TN": 0, "FP": 0, "FN": 0} for t in ["v2", "v1se", "ens"]}
no_face = 0
start_all = time.time()

for n, item in enumerate(sample):
    img = cv2.imread(item["path"])

    if img is None:
        continue

    faces = app.get(img)

    if len(faces) == 0:
        writer.writerow([
            item["rel"], item["is_spoof"], item["spoof_type"],
            item["illumination"], item["environment"],
            "no_face", "", "", "", "", "", ""
        ])
        no_face += 1
        continue

    face = max(faces, key=lambda f: f.bbox[2] - f.bbox[0])
    bbox = face.bbox.astype(int)
    results, ens = analyse(img, bbox)

    scores = {
        "v2": results["v2"][0],
        "v1se": results["v1se"][0],
        "ens": ens,
    }

    decisions = {t: int(np.argmax(s)) == LIVE_INDEX for t, s in scores.items()}
    actually_live = item["is_spoof"] == 0

    for tag in ["v2", "v1se", "ens"]:
        predicted_live = decisions[tag]

        if actually_live and predicted_live:
            counts[tag]["TP"] += 1
        elif not actually_live and not predicted_live:
            counts[tag]["TN"] += 1
        elif not actually_live and predicted_live:
            counts[tag]["FP"] += 1
        else:
            counts[tag]["FN"] += 1

    writer.writerow([
        item["rel"], item["is_spoof"], item["spoof_type"],
        item["illumination"], item["environment"],
        "ok",
        f"{face.det_score:.4f}",
        bbox[2] - bbox[0],
        f"{scores['v2'][LIVE_INDEX]:.4f}",
        f"{scores['v1se'][LIVE_INDEX]:.4f}",
        f"{scores['ens'][LIVE_INDEX]:.4f}",
        f"{results['v1se'][1]:.2f}"
    ])

    if (n + 1) % 100 == 0:
        elapsed = time.time() - start_all
        rate = (n + 1) / elapsed
        left = (len(sample) - n - 1) / rate / 60
        print(f"{n+1}/{len(sample)}  {rate:.1f} img/s  about {left:.0f} min left  no face: {no_face}")

file.close()

print()
print("No face found in", no_face, "images")
print()

for tag in ["v2", "v1se", "ens"]:
    c = counts[tag]
    total = c["TP"] + c["TN"] + c["FP"] + c["FN"]
    if total == 0:
        continue
    print(tag)
    print(f"  TP {c['TP']:5d}  real accepted")
    print(f"  TN {c['TN']:5d}  attack rejected")
    print(f"  FP {c['FP']:5d}  attack ACCEPTED, security failure")
    print(f"  FN {c['FN']:5d}  real rejected, usability failure")
    print(f"  accuracy {(c['TP'] + c['TN']) / total * 100:.2f}%")
    if c["TP"] + c["FN"] > 0:
        print(f"  real people accepted {c['TP'] / (c['TP'] + c['FN']) * 100:.2f}%")
    if c["TN"] + c["FP"] > 0:
        print(f"  attacks blocked      {c['TN'] / (c['TN'] + c['FP']) * 100:.2f}%")
    print()