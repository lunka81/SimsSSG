import os

ROOT = "data/celeba-spoof"

for dirpath, dirnames, filenames in os.walk(ROOT):
    depth = dirpath[len(ROOT):].count(os.sep)
    if depth <= 2:
        print("  " * depth, os.path.basename(dirpath) or ROOT,
              f"[{len(dirnames)} folders, {len(filenames)} files]")
        for f in filenames[:5]:
            print("  " * (depth + 1), f)