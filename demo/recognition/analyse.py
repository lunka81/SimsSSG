import sys
import csv
import statistics as st
from collections import defaultdict

PATH = sys.argv[1] if len(sys.argv) > 1 else "data/liveness.csv"

rows = list(csv.DictReader(open(PATH)))
print("Total rows:", len(rows))
print()


def correct_count(rows, tag):
    n = 0
    for r in rows:
        said_live = r[tag + "_is_live"] == "1"
        is_attack = r["is_attack"] == "True"
        if is_attack and not said_live:
            n += 1
        elif not is_attack and said_live:
            n += 1
    return n


def summarise(title, rows):
    if not rows:
        return

    attack = rows[0]["is_attack"] == "True"
    kind = "ATTACK" if attack else "REAL"

    print(f"{title}  [{kind}]  n={len(rows)}")

    for tag in ["v2", "v1se", "ens"]:
        vals = [float(r[tag + "_live"]) for r in rows]
        ok = correct_count(rows, tag)
        label = "blocked" if attack else "accepted"
        print(f"   {tag:5s} live mean {st.mean(vals):.4f}  "
              f"min {min(vals):.4f}  max {max(vals):.4f}   "
              f"{label} {ok}/{len(rows)} ({100*ok/len(rows):.1f}%)")

    w = [int(r["face_width_px"]) for r in rows if r["face_width_px"]]
    s = [float(r["v1se_scale"]) for r in rows if r["v1se_scale"]]
    if w:
        print(f"   face width {min(w)} to {max(w)}, mean {st.mean(w):.0f}"
              f"   v1se crop mean {st.mean(s):.2f} of 4.00")
    print()


groups = defaultdict(list)
for r in rows:
    groups[r["condition"]].append(r)

print("=" * 70)
print("BY CONDITION")
print("=" * 70)
print()

for cond in sorted(groups):
    summarise(cond, groups[cond])

print("=" * 70)
print("BY CONDITION AND SUBJECT")
print("=" * 70)
print()

pairs = defaultdict(list)
for r in rows:
    pairs[(r["condition"], r["subject"])].append(r)

for cond, subject in sorted(pairs):
    summarise(f"{cond} / {subject}", pairs[(cond, subject)])

print("=" * 70)
print("THRESHOLD SWEEP, ALL DATA, V2")
print("=" * 70)
print()

real = [r for r in rows if r["is_attack"] == "False"]
att = [r for r in rows if r["is_attack"] == "True"]

if real and att:
    for t in [0.05, 0.10, 0.20, 0.30, 0.50, 0.70, 0.90]:
        admitted = sum(1 for r in att if float(r["v2_live"]) >= t)
        refused = sum(1 for r in real if float(r["v2_live"]) < t)
        print(f"  t={t:.2f}   attacks admitted {admitted:4d}/{len(att)} "
              f"({100*admitted/len(att):5.1f}%)   "
              f"real refused {refused:4d}/{len(real)} "
              f"({100*refused/len(real):5.1f}%)")
else:
    print("  Need both real and attack rows in the file for this")
print()