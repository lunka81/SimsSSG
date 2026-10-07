"""Send face embeddings to the recognition server and return its answer."""

import requests
from config.config import DEVICE_API_KEY
from config.config import DEVICE_ID, SERVER_TIMEOUT, SERVER_URL


def recognize(face, embedding, timestamp):
    """Ask the server who the face belongs to.

    face is the YuNet row from FaceDetector, embedding the vector from FaceEmbedder.
    Returns the server's answer as a dict (with "recognized", and "name" and "similarity"
    when it is recognized), or None if the server could not be reached or answered with an error.
    """
    payload = {
        "camera_id": DEVICE_ID,
        "timestamp": timestamp,
        "detection_confidence": float(face[-1]),
        "face_width": int(face[2]),
        "face_height": int(face[3]),
        "embedding": [float(v) for v in embedding],
    }
    try:
        response = requests.post(
            SERVER_URL,
            json=payload,
            headers={"X-API-Key": DEVICE_API_KEY},
            timeout=SERVER_TIMEOUT,
        )
    except requests.RequestException as e:
        print("Couldn't contact server:", e)
        return None
    if response.status_code != 200:
        print(f"Server answered with status {response.status_code}")
        return None
    return response.json()

