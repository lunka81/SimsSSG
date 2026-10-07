import threading
import time
from datetime import datetime, timezone

from camera.camera import Camera
from clients.uploader import recognize
from config.config import (
    MODELS_DIR,
    RECOGNITION_COOLDOWN,
    SEND_INTERVAL,
    USE_HARDWARE_LOCK,
)
from models.models import ensure_models
from recognition.detector import FaceDetector
from recognition.extractor import FaceEmbedder
from recognition.liveness import LivenessChecker


class RecognitionService:
    def __init__(self):
        self._thread = None
        self._stop_event = threading.Event()

        # Skyddar data som läses både av kameratråden och routes.
        self._data_lock = threading.Lock()

        # Förhindrar samtidiga start-/stoppanrop.
        self._lifecycle_lock = threading.Lock()

        self._latest_frame = None
        self._last_sent = None
        self._last_decision = None

        self._status = {
            "running": False,
            "camera_open": False,
            "last_frame_at": None,
            "face_detected": False,
            "is_live": None,
            "liveness_score": None,
            "last_response": None,
            "last_error": None,
        }

    def start(self):
        """Starta kameraloopen om den inte redan körs."""
        with self._lifecycle_lock:
            if self._thread is not None and self._thread.is_alive():
                return

            self._stop_event.clear()
            self._last_sent = None
            self._last_decision = None

            with self._data_lock:
                self._latest_frame = None
                self._status.update(
                    running=True,
                    camera_open=False,
                    last_frame_at=None,
                    face_detected=False,
                    is_live=None,
                    liveness_score=None,
                    last_response=None,
                    last_error=None,
                )

            self._thread = threading.Thread(
                target=self._run,
                name="recognition-worker",
                daemon=True,
            )
            self._thread.start()

    def stop(self):
        """Begär stopp och vänta på att resurserna frigörs."""
        with self._lifecycle_lock:
            self._stop_event.set()

            if self._thread is not None:
                self._thread.join()
                self._thread = None

    def get_status(self):
        """Returnera en kopia av aktuell status."""
        with self._data_lock:
            return self._status.copy()

    def get_latest_frame(self):
        """Returnera en kopia av senaste bildrutan."""
        with self._data_lock:
            if self._latest_frame is None:
                return None

            return self._latest_frame.copy()

    def _update_status(self, **values):
        with self._data_lock:
            self._status.update(values)

    def _run(self):
        """Öppna resurser och kör kameraloopen."""
        camera = None
        lock = None

        try:
            # Importera GPIO-koden bara på riktig Raspberry.
            if USE_HARDWARE_LOCK:
                from hardware.lock import Lock
            else:
                from hardware.fake_lock import FakeLock as Lock

            detector_path, recognizer_path = ensure_models()

            detector = FaceDetector(detector_path)
            embedder = FaceEmbedder(recognizer_path)

            # Dessa filer måste redan finnas i MODELS_DIR.
            liveness = LivenessChecker(
                model_paths=[
                    (
                        "v2",
                        str(MODELS_DIR / "2.7_80x80_MiniFASNetV2.onnx"),
                        2.7,
                    ),
                    (
                        "v1se",
                        str(MODELS_DIR / "4_0_0_80x80_MiniFASNetV1SE.onnx"),
                        4.0,
                    ),
                ]
            )

            lock = Lock()

            if self._stop_event.is_set():
                return

            camera = Camera()
            self._update_status(camera_open=True)

            while not self._stop_event.is_set():
                frame = camera.read()
                lock.update()

                with self._data_lock:
                    self._latest_frame = frame.copy()
                    self._status["last_frame_at"] = (
                        datetime.now(timezone.utc).isoformat()
                    )

                # Stopp kan ha begärts medan kameran lästes.
                if self._stop_event.is_set():
                    break

                self._process_frame(
                    frame,
                    detector,
                    liveness,
                    embedder,
                    lock,
                )

        except Exception as error:
            self._update_status(
                last_error=f"{type(error).__name__}: {error}"
            )
            print("Recognition service failed:", error)

        finally:
            # Försök stänga båda även om en stängning misslyckas.
            for resource in (camera, lock):
                if resource is not None:
                    try:
                        resource.close()
                    except Exception as error:
                        self._update_status(
                            last_error=f"Cleanup failed: {error}"
                        )
                        print("Cleanup failed:", error)

            self._update_status(
                running=False,
                camera_open=False,
            )

    def _process_frame(
        self,
        frame,
        detector,
        liveness,
        embedder,
        lock,
    ):
        """Kontrollera ansiktet och be backend om tillträdesbeslut."""
        now = time.monotonic()

        # Kameran läses fortfarande under cooldown.
        if (
            self._last_decision is not None
            and now - self._last_decision < RECOGNITION_COOLDOWN
        ):
            return

        if (
            self._last_sent is not None
            and now - self._last_sent < SEND_INTERVAL
        ):
            return

        face = detector.detect(frame)

        self._update_status(
            face_detected=face is not None,
            is_live=None,
            liveness_score=None,
        )

        if face is None:
            return

        # YuNet: x, y, width, height.
        # LivenessChecker: x1, y1, x2, y2.
        x, y, width, height = [float(value) for value in face[:4]]
        bbox = (x, y, x + width, y + height)

        live_result = liveness.check(frame, bbox)

        self._update_status(
            is_live=bool(live_result["is_live"]),
            liveness_score=float(live_result["live"]),
        )

        if not live_result["is_live"]:
            return

        embedding = embedder.embed(frame, face)
        if embedding is None:
            return

        if self._stop_event.is_set():
            return

        timestamp = datetime.now(timezone.utc).isoformat()
        self._last_sent = time.monotonic()

        result = recognize(face, embedding, timestamp)

        if result is None:
            self._update_status(
                last_response=None,
                last_error="Backend gav inget användbart svar",
            )
            return

        # Förväntar sig ett JSON-objekt med approved: true/false.
        if (
            not isinstance(result, dict)
            or not isinstance(result.get("approved"), bool)
        ):
            self._update_status(
                last_response=None,
                last_error="Backendens svar saknar approved som boolean",
            )
            return

        self._update_status(
            last_response=result,
            last_error=None,
        )
        self._last_decision = time.monotonic()

        # Ett svar som kommer under avstängning ska inte öppna låset.
        if self._stop_event.is_set():
            return

        if result["approved"]:
            print("Godkänd:", result.get("name"))
            lock.unlock()
        else:
            print("Tillträde nekat")
            lock.deny()