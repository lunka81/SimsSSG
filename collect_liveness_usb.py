import cv2
import csv
import time
import numpy as np
import onnxruntime as ort
from insightface.app import FaceAnalysis

CONDITION = "face_mask_pic"
SUBJECT = "fredrik"
IS_ATTACK = True
CAMERA_LABEL = "usb_camera"
CAMERA_INDEX = 0
MANUAL_EXPOSURE = False
EXPOSURE_VALUE = -6
OUTPUT_FILE = "data/liveness_usb.csv"

SIZE = 80
LIVE_INDEX = 1

MODELS = [
    ("v2",   "models/2.7_80x80_MiniFASNetV2.onnx",      2.7),
    ("v1se", "models/4_0_0_80x80_MiniFASNetV1SE.onnx",  4.0),
]

app = FaceAnalysis(name="buffalo_l", allowed_modules=["detection"])
app.prepare(ctx_id=-1, det_size=(640, 640))

sessions = []
for tag, path, scale in MODELS:
    sess = ort.InferenceSession(path, providers=["CPUExecutionProvider"])
    sessions.append((tag, sess, sess.get_inputs()[0].name, scale))
    print("Loaded", tag, "at scale", scale)


def softmax(x):
    e = np.exp(x - np.max(x))
    return e / e.sum()


def stamp():
    return time.strftime("%Y-%m-%d %H:%M:%S") + f".{int((time.time() % 1) * 1000):03d}"


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


def analyse(frame, bbox):
    per_model = []
    total = np.zeros(3)

    for tag, sess, name, want_scale in sessions:
        crop, used = crop_face(frame, bbox, want_scale)
        blob = crop.astype(np.float32).transpose(2, 0, 1)[np.newaxis]
        scores = softmax(sess.run(None, {name: blob})[0][0])
        total += scores
        per_model.append((tag, scores, used, want_scale))

    return per_model, total / len(sessions)


file = open(OUTPUT_FILE, "a", newline="")
writer = csv.writer(file)

if file.tell() == 0:
    writer.writerow([
        "timestamp", "subject", "condition", "is_attack", "camera",
        "det_score", "face_width_px",
        "v2_live", "v2_is_live", "v2_scale",
        "v1se_live", "v1se_is_live", "v1se_scale",
        "ens_live", "ens_is_live",
        "ms"
    ])

cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Could not open camera index", CAMERA_INDEX)
    exit()

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

if MANUAL_EXPOSURE:
    ok1 = cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
    ok2 = cap.set(cv2.CAP_PROP_EXPOSURE, EXPOSURE_VALUE)
    print("Manual exposure requested. auto_exposure accepted:", ok1,
          " exposure accepted:", ok2)
    print("Reported exposure now:", cap.get(cv2.CAP_PROP_EXPOSURE))
else:
    print("Auto exposure, camera default")

ok, probe = cap.read()
if ok:
    print("Frame size:", probe.shape)
print("FPS reported:", cap.get(cv2.CAP_PROP_FPS))

print()
print("r = start or stop recording")
print("q = quit")
print("Condition:", CONDITION, " attack:", IS_ATTACK, " camera:", CAMERA_LABEL)

recording = False
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
        per_model, ens = analyse(frame, face.bbox.astype(int))

        row = {tag: (s, used, want) for tag, s, used, want in per_model}

        ens_live = ens[LIVE_INDEX]
        ens_is_live = np.argmax(ens) == LIVE_INDEX

        colour = (0, 255, 0) if ens_is_live else (0, 0, 255)
        cv2.rectangle(frame, (x1, y1), (x2, y2), colour, 2)

        cv2.putText(frame, f"ens {ens_live:.2f}", (x1, y1 - 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, colour, 2)
        cv2.putText(frame, f"v2  {row['v2'][0][LIVE_INDEX]:.2f}", (x1, y1 - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 200, 0), 2)
        cv2.putText(frame, f"v1se {row['v1se'][0][LIVE_INDEX]:.2f}", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)

        if recording:
            writer.writerow([
                stamp(), SUBJECT, CONDITION, IS_ATTACK, CAMERA_LABEL,
                f"{face.det_score:.4f}", x2 - x1,
                f"{row['v2'][0][LIVE_INDEX]:.4f}",
                1 if np.argmax(row['v2'][0]) == LIVE_INDEX else 0,
                f"{row['v2'][1]:.2f}",
                f"{row['v1se'][0][LIVE_INDEX]:.4f}",
                1 if np.argmax(row['v1se'][0]) == LIVE_INDEX else 0,
                f"{row['v1se'][1]:.2f}",
                f"{ens_live:.4f}",
                1 if ens_is_live else 0,
                f"{elapsed:.1f}"
            ])
            rows_written += 1

    if recording:
        status = f"RECORDING {CONDITION}  rows: {rows_written}"
        status_colour = (0, 0, 255)
    else:
        status = "press r to record"
        status_colour = (0, 255, 255)

    cv2.putText(frame, status, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_colour, 2)
    cv2.putText(frame, CAMERA_LABEL, (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)

    cv2.imshow("Collect liveness", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

    if key == ord("r"):
        recording = not recording
        print("Recording" if recording else "Stopped")

cap.release()
cv2.destroyAllWindows()
file.close()
print("Wrote", rows_written, "rows to", OUTPUT_FILE)