import base64
from io import BytesIO
from PIL import Image
import cv2
import numpy as np



def decode_image_to_bgr(image_data_url: str) -> tuple[bytes, np.ndarray]:
    """Avkodar en data-URL och ger tillbaka bildbytes och en BGR-array.

    Bildbytes används när originalbilden ska sparas i databasen.
    BGR-arrayen används som indata till DeepFace.
    """
    # Data-URL:en består av en header och Base64-kodade bilddata.
    # split(",", 1) delar bara vid det första kommatecknet.
    _, b64data = image_data_url.split(",", 1)

    # Base64-texten görs om till de ursprungliga JPEG-bytesen.
    img_bytes = base64.b64decode(b64data)

    # PIL öppnar bytesen som en bild. RGB säkerställer tre färgkanaler.
    pil_img = Image.open(BytesIO(img_bytes)).convert("RGB")

    # NumPy ger en array av bildens pixlar.
    rgb = np.array(pil_img)

    # DeepFace förväntar sig en NumPy-bild i BGR-ordning.
    # Samma konvertering används vid både registrering och sökning.
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

    return img_bytes, bgr