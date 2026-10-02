import os
import json
import shutil
from collections import Counter

ROOT = "P:/celeba-test/CelebA_Spoof/CelebA_Spoof"
LABELS = os.path.join(ROOT, "metas/intra_test/test_label.json")
OUT = "illumination_samples"

with open(LABELS) as f:
    data = json.load(f)

print("Total entries:", len(data))

illum = Counter()
env = Counter()
spoof_type = Counter()
live_spoof = Counter()

for path, values in data.items():
    spoof_type[values[40]] += 1
    illum[values[41]] += 1
    env[values[42]] += 1
    live_spoof[values[43]] += 1

print()
print("Illumination values:", dict(sorted(illum.items())))
print("Environment values:", dict(sorted(env.items())))
print("Live/spoof values:", dict(sorted(live_spoof.items())))
print("Spoof type values:", dict(sorted(spoof_type.items())))

os.makedirs(OUT, exist_ok=True)

saved = Counter()
for path, values in data.items():
    value = values[41]
    if saved[value] >= 4:
        continue

    src = os.path.join(ROOT, path)
    if not os.path.exists(src):
        continue

    name = f"illum{value}_{saved[value]}.png"
    shutil.copy(src, os.path.join(OUT, name))
    saved[value] += 1

print()
print("Saved samples to", OUT)
print("Open them and see which lighting each number means")