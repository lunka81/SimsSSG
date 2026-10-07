import os
import secrets
from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Header, HTTPException
from demo.routes.camera_routes import camera_router
from demo.routes.employee_routes import employee_router
from demo.routes.recognition_routes import recognition_router
from contextlib import asynccontextmanager

from demo.db.database import Base, engine
from demo.models.employee_test import EmployeeTest
from demo.models.employee_test_log import EmployeeTestLog


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield
load_dotenv()
app = FastAPI(
    debug=os.getenv("DEBUG", "False").lower() == "true",
    lifespan=lifespan,
)
app.include_router(camera_router)
app.include_router(employee_router)

app.include_router(recognition_router)
# React kör på port 5173 och FastAPI på en annan port.
# Webbläsaren betraktar dem därför som olika origins och kräver
# att backend uttryckligen tillåter anrop från React-adressen.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/device/ping")
def device_ping(
    x_api_key: str | None = Header(default=None)
):
    expected_key = os.environ["DEVICE_API_KEY"]

    if x_api_key is None or not secrets.compare_digest(
        x_api_key, expected_key
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

    return {"message": "Kontakt med backend fungerar"}