import cv2
import numpy as np
import onnxruntime as ort
from insightface.app import FaceAnalysis

SIZE = 80
LIVE_INDEX = 1

MODELS = [
    ("models/2.7_80x80_MiniFASNetV2.onnx", 2.7),
    ("models/4_0_0_80x80_MiniFASNetV1SE.onnx", 4.0),
]

app = FaceAnalysis(name="buffalo_l", allowed_modules=["detection"])
app.prepare(ctx_id=-1, det_size=(640, 640))

sessions = []
for path, scale in MODELS:
    sess = ort.InferenceSession(path, providers=["CPUExecutionProvider"])
    sessions.append((sess, sess.get_inputs()[0].name, scale))
    print("Loaded", path, "at scale", scale)


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


def check_liveness(frame, bbox):
    total = np.zeros(3)
    scales_used = []

    for sess, name, scale in sessions:
        crop, used = crop_face(frame, bbox, scale)
        blob = crop.astype(np.float32).transpose(2, 0, 1)[np.newaxis]
        scores = softmax(sess.run(None, {name: blob})[0][0])
        total += scores
        scales_used.append(used)

    return total / len(sessions), scales_used


cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Could not open the camera")
    exit()

while True:
    ok, frame = cap.read()

    if not ok:
        break

    faces = app.get(frame)

    for face in faces:
        bbox = face.bbox.astype(int)
        scores, scales_used = check_liveness(frame, bbox)

        live = scores[LIVE_INDEX]
        is_live = np.argmax(scores) == LIVE_INDEX

        colour = (0, 255, 0) if is_live else (0, 0, 255)
        text = f"{'LIVE' if is_live else 'SPOOF'} {live:.2f}"

        x1, y1, x2, y2 = bbox
        cv2.rectangle(frame, (x1, y1), (x2, y2), colour, 2)
        cv2.putText(frame, text, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, colour, 2)

        wanted = [s for _, _, s in sessions]
        if any(u < wa for u, wa in zip(scales_used, wanted)):
            cv2.putText(frame, "Too close, step back", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    cv2.imshow("Liveness ensemble", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()