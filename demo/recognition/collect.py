import cv2
import csv
import time
import numpy as np
from insightface.app import FaceAnalysis

CONDITION = "photo_phone_bright"
SUBJECT = "ali"
IS_ATTACK = True
OUTPUT_FILE = "data/results.csv"

app = FaceAnalysis(name="buffalo_l", allowed_modules=["detection", "recognition"])
app.prepare(ctx_id=-1, det_size=(640, 640))


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


reference = None
recording = False

file = open(OUTPUT_FILE, "a", newline="")
writer = csv.writer(file)

if file.tell() == 0:
    writer.writerow([
        "timestamp", "subject", "condition", "is_attack",
        "det_score", "similarity", "face_width_px", "ms"
    ])

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Could not open the camera")
    exit()

print("s = save reference")
print("r = start or stop recording")
print("q = quit")
print("Condition:", CONDITION)

rows_written = 0

while True:
    ok, frame = cap.read()

    if not ok:
        break

    start = time.time()
    faces = app.get(frame)
    elapsed = (time.time() - start) * 1000

    for face in faces:
        x1, y1, x2, y2 = face.bbox.astype(int)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        if reference is not None:
            score = cosine_similarity(face.embedding, reference)

            cv2.putText(frame, f"{score:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            if recording:
                writer.writerow([
                    time.strftime("%Y-%m-%d %H:%M:%S") + f".{int((time.time() % 1) * 1000):03d}",
                    SUBJECT,
                    CONDITION,
                    IS_ATTACK,
                    f"{face.det_score:.4f}",
                    f"{score:.4f}",
                    x2 - x1,
                    f"{elapsed:.1f}"
                ])
                rows_written += 1

    if recording:
        colour = (0, 0, 255)
        status = f"RECORDING {CONDITION}  rows: {rows_written}"
    else:
        colour = (0, 255, 255)
        status = "press r to record"

    cv2.putText(frame, status, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, colour, 2)

    cv2.imshow("Collect", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

    if key == ord("s") and len(faces) > 0:
        reference = faces[0].embedding
        print("Reference saved")

    if key == ord("r"):
        recording = not recording
        print("Recording" if recording else "Stopped")

cap.release()
cv2.destroyAllWindows()
file.close()
print("Wrote", rows_written, "rows to", OUTPUT_FILE)