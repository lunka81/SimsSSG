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
from sqlalchemy import text

from demo.db.database import Base, engine
import demo.models.employee_test      # models must be imported so Base knows about them
import demo.models.employee_test_log

@asynccontextmanager
async def lifespan(app: FastAPI):
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(engine)
    yield

load_dotenv()
app = FastAPI(lifespan=lifespan, debug=os.getenv("DEBUG", "False").lower() == "true")
#app = FastAPI(lifespan=lifespan, debug=os.getenv("DEBUG", "False").lower() == "true")
app.include_router(camera_router)
app.include_router(employee_router)
app.include_router(recognition_router)

'''
React runs on port 5173 and FastAPI on a different port.
The browser therefore treats them as different origins and requires
the backend to explicitly allow requests from the React address.
'''
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


