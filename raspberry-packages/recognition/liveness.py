import cv2
import numpy as np
import onnxruntime as ort

from config.config import LIVENESS_THRESHOLD
from recognition.model_files import LIVENESS_V1SE_FILE, LIVENESS_V2_FILE

# Input size both MiniFASNet models expect, 80 by 80 pixels.
SIZE = 80

# The models output three classes. Index 1 is the real face class, the other
# two are different kinds of attack. Note that the model card for these models
# gives the order as live, print, replay, which is wrong. Verified against the
# sample images shipped with the original repository, where the correct answer
# is known in advance.
LIVE_INDEX = 1

# The two models and the crop scale each one was trained with. V2 sees a
# region 2.7 times the face box, V1SE sees 4.0 times, so the two look at
# different amounts of the area around the face.
MODELS = [
    ("v2", LIVENESS_V2_FILE, 2.7),
    ("v1se", LIVENESS_V1SE_FILE, 4.0),
]


class LivenessChecker:
    def __init__(self, model_paths=None, threshold=LIVENESS_THRESHOLD):
        self.threshold = threshold
        self.sessions = []

        # Load each model once at start-up rather than per frame, since
        # creating an ONNX session is slow. CPU only, there is no GPU on the Pi.
        for tag, path, scale in (model_paths or MODELS):
            sess = ort.InferenceSession(
                str(path), providers=["CPUExecutionProvider"]
            )
            # Keep the input name alongside the session so run() can be called
            # without looking it up again on every frame.
            self.sessions.append((tag, sess, sess.get_inputs()[0].name, scale))

    def _softmax(self, x):
        # Turns the three raw output values into probabilities that sum to one.
        # Subtracting the maximum first prevents overflow when the values are
        # large. The result is mathematically identical either way.
        e = np.exp(x - np.max(x))
        return e / e.sum()

    def _crop(self, frame, bbox, scale):
        """Cuts the enlarged region around the face and resizes it to 80x80.

        Returns the crop and the scale actually achieved, which can be smaller
        than the one requested if the face is large or close to the edge.
        """
        h, w = frame.shape[:2]
        x1, y1, x2, y2 = bbox
        box_w = x2 - x1
        box_h = y2 - y1

        # A degenerate box, for example from a bad detection. Give up on this
        # model rather than producing a meaningless score.
        if box_w <= 0 or box_h <= 0:
            return None, 0.0

        # Cap the scale so the enlarged region is never bigger than the frame.
        # This limits the size of the box only, not where it sits, so a box
        # near an edge can still cross the border. That is handled below.
        scale = min((h - 1) / box_h, (w - 1) / box_w, scale)

        # Enlarge the box around the centre of the face.
        new_w = box_w * scale
        new_h = box_h * scale
        cx = x1 + box_w / 2
        cy = y1 + box_h / 2

        left = cx - new_w / 2
        top = cy - new_h / 2
        right = cx + new_w / 2
        bottom = cy + new_h / 2

        # If the enlarged box crosses an edge of the frame, slide the whole box
        # back inside and keep its size. The face ends up off centre, which is
        # what the original Silent-Face implementation does. The alternative,
        # padding with black, would add artificial edges that the model could
        # read as evidence of a photograph.
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
        """Returns the live score, the verdict, and each model's own score.

        bbox is (x1, y1, x2, y2). YuNet gives (x, y, w, h), so the caller
        converts it before calling this.
        """
        scores = {}   # each model's own live score, for logging
        scales = {}   # the crop scale each model actually got, for logging
        total = np.zeros(3)   # running sum of the three-class vectors
        used = 0              # how many models produced a usable crop

        for tag, sess, name, want in self.sessions:
            crop, got = self._crop(frame, bbox, want)

            # This model could not get a crop. Skip it and let the other one
            # carry the decision.
            if crop is None:
                continue

            # Convert to float32 and move the colour channels in front of the
            # image dimensions, giving the 1x3x80x80 shape the model expects.
            # The values stay in the range 0 to 255 and stay in BGR order,
            # because that is what the models were trained on. Dividing by 255
            # or converting to RGB here would quietly make the scores worse.
            blob = crop.astype(np.float32).transpose(2, 0, 1)[np.newaxis]
            out = self._softmax(sess.run(None, {name: blob})[0][0])

            scores[tag] = float(out[LIVE_INDEX])
            scales[tag] = round(got, 2)
            total += out
            used += 1

        # Neither model could run. Treat the face as not live, so a check that
        # cannot be performed refuses rather than lets someone through. For
        # something controlling a lock, failing closed is the safe default.
        if used == 0:
            return {"live": 0.0, "is_live": False, "scores": {}, "scales": {}}

        # Average the probability vectors of the models that ran. Dividing by
        # used rather than by 2 keeps the average correct when only one model
        # managed to produce a crop.
        ens = total / used
        live = float(ens[LIVE_INDEX])

        return {
            "live": live,
            "is_live": live >= self.threshold,
            "scores": scores,
            "scales": scales,
        }
