# Smart Access, liveness and anti-spoofing

Part of a student project with SSG Standard Solutions Group. The aim is to
replace access cards at industrial site gates with face recognition.

This repository covers the anti-spoofing side: checking that the camera is
looking at a real person rather than a photograph, and measuring how well it
performs under different conditions.

## Requirement

Access to an industrial site is currently granted on an access card. A card only
proves that someone is holding a card, so it can be lent to a person without
valid safety training.

Replacing the card with the face solves that, but only if the system can tell a
real face from a picture of one. Face recognition cannot do this on its own: in
our testing a photograph of an enrolled person scored 0.92 against 0.98 for the
real face, which is close enough that no threshold separates them.

So the system needs two checks, not one:

- Is this a real person in front of the camera?
- If so, who is it?

This repository implements the first, and includes the recognition work used to
demonstrate why it is needed.

## How the system works

Three stages, each answering one question.

**1. Find the face.** InsightFace, specifically the SCRFD detector from the
buffalo_l pack. Returns a bounding box and a confidence score. Runs on the
colour frame directly.

**2. Check it is real.** MiniFASNetV2, from the Silent Face Anti Spoofing
project, running through ONNX Runtime.

The face box is expanded to 2.7 times its size around the same centre before
being passed to the model. This matters: the model was trained on that crop
ratio, and much of the evidence it uses is in the surroundings rather than the
face itself, such as the edge of a phone, the border of a printed photo, or
reflections on glass. If the face is too close to the camera for the full margin
to fit, the crop is reduced and accuracy drops.

The crop is resized to 80 by 80, kept as raw 0 to 255 values, rearranged to
channels-first, and run through the model. The output is three numbers; position
1 is the live score.

**3. Identify the person.** InsightFace again, converting the face into a
512-value embedding and comparing it against the enrolled references using
cosine similarity. Returns an identity and a similarity score.

All processing happens on the device. No images are stored or transmitted, which
is what GDPR requires for biometric data.

## Model choice

MiniFASNetV2 alone. The upstream project and DeepFace both recommend running V2
and V1SE together and averaging the results, but measured on our own data that
performs worse. V1SE missed 96% of one attack type where V2 missed 10%, and
averaging the two inherits the weakness.

The build log records the comparison in full.

## Performance

Measured on a USB webcam. Earlier results recorded through a phone streamed over
Phone Link are not comparable, because the compression removes the fine texture
the model depends on.

Real faces accepted:

| Lighting | Result |
|---|---|
| Bright | 100% |
| Backlit | 100% |
| Dark | 100% |

Attacks blocked:

| Attack | Result |
|---|---|
| Phone screen | 100% at normal distance |
| Laptop screen | 100% |
| Access card | 100% |
| Printed photo, border intact | 100% |
| Printed photo, cut out to the face, dark | 100% |
| Printed photo, cut out to the face, bright | 24% |

## Known limitations

**Cut-out printed photographs.** A photograph trimmed to the edge of the face
and held at normal distance defeats the system roughly 90% of the time in good
lighting. The live score for these attacks is above 0.95, the same range as a
real face, so no threshold setting prevents it. This matches the published
figure of 89% for the same attack type on the CelebA-Spoof benchmark.

**Capture quality.** Performance depends heavily on the camera. A compressed
video stream reduced backlit acceptance from 100% to 66% and reduced blocking of
cut-out attacks from 100% to 26%. Any deployment should use a camera with
minimal compression.

**Close range.** The model requires a crop 2.7 times the face box. If a person
stands close enough that the face fills the frame, the crop is reduced and
results become unreliable. Camera placement should ensure space around the head
at the standing position.

**Autofocus.** With an autofocus camera, the phone screen attack produced 56%
blocking in one run and 99% in a repeat under identical conditions. A fixed
focus camera is likely to be more predictable.

**Not tested.** Silicone or moulded masks, deepfake video, and large enrolled
populations. Tailgating, meaning a second person entering behind a valid entry,
cannot be addressed in software without a turnstile.

## Installation

Python 3.12. Newer versions are avoided deliberately, because the libraries ship
prebuilt packages for specific Python versions and the newest release usually
has none.

```
python -m venv venv
source venv/Scripts/activate      # Windows, Git Bash
pip install -r requirements.txt
```

Models are not included in the repository.

MiniFASNet weights go in `models/`:

- `2.7_80x80_MiniFASNetV2.onnx`
- `4_0_0_80x80_MiniFASNetV1SE.onnx`

available from the Silent Face Anti Spoofing project.

InsightFace downloads the buffalo_l pack automatically on first run, about
300 MB, into your user directory.

## Usage

Identify which camera to use:

```
python find_camera.py
```

Run the live view, which shows the live score for both models on screen:

```
python liveness_ensemble.py
```

Record a test. Set the condition, subject, attack flag and camera label at the
top of the file first:

```
python collect_liveness_usb.py
```

Press `r` to start and stop recording, `q` to quit. Each run should last about
ten seconds, giving 30 to 60 frames.

Analyse the results:

```
python analyse.py data/liveness_usb.csv
```

This prints results per condition and per subject for all three models, plus a
threshold sweep showing how many attacks would be admitted and how many real
people refused at each possible cut-off.

## Files

| File | Purpose |
|---|---|
| `collect_liveness_usb.py` | Records liveness results to CSV, one row per frame |
| `liveness_ensemble.py` | Live view with both models running |
| `liveness_test.py` | Single model version |
| `recognise.py` | Face recognition against a saved reference |
| `analyse.py` | Produces results tables and the threshold sweep |
| `find_camera.py` | Lists available cameras and their resolutions |
| `camera.py` | Minimal camera capture, used for checking the feed |
| `detect_faces.py` | Haar cascade detection, kept for comparison |
| `scripts-archive/` | One-off scripts used to inspect models and datasets |
| `BUILD-LOG.md` | Development record, with the reasoning behind each decision |
| `TEST-PLAN.md` | Remaining tests |

## Licences

The licence on a project's code does not necessarily apply to its trained
models. Both need checking separately.

**MiniFASNet**, used for anti-spoofing: Apache 2.0, including commercial use.

**InsightFace**, used for detection and recognition: MIT code, but the
pretrained models are released for non-commercial research purposes only. This
is acceptable for a research project. A commercial deployment would require
licensing the weights from InsightFace or substituting a permissively licensed
model such as OpenCV's SFace, with some loss of accuracy.

**CelebA-Spoof**, used for benchmark testing: research use only.

## Status

Liveness detection and recognition both work and are measured. They have not yet
been combined into a single pipeline, pending agreement on the interface with
the recognition component.

Outstanding: remaining attack types on the USB camera, additional test subjects,
the Axis camera supplied by SSG, and performance measurement on the Jetson Orin
Nano rather than a laptop.
