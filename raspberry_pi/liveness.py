import cv2
import numpy as np
import onnxruntime as ort

SIZE = 80
LIVE_INDEX = 1

MODELS = [
    ("v2", "models/2.7_80x80_MiniFASNetV2.onnx", 2.7),
    ("v1se", "models/4_0_0_80x80_MiniFASNetV1SE.onnx", 4.0),
]


class LivenessChecker:
    def __init__(self, model_paths=None, threshold=0.5):
        self.threshold = threshold
        self.sessions = []

        for tag, path, scale in (model_paths or MODELS):
            sess = ort.InferenceSession(
                path, providers=["CPUExecutionProvider"]
            )
            self.sessions.append((tag, sess, sess.get_inputs()[0].name, scale))

    def _softmax(self, x):
        e = np.exp(x - np.max(x))
        return e / e.sum()

    def _crop(self, frame, bbox, scale):
        h, w = frame.shape[:2]
        x1, y1, x2, y2 = bbox
        box_w = x2 - x1
        box_h = y2 - y1

        if box_w <= 0 or box_h <= 0:
            return None, 0.0

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

        if crop.size == 0:
            return None, 0.0

        return cv2.resize(crop, (SIZE, SIZE)), scale

    def check(self, frame, bbox):
        """Returns the live score, the verdict, and each model's own score."""
        scores = {}
        scales = {}
        total = np.zeros(3)
        used = 0

        for tag, sess, name, want in self.sessions:
            crop, got = self._crop(frame, bbox, want)

            if crop is None:
                continue

            blob = crop.astype(np.float32).transpose(2, 0, 1)[np.newaxis]
            out = self._softmax(sess.run(None, {name: blob})[0][0])

            scores[tag] = float(out[LIVE_INDEX])
            scales[tag] = round(got, 2)
            total += out
            used += 1

        if used == 0:
            return {"live": 0.0, "is_live": False, "scores": {}, "scales": {}}

        ens = total / used
        live = float(ens[LIVE_INDEX])

        return {
            "live": live,
            "is_live": live >= self.threshold,
            "scores": scores,
            "scales": scales,
        }