import cv2

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from demo.camera.camera import generate_camera_frames

camera_router = APIRouter(
    prefix="/camera",
    tags=["Camera"]
)


@camera_router.get("/stream")
def stream_camera():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        cap.release()
        raise HTTPException(
            status_code=503,
            detail="Could not open the camera"
        )

    return StreamingResponse(
        generate_camera_frames(cap),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )