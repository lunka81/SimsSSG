from contextlib import asynccontextmanager

from fastapi import FastAPI

from routes.camera_routes import camera_router
from services.recognition_service import RecognitionService


@asynccontextmanager
async def lifespan(app: FastAPI):
    service = RecognitionService()
    app.state.recognition_service = service
    service.start()

    try:
        yield
    finally:
        service.stop()


app = FastAPI(lifespan=lifespan)
app.include_router(camera_router)