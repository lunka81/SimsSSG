import cv2
import numpy as np
from insightface.app import FaceAnalysis

app = FaceAnalysis(name="buffalo_l", allowed_modules=["detection", "recognition"])
app.prepare(ctx_id=-1, det_size=(320, 320))


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


reference = None
reference_name = "Person"

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Could not open the camera")
    exit()

print("Press s to save the current face as the reference")
print("Press q to quit")

while True:
    ok, frame = cap.read()

    if not ok:
        print("Could not read a frame")
        break

    faces = app.get(frame)

    for face in faces:
        x1, y1, x2, y2 = face.bbox.astype(int)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        if reference is not None:
            score = cosine_similarity(face.embedding, reference)
            label = f"{reference_name}: {score:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    status = "reference saved" if reference is not None else "press s to save"
    cv2.putText(frame, status, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    cv2.imshow("Recognition", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

    if key == ord("s") and len(faces) > 0:
        reference = faces[0].embedding
        print("Saved reference face. Embedding size:", reference.shape)

cap.release()
cv2.destroyAllWindows()