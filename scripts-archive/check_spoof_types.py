import os
import json
import shutil
from collections import Counter

ROOT = "P:/celeba-test/CelebA_Spoof/CelebA_Spoof"
LABELS = ROOT + "/metas/intra_test/test_label.json"
OUT = "spoof_type_samples"

with open(LABELS) as f:
    data = json.load(f)

os.makedirs(OUT, exist_ok=True)

saved = Counter()
for rel, values in data.items():
    t = values[40]
    if t == 0 or saved[t] >= 4:
        continue
    src = os.path.join(ROOT, rel)
    if not os.path.exists(src):
        continue
    shutil.copy(src, os.path.join(OUT, f"type{t:02d}_{saved[t]}.png"))
    saved[t] += 1

print("Saved samples for types:", sorted(saved))