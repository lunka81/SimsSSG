import cv2
import time
from insightface.app import FaceAnalysis

app = FaceAnalysis(name="buffalo_l", allowed_modules=["detection"])
app.prepare(ctx_id=-1, det_size=(640, 640))

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Could not open the camera")
    exit()

while True:
    ok, frame = cap.read()

    if not ok:
        print("Could not read a frame")
        break

    start = time.time()
    faces = app.get(frame)
    elapsed = (time.time() - start) * 1000

    for face in faces:
        x1, y1, x2, y2 = face.bbox.astype(int)

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        score = face.det_score
        cv2.putText(
            frame,
            f"{score:.2f}",
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )

    cv2.putText(
        frame,
        f"Faces: {len(faces)}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.putText(
        frame,
        f"{elapsed:.0f} ms",
        (10, 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 255),
        2
    )

    cv2.imshow("InsightFace detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()