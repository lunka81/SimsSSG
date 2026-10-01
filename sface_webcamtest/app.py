"""Webcam face recognition using DeepFace.

Drop reference photos into known_faces/<person name>/*.jpg before running.
Recognized faces get a bounding box with the person's name and confidence.
"""

import os
import sys
import time

if sys.platform == "win32":
    # DeepFace logs emoji characters on import; Windows consoles default to
    # a codepage that can't encode them, which crashes the import otherwise.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import cv2
from deepface import DeepFace

DB_PATH = "known_faces"
# Options: VGG-Face, Facenet, Facenet512, OpenFace, DeepFace, DeepID, Dlib,
# ArcFace, SFace, GhostFaceNet.
MODEL_NAME = "SFace"
DETECTOR_BACKEND = "mtcnn"
DISTANCE_METRIC = "cosine"
PROCESS_EVERY_N_FRAMES = 1
BOX_COLOR = (0, 200, 0)


def recognize_faces(frame):
    """Return a list of (x, y, w, h, name, confidence) for recognized faces."""
    try:
        matches = DeepFace.find(
            img_path=frame,
            db_path=DB_PATH,
            model_name=MODEL_NAME,
            detector_backend=DETECTOR_BACKEND,
            distance_metric=DISTANCE_METRIC,
            enforce_detection=False,
            silent=True,
        )
    except ValueError:
        return []

    results = []
    for df in matches:
        if df.empty:
            continue
        best = df.iloc[0]
        x, y, w, h = (int(best[c]) for c in ("source_x", "source_y", "source_w", "source_h"))
        name = os.path.basename(os.path.dirname(best["identity"]))
        results.append((x, y, w, h, name, float(best["confidence"])))
    return results


def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam.")

    frame_count = 0
    results = []
    #idx = 0
    print("Press 'q' to quit.")
    while True:
        ok, frame = cap.read()
        #idx += 1
        #if idx == 5:
        #    break
        #frame = cv2.imread(f"./static_faces/{idx}.jpg")
        if not ok:
            break

        frame_count += 1
        if frame_count % PROCESS_EVERY_N_FRAMES == 0:
            start_time = time.time()
            results = recognize_faces(frame)
            print("%s seconds" % (time.time() - start_time))

        for x, y, w, h, name, confidence in results:
            cv2.rectangle(frame, (x, y), (x + w, y + h), BOX_COLOR, 2)
            label = f"{name} ({confidence:.0f}%)"
            cv2.putText(
                frame, label, (x, max(y - 10, 0)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, BOX_COLOR, 2,
            )

        cv2.imshow("DeepFace Recognition", frame)
        #cv2.imwrite(f"./static_faces/identifications/{idx}.jpg", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        #time.sleep(1)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
