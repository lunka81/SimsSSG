

import cv2


def generate_camera_frames(cap):
    try:
        while True:
            ok, frame = cap.read()

            if not ok:
                break

            # Turns the frame into JPEG bytes
            ok, encoded = cv2.imencode(".jpg", frame)

            if not ok:
                continue

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n"
                + encoded.tobytes()
                + b"\r\n"
            )
    finally:
        cap.release()




