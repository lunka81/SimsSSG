import base64
from io import BytesIO
from PIL import Image
import cv2
import numpy as np
from deepface import DeepFace



def decode_image_to_bgr(image_data_url: str) -> tuple[bytes, np.ndarray]:
    """Decodes a data URL and returns image bytes and a BGR array.

    The image bytes are used when the original image is to be stored in the database.
    The BGR array is used as input to DeepFace.
    """
    # The data URL consists of a header and Base64-encoded image data.
    # split(",", 1) only splits at the first comma.
    _, b64data = image_data_url.split(",", 1)

    # The Base64 text is converted back into the original JPEG bytes.
    img_bytes = base64.b64decode(b64data)

    # PIL opens the bytes as an image. RGB ensures three color channels.
    pil_img = Image.open(BytesIO(img_bytes)).convert("RGB")

    # NumPy gives an array of the image's pixels.
    rgb = np.array(pil_img)

    # DeepFace expects a NumPy image in BGR order.
    # The same conversion is used for both registration and search.
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

    return img_bytes, bgr


def image_media_type(img_bytes: bytes) -> str:
    """Determines whether stored image bytes are PNG or JPEG (the formats the frontend allows)."""
    if img_bytes.startswith(b"\x89PNG"):
        return "image/png"
    return "image/jpeg"


def get_embedding(bgr: np.ndarray) -> list[float]:
    """Computes the face embedding with DeepFace.

    Facenet gives 128 values, which matches the column VECTOR(128).
    Raises ValueError if no face is found in the image.
    """
    result = DeepFace.represent(img_path=bgr, model_name="Facenet", enforce_detection=True)
    return result[0]["embedding"]
