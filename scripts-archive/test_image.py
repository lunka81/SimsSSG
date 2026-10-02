import sys
import cv2
import numpy as np
import onnxruntime as ort
from insightface.app import FaceAnalysis

SCALE = 2.7
SIZE = 80
LIVE_INDEX = 1

app = FaceAnalysis(name="buffalo_l", allowed_modules=["detection"])
app.prepare(ctx_id=-1, det_size=(640, 640))

session = ort.InferenceSession(
    "models/minifasnet_v2.onnx",
    providers=["CPUExecutionProvider"]
)
input_name = session.get_inputs()[0].name


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


def check_liveness(crop):
    blob = crop.astype(np.float32)
    blob = blob.transpose(2, 0, 1)[np.newaxis]
    return softmax(session.run(None, {input_name: blob})[0][0])


image_path = sys.argv[1]
img = cv2.imread(image_path)

if img is None:
    print("Could not read", image_path)
    exit()

faces = app.get(img)
print(image_path, " faces found:", len(faces))

for face in faces:
    crop, used_scale = crop_face(img, face.bbox.astype(int), SCALE)
    scores = check_liveness(crop)

    live = scores[LIVE_INDEX]
    verdict = "LIVE" if np.argmax(scores) == LIVE_INDEX else "SPOOF"

    print(f"  live {live:.3f}  spoof {1 - live:.3f}  -> {verdict}")

    if used_scale < SCALE:
        print(f"  note: margin reduced to {used_scale:.2f}, face fills too much of the image")