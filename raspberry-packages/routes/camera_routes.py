from fastapi import APIRouter, Request
import asyncio

import cv2
from fastapi.responses import StreamingResponse

camera_router = APIRouter(
    prefix="/camera",
    tags=["Camera"],
)


@camera_router.get("/status")
def camera_status(request: Request):
    service = request.app.state.recognition_service
    return service.get_status()


@camera_router.get("/stream")
async def camera_stream(request: Request):
    service = request.app.state.recognition_service

    async def generate_frames():
        while not await request.is_disconnected():
            if not service.get_status()["running"]:
                break

            frame = service.get_latest_frame()

            if frame is not None:
                ok, encoded = cv2.imencode(".jpg", frame)

                if ok:
                    yield (
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n\r\n"
                        + encoded.tobytes()
                        + b"\r\n"
                    )

            await asyncio.sleep(0.1)

    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers={"Cache-Control": "no-store"},
    )